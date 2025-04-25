import os
from random import shuffle
import sys
import time
from helpers import *


if len(sys.argv) == 1:
    prog_exit("Drop a file (library.json) or a music folder.")


input_dir = sys.argv[1]
input_type = "dir" if os.path.isdir(input_dir) else "file"


library = []
if input_type == "file":
    if not input_dir.endswith(".json"):
        prog_exit("Invalid file type. Only JSON files are supported.")
    if not os.path.exists(input_dir):
        prog_exit("File does not exist.")
    library = load_json(input_dir)
else:
    if not os.path.exists(input_dir):
        prog_exit("Directory does not exist.")
    input_dir_parent = os.path.dirname(input_dir)
    input_dir_name = os.path.basename(input_dir)
    print("Scanning the '%s' directory for mp3 files ..." % input_dir_name)
    input_files = get_mp3_files(input_dir)
    library = get_mp3_durations(input_files)
    save_json(library, os.path.join(input_dir_parent, input_dir_name + "-library.json"))
print("Found %d songs." % len(library))


vlc_playlist = []
if is_vlc_running():
    vlc_playlist = get_vlc_playlist()
print("Found %d songs in VLC playlist." % len(vlc_playlist))


listened_files = []
unlistened_files = []
for entry in library:
    path = entry["path"]
    if path not in vlc_playlist:
        unlistened_files.append(entry)
    else:
        listened_files.append(entry)


shuffle(unlistened_files)


target_duration = get_input_integer("Enter duration in minutes: ", True, 1, 100)
target_duration *= 60
current_duration = 0
playlist = []
for song in unlistened_files:
    playlist.append(song["path"])
    current_duration += song["duration"]
    if current_duration >= target_duration:
        break
print("Picked %d songs." % len(playlist))


play_vlc_playlist(playlist)


time.sleep(5)
