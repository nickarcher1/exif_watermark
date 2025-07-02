"""
file/folder dependencies:
    - Roboto-Regular.tff
    - folder path supplied as cmd argument
pip dependencies:
    - pillow
    - geopy
    - piexif
"""
from PIL import Image, ExifTags, ImageDraw, ImageFont, ImageOps
from geopy.geocoders import Nominatim
import piexif
import sys
import os

class time:
    def __init__(self, timestamp: str):
        self.year:   str = timestamp[0:4]
        self.month:  str = timestamp[5:7]
        self.day:    str = timestamp[8:10]
        self.hour:   str = timestamp[11:13]
        self.minute: str = timestamp[14:16]
    
    def add_lead_zero(self, h: int) -> str:
        if len(str(h)) == 1:
            return f"0{h}"
        return str(h)

    def murican_time(self) -> tuple[str, str]:
        h: int = int(self.hour)
        am_pm: str = "AM"
        if h>12:
            h-=12
            am_pm = "PM"
        elif h == 0:
            h=12
        return self.add_lead_zero(h), am_pm
    
    def get24hourTimestamp(self) -> str:
        return f"{self.hour}:{self.minute} {self.day}/{self.month}/{self.year}"

    def getMuricanTimestamp(self) -> str:
        adjusted_hour, am_pm = self.murican_time()
        return f"{adjusted_hour}:{self.minute} {am_pm}  {self.day}/{self.month}/{self.year}"

    def __str__(self) -> str:
        return self.getMuricanTimestamp()

class location:
    def __init__(self, loc_data: dict[int, tuple]):
        self.lat: float
        self.lon: float
        self.lat, self.lon = self.dms_to_dec(loc_data)
        geolocator = Nominatim(user_agent="my_geopy_app")   # I want to make this global or something
        self.location = geolocator.reverse(f"{self.lat},{self.lon}").raw['address']

    def dms_to_dec(self, loc_data: dict[int, tuple]) -> tuple[float, float]:
        dir1:    str = loc_data[1]
        dir1deg: str = loc_data[2][0]
        dir1min: str = loc_data[2][1]
        dir1sec: str = loc_data[2][2]
        dir2:    str = loc_data[3]
        dir2deg: str = loc_data[4][0]
        dir2min: str = loc_data[4][1]
        dir2sec: str = loc_data[4][2]
        
        lat = float(dir1deg) + float(dir1min)/60 + float(dir1sec)/3600
        if dir1 in ('S', 'W'):
            lat *= -1
        lon = float(dir2deg) + float(dir2min)/60 + float(dir2sec)/3600
        if dir2 in ('S', 'W'):
            lon *= -1

        return lat, lon

    def getCityState(self) -> str:
        if 'city' in self.location.keys():
            city = self.location['city']
        elif 'municipality' in self.location.keys():
            city = self.location['municipality']
        elif 'village' in self.location.keys():
            city = self.location['village']
        elif 'county' in self.location.keys():
            city = self.location['county']
        elif 'town' in self.location.keys():
            city = self.location['town']
        else:
            city = ''

        if 'state' in self.location.keys():
            state = self.location['state']
        elif 'province'  in self.location.keys():
            state = self.location['province']
        elif 'region'  in self.location.keys():
            state = self.location['region']
        else:
            state = ''

        citystate = city
        if citystate == '':
            citystate = state
        else:
            citystate += f", {state}"

        return citystate
    
    def getCountry(self) -> str:
        country = self.location['country']
        if country == 'Schweiz/Suisse/Svizzera/Svizra':
            country = 'Schweiz'
        return country
    
    def __str__(self) -> str:
        return f"{self.getCityState()}\n{self.getCountry()}"
        
def getImageData(img: Image.Image, origin: str) -> dict:
    exif = {
        ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in ExifTags.TAGS
    }
    out: dict = {}
    out['turn'] = False
    if 'Orientation' in exif.keys():
        if exif['Orientation'] == 6:
            out['turn'] = True
    if 'DateTime' in exif.keys():
        out['timestamp'] = time(exif['DateTime'])
    if 'GPSInfo' in exif.keys():
        if len(exif['GPSInfo'].keys()) > 1:
            out['location'] = location(exif['GPSInfo'])
    return out

def addStampsToPhoto(img: Image.Image, dat: dict) -> tuple[bool, bool]:
    watermark = ''
    if 'timestamp' in dat.keys():
        t = True
        watermark = str(dat['timestamp'])
    else:
        t = False
    if 'location' in dat.keys():
        l = True
        if watermark != '':
            watermark += '\n'
        watermark += str(dat['location'])
    else:
        l = False
    rotate = dat['turn']

    if watermark == '':
        return False, False

    draw = ImageDraw.Draw(img)
    if rotate:
        ImageOps.exif_transpose(img)
    font = ImageFont.truetype("Roboto-Regular.ttf", 0.025*img.size[1])

    text_width, text_height = draw.textbbox((0.02*img.size[0], 0.02*img.size[1]), watermark, font=font)[2:] # Using textbbox to get accurate dimensions
    # Calculate the position for the bottom right corner
    image_width, image_height = img.size
    margin = 10  # Adjust the margin as needed
    x_position = image_width - text_width - margin
    y_position = image_height - text_height - margin

    draw.text((x_position, y_position), watermark, fill=(255, 255, 255), font=font) # White color for the timestamp
    return t, l

def stamp_jpg(path: str, out_folder_path: str) -> bool:
    newpath = f"{out_folder_path}{os.sep}{os.path.basename(path)}"

    init_img = Image.open(path)
    exif_bytes = init_img.info.get('exif')                                  # Pull exif data

    if len(init_img.getexif()) == 0:                                        # Don't do anything if inputed photo has no metadata
        return False, False
    
    img = ImageOps.exif_transpose(init_img)                                 # Will transpose if needed

    dat = getImageData(init_img, path)                                            # pulls exif time, location, and rotation data
    if 'timestamp' not in dat.keys() and 'location' not in dat.keys():      # Don't do anything if inputed photo has no time or location metadata
        return False, False
    hastime, hasloc = addStampsToPhoto(img, dat)
    if not hastime and not hasloc:   # Run stamping script
        return False, False

    exif_dict = piexif.load(exif_bytes)                                     # Load exif data
    if piexif.ImageIFD.Orientation in exif_dict["0th"]:
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1                   # Change orientation to be known as 'stored correctly'
    exif_bytes = piexif.dump(exif_dict)                                     # Reload edited exif data

    img.save(newpath, exif=exif_bytes)                                      # Save file, with edited exif data
    return hastime, hasloc

def manual_mode(files: list[str], missing_time: list[str], missing_loc: list[str]):
    if len(files) != 0:
        print("\nThe following files could not be stamped: ")
        for path in files:
            print(path)
    if len(missing_time) != 0:
        print("\nThe following files are missing their time, but a photo with stamped location has been created: ")
        for path in missing_time:
            print(path)
    if len(missing_loc) != 0:
        print("\nThe following files are missing their location, but a photo with stamped time has been created: ")
        for path in missing_loc:
            print(path)
    

    

def stamp_all_photos_in_folder(folder_path: str):
    non_stamped_files = []
    missing_time = []
    missing_loc = []
    out_folder = f"{folder_path}{os.sep}WATERMARKED"
    file_paths = []
    for file in os.listdir(folder_path):
        filepath = os.path.join(folder_path, file)
        if os.path.isfile(filepath):
            file_paths.append(filepath)
    if not os.path.isdir(out_folder):
        try:
            os.makedirs(out_folder, exist_ok = True)
        except OSError as e:
            print(f"Error creating folder '{out_folder}': {e}")
            sys.exit(1)
    num_completed = 0
    num_review = 0
    total = len(file_paths)
    for file in file_paths:
        hastime, hasloc = stamp_jpg(file, out_folder)
        if hastime and hasloc:
            num_completed += 1
        elif not hastime and not hasloc:
            non_stamped_files.append(file)
            num_review += 1
        else:
            if not hastime:
                missing_time.append(file)
                num_review += 1
            if not hasloc:
                missing_loc.append(file)
                num_review += 1
        print(f"\rCompleted: {num_completed} of {total}. Num to review: {num_review} of {total}. Total processed: {num_completed + num_review} of {total}.", end="")
    manual_mode(non_stamped_files, missing_time, missing_loc)

def main():
    if len(sys.argv) != 2:
        print("ERROR: too many or too few cmd arguments.")
        return
    stamp_all_photos_in_folder(sys.argv[1])

if __name__ == "__main__":
    main()
