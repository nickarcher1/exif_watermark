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
        try:
            city = self.location['city']
        except:
            city = self.location['municipality']
        return f"{city}, {self.location['state']}"
    
    def getCountry(self) -> str:
        return self.location['country']
    
    def __str__(self) -> str:
        return f"{self.getCityState()}\n{self.getCountry()}"
        
# def getImageData(img: Image.Image) -> dict[str, bool|time|location]:
def getImageData(img: Image.Image) -> dict:
    exif = {
        ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in ExifTags.TAGS
    }
    # out: dict[str, bool|time|location] = {}
    out: dict = {}
    if exif['Orientation'] == 6:
        out['turn'] = True
    else:
        out['turn'] = False
    out['timestamp'] = time(exif['DateTime'])
    out['location'] = location(exif['GPSInfo'])
    return out

def addStampsToPhoto(img: Image.Image, t: time, l: location, rotate: bool):
    watermark = f"{t}\n{l}"
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

def stamp_jpg(path: str, out_folder_path: str) -> bool:
    newpath = f"{out_folder_path}{os.sep}{os.path.basename(path)}"

    init_img = Image.open(path)
    exif_bytes = init_img.info.get('exif')

    if len(init_img.getexif()) == 0:
        init_img.save(newpath) # , exif = exif_bytes
        return False
    
    img = ImageOps.exif_transpose(init_img)
    dat = getImageData(init_img)
    addStampsToPhoto(img, dat['timestamp'], dat['location'], dat['turn'])

    exif_dict = piexif.load(exif_bytes)
    if piexif.ImageIFD.Orientation in exif_dict["0th"]:
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
    exif_bytes = piexif.dump(exif_dict)

    img.save(newpath, exif=exif_bytes) # , exif = exif_bytes
    return True

def stamp_all_photos_in_folder(folder_path: str):
    out_folder = f"{folder_path}{os.sep}WATERMARKED"
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    if not os.path.isdir(out_folder):
        try:
            os.makedirs(out_folder, exist_ok = True)
        except OSError as e:
            print(f"Error creating folder '{out_folder}': {e}")
            sys.exit(1)
    for file in file_paths:
        if 'WATERMARKED' in file:
            continue
        if stamp_jpg(file, out_folder):
            print(f"SUCCESSFUL: {file}")
        else:
            print(f"  FAILED  : {file}")

def main():
    if len(sys.argv) != 2:
        print("ERROR: too many or too few cmd arguments.")
        return
    stamp_all_photos_in_folder(sys.argv[1])

if __name__ == "__main__":
    main()
