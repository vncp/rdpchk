from check import *

# PUT ALL PATHS HERE
icon_dir = "icons"
desktop_dir = "src/source_connection.png"

icon_check = check_icon(desktop_dir, icon_dir, debug=.11)
for i in icon_check:
    if i[0] == 0:
        print(f"i-1: {i[1]}: was not found on desktop!")
    else:
        print(f"i-0: {i[1]}: was found with {i[0]} unique features.")

