from collections import ChainMap
from math import floor
from typing import List, Dict

from .WaccaData import SONG_DATA


class WaccaCollections:
    """wip"""
    STARTING_CODE = 1

    PROGRESSION_NAME: str = "Wedge"
    PROGRESSION_CODE: int = STARTING_CODE

    VERSIONS: Dict[str, int] = {
        "WACCA": 1,
        "Lily": 2,
        "Reverse": 3,
        "Plus": 4
    }

    song_items = SONG_DATA
    song_locations: Dict[str, int] = {}

    item_names_to_id: ChainMap = ChainMap({k: v.code for k, v in SONG_DATA.items()})
    location_names_to_id: ChainMap = ChainMap(song_locations)

    def __init__(self) -> None:
        self.item_names_to_id[self.PROGRESSION_NAME] = self.PROGRESSION_CODE

        location_id_index = self.STARTING_CODE
        for name in self.song_items.keys():
            self.song_locations[f"{name}-0"] = location_id_index
            self.song_locations[f"{name}-1"] = location_id_index + 1
            location_id_index += 2

    def get_songs_with_settings(self, versions: set[str], diff_min: int, diff_max: int, max_includes_plus: bool) -> \
            List[str]:
        """Gets a list of all songs that match the filter settings. Difficulty thresholds are inclusive."""

        # get the int version of the version strings
        numeric_versions = [self.VERSIONS[k] for k in versions]

        def compare_versions(song_version: int) -> bool:
            normalized_song_version = floor(song_version / 100)
            return normalized_song_version in numeric_versions

        filtered_list = []

        diff_max = diff_max + 1 if max_includes_plus else diff_max + 0.7

        for songKey, songData in self.song_items.items():
            if not compare_versions(songData.version):
                continue

            if diff_min <= songData.normal < diff_max:
                filtered_list.append(songKey)
                continue

            if diff_min <= songData.hard < diff_max:
                filtered_list.append(songKey)
                continue

            if diff_min <= songData.expert < diff_max:
                filtered_list.append(songKey)
                continue

            if songData.inferno is not None and diff_min <= songData.inferno < diff_max:
                filtered_list.append(songKey)
                continue

        return filtered_list
