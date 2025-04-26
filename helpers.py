import json
import math
from pathlib import Path
import subprocess
import sys
import ffmpeg
import requests
from urllib.parse import quote, unquote


#region ==================== VLC

def is_vlc_running():
    """Checks if the VLC process is running."""
    try:
        output = subprocess.check_output("tasklist", shell=True, text=True)
        if "vlc.exe" in output:
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error checking VLC process: {e}")
    return False


def get_vlc_playlist():
    """Returns a list of song paths from the VLC playlist."""
    playlist = []
    response = get_vlc_playlist_response()
    if response is not None:
        for item in response["children"]:
            if item["name"] == "Playlist":
                for child in item["children"]:
                    path = child["uri"]
                    path = unquote(path)
                    path = path.replace('file:///', '')
                    path = path.replace('/', '\\')
                    playlist.append(path)
    return playlist


def get_vlc_playlist_response():
    """Makes a request to the VLC HTTP interface to get the current playlist."""
    response = None
    try:
        response = requests.get("http://localhost:8080/requests/playlist.json", auth=("", "1234"), timeout=1)
        if response.status_code != 200:
            raise Exception("Status code is not 200.")
        response = json.loads(response.text)
    except Exception as e:
        print(f"Error fetching VLC playlist: {e}")
    return response


def play_vlc_playlist(playlist):
    """Plays a list of songs in VLC."""
    # https://wiki.videolan.org/VLC_command-line_help/
    exe_path = "C:/Program Files/VideoLAN/VLC/vlc.exe"
    args = [
        "--one-instance",
        "--playlist-enqueue",
    ]
    # expects playlist items to be in backslashes
    cmd_args = [exe_path] + args + playlist
    subprocess.Popen(
        cmd_args,
        stdin=None,
        stdout=None,
        stderr=None,
    )

#endregion


#region ==================== MP3

def get_mp3_files(input_dir):
    """Recursively get all mp3 files (paths) from the input directory."""
    files = []
    for path in Path(input_dir).rglob("*.mp3"):
        path = str(path)
        files.append(path)
    return files


def get_mp3_duration(mp3_path):
    """Returns the duration in seconds."""
    duration = 0
    try:
        probe = ffmpeg.probe(mp3_path)
        duration = float(probe['format']['duration'])
    except Exception as e:
        print(f"Error getting duration for {mp3_path}: {e}")
    return duration


def get_mp3_durations(mp3_files):
    """Returns a list of dictionaries with mp3 file paths and their durations."""
    library = []
    for mp3_file in mp3_files:
        duration = get_mp3_duration(mp3_file)
        entry = {
            "path": mp3_file,
            "duration": duration,
        }
        library.append(entry)
    return library

#endregion


#region ==================== JSON

def save_json(data, filename):
    """Saves data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_json(filename):
    """Loads data from a JSON file."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

#endregion


#region ==================== PROG

def prog_exit(*messages):
    """Exits the program with optional messages."""
    for message in messages:
        print(message)
        if message != "":
            print("")
    print("Program is done.")
    input("")
    sys.exit()

#endregion


#region ==================== INPUT

def get_input_integer(msg, be_persistent=True, min=None, max=None):
    value = input(msg)
    try:
        value = int(value)
    except ValueError:
        if be_persistent:
            print("Invalid value.")
            value = get_input_integer(msg, be_persistent, min, max)
        else:
            raise ValueError("Invalid value '%s' for '%s'" % (value, msg))
    if min is not None and value < min:
        if be_persistent:
            print("Number underflow.")
            value = get_input_integer(msg, be_persistent, min, max)
        else:
            raise ValueError("Number underflow.")
    if max is not None and value > max:
        if be_persistent:
            print("Number overflow.")
            value = get_input_integer(msg, be_persistent, min, max)
        else:
            raise ValueError("Number overflow.")
    return value

#endregion


#region ==================== DURATION

def duration_str(duration_in_sec):
    """Converts a duration in seconds to a formatted string."""
    dur_s = 1
    dur_m = dur_s * 60
    dur_h = dur_m * 60
    dur_format = "%dh %dm %ds"
    duration_str = dur_format % (
        math.floor(duration_in_sec / dur_h),
        math.floor((duration_in_sec % dur_h) / dur_m),
        duration_in_sec % dur_m,
    )
    return duration_str

#endregion

