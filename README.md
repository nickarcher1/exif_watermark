
1. Put your images you want to watermark in a folder **<pic_folder_name>**.
2. Open terminal
3. Install python:
	- Type the following command: `python3 --version`
	- Click **Install** on the "developer tools" pop up window
	- Click **Agree**
4. Past and run each of the following commands individually: `pip3 install pillow`, `pip3 install geopy`, `pip3 install exif`.
5. Run `cd Downloads`
6. Run `git clone https://github.com/nickarcher1/exif_watermark.git`
7. Run `cd exif_watermark`
8. Run `open .`
9. Put **<pic_folder_name>** in the folder that popped up
10. Run `python3 exif_watermark.py <pic_folder_name>`
