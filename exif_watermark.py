"""
pip dependencies:
    - pillow
    - geopy
    - piexif
file/folder dependencies:
    - dependencies/stamping_functions
    - dependencies/metadata_classes
    - dependencies/manualediting_functions
    - folder path supplied as cmd argument
"""
import sys
from dependencies.stamping_functions import stamp_all_photos_in_folder
from dependencies.manualediting_functions import manual_mode, print_completion_summary, getYesNo

def main():
    if len(sys.argv) != 2:
        print("ERROR: too many or too few cmd arguments.")
        return
    
    non_stamped_files, missing_time, missing_loc = stamp_all_photos_in_folder(sys.argv[1])

    print_completion_summary(non_stamped_files, missing_time, missing_loc)

    resolve = getYesNo("Would you like to resolve the missing stamps?")
    if resolve:
        manual_mode(non_stamped_files, missing_time, missing_loc)

if __name__ == "__main__":
    main()
