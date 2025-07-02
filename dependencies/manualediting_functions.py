from dependencies.stamping_functions import get_image_data, add_stamps_to_photos
from PIL import Image, ImageOps, ImageTk
import piexif
import os
import tkinter as tk

def print_completion_summary(files: list[str], missing_time: list[str], missing_loc: list[str]):
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

def getYesNo(question_text: str) -> bool:
    answer = 'q'
    while(answer not in ['y', 'n', 'yes', 'no']):
        answer = input(f"\n{question_text} (y/n) ").lower()
    if answer in ['y', 'yes']:
        return True
    return False

def imgWindow(img: Image.Image):
    # root = tk.Tk()
    # root.withdraw()
    # popup = tk.Toplevel(root)
    # popup.title("image path placeholder")
    # popup.geometry("600x350")
    # popup.attributes('-topmost', True)
    # tkimg = ImageTk.PhotoImage(img)
    # label = tk.Label(popup, image = tkimg)
    # label.image = tkimg
    # label.pack()
    img.show()

def variableStamp(path: str, needLoc: bool, needTime: bool, out_folder_name: str):
    init_img = Image.open(path)
    exif_bytes = init_img.info.get('exif')                                  # Pull exif data
    
    img = ImageOps.exif_transpose(init_img)                                 # Will transpose if needed
    imgWindow(img)
    if not (needLoc and needTime):
        dat = get_image_data(init_img, path)                                # pulls exif time, location, and rotation data
    else:
        dat = {}
        dat['turn'] = False

    if needLoc:
        dat['location'] = input(f"{path}: What city/state/country would you like to show on this image? ")
    if needTime:
        dat['timestamp'] = input(f"{path}: What date and time would you like to show on this image? (use 00:00 XM DD/MM/YYYY) ")

    add_stamps_to_photos(img, dat)

    if not (needLoc and needTime):
        exif_dict = piexif.load(exif_bytes)                                     # Load exif data
        if piexif.ImageIFD.Orientation in exif_dict["0th"]:
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1                   # Change orientation to be known as 'stored correctly'
        exif_bytes = piexif.dump(exif_dict)                                     # Reload edited exif data

        img.save(f"{os.path.dirname(path)}{os.sep}{out_folder_name}{os.sep}{os.path.basename(path)}", exif=exif_bytes) # Save file, with edited exif data
    else:
        img.save(f"{os.path.dirname(path)}{os.sep}{out_folder_name}{os.sep}{os.path.basename(path)}")

def manual_mode(no_metadata: list[str], missing_time: list[str], missing_loc: list[str], out_folder_name: str):
    for path in no_metadata:
        variableStamp(path, True, True, out_folder_name)
    for path in missing_time:
        variableStamp(path, False, True, out_folder_name)
    for path in missing_loc:
        variableStamp(path, True, False, out_folder_name)