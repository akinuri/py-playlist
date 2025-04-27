import os
from random import shuffle
import sys
import time
from helpers import *


if len(sys.argv) == 1:
    prog_exit("Drop a file (*-music.json) or a music folder.")


input_value = sys.argv[1]
input_type = "dir" if os.path.isdir(input_value) else "file"


library = []
if input_type == "file":
    input_file = input_value
    if not input_file.endswith(".json"):
        prog_exit("Invalid file type. Only JSON files are supported.")
    if not os.path.exists(input_file):
        prog_exit("File does not exist.")
    input_file_name = os.path.basename(input_file)
    print("Loading the '%s' file for mp3 files ..." % input_file_name)
    library = load_json(input_file)
    print("Found %d songs." % len(library))
    print("Total duration: %s" % library["total_duration_str"])
else:
    input_dir = input_value
    if not os.path.exists(input_dir):
        prog_exit("Directory does not exist.")
    input_dir_parent = os.path.dirname(input_dir)
    input_dir_name = os.path.basename(input_dir)
    print("Scanning the '%s' directory for mp3 files ..." % input_dir_name)
    input_files = get_mp3_files(input_dir)
    print("Found %d songs." % len(input_files))
    print("Getting durations ...")
    library = build_music_library(input_files)
    print("Total duration: %s" % library["total_duration_str"])
    save_json(library, os.path.join(input_dir_parent, input_dir_name + "-music.json"))


vlc_playlist = []
if is_vlc_running():
    vlc_playlist = get_vlc_playlist()
print("Found %d songs in VLC playlist." % len(vlc_playlist))


listened_files = []
unlistened_files = []
for item in library["items"]:
    path = item["path"]
    if path not in vlc_playlist:
        unlistened_files.append(item)
    else:
        listened_files.append(item)


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


time.sleep(1)


if get_vlc_state() == "stopped":
    item_id, item_name = play_vlc_playlist_item(playlist[0])
    print("Playing #%d: %s" % (int(item_id), item_name))


time.sleep(5)
