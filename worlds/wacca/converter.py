import json
import os
import re


def convert():
    js_path = os.path.join(os.path.dirname(__file__), "waccaSongsPlus.js")
    py_path = os.path.join(os.path.dirname(__file__), "WaccaData.py")

    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract the array from the JS file
    # Searches for 'const waccaSongs = [...];'
    match = re.search(r"const waccaSongs = (\[.*\]);", content, re.DOTALL)
    if not match:
        print("Could not find waccaSongs array in JS file.")
        return

    # JS objects are very similar to JSON, but we might need to handle trailing commas
    # or unquoted keys if the source wasn't strict JSON.
    # For this specific file, it's structured enough for a basic cleanup.
    json_data = match.group(1)
    # Remove trailing commas before closing brackets/braces
    json_data = re.sub(r",(\s*[\]}])", r"\1", json_data)

    songs = json.loads(json_data)

    output = [
        "from .Items import SongData",
        "from typing import Dict",
        "",
        "SONG_DATA: Dict[str, SongData] = {"
    ]

    for song in songs:
        title = song.get("titleEnglish") or song.get("title")
        song_id = song["id"]
        version = song["gameVersion"]

        # Extract difficulties from sheets (Normal, Hard, Expert, Inferno)
        sheets = song.get("sheets", [])
        diffs = [None, None, None, None]
        for i in range(min(len(sheets), 4)):
            diffs[i] = sheets[i]["difficulty"]

        # Format line: "Key": SongData(code, ID, version, normal, hard, expert, inferno)
        line = f'    "{title}": SongData({song_id}, {song_id}, {version}, {diffs[0]}, {diffs[1]}, {diffs[2]}, {diffs[3]}),'
        output.append(line)

    output.append("}")

    with open(py_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output) + "\n")

    print(f"Successfully converted {len(songs)} songs to {py_path}")


if __name__ == "__main__":
    convert()
