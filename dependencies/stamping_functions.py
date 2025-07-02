from PIL import Image, ExifTags, ImageDraw, ImageFont, ImageOps
import piexif
import sys
import os
from dependencies.metadata_classes import time, location
       
def get_image_data(img: Image.Image, origin: str) -> dict:
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

def add_stamps_to_photos(img: Image.Image, dat: dict) -> tuple[bool, bool]:
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
    font = ImageFont.truetype(f"dependencies{os.sep}Roboto-Regular.ttf", 0.025*img.size[1])

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

    dat = get_image_data(init_img, path)                                            # pulls exif time, location, and rotation data
    if 'timestamp' not in dat.keys() and 'location' not in dat.keys():      # Don't do anything if inputed photo has no time or location metadata
        return False, False
    hastime, hasloc = add_stamps_to_photos(img, dat)
    if not hastime and not hasloc:   # Run stamping script
        return False, False

    exif_dict = piexif.load(exif_bytes)                                     # Load exif data
    if piexif.ImageIFD.Orientation in exif_dict["0th"]:
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1                   # Change orientation to be known as 'stored correctly'
    exif_bytes = piexif.dump(exif_dict)                                     # Reload edited exif data

    img.save(newpath, exif=exif_bytes)                                      # Save file, with edited exif data
    return hastime, hasloc

def stamp_all_photos_in_folder(folder_path: str, out_folder_name: str):
    non_stamped_files = []
    missing_time = []
    missing_loc = []
    out_folder = f"{folder_path}{os.sep}{out_folder_name}"
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
    print()
    return non_stamped_files, missing_time, missing_loc