from collections import ChainMap
from math import floor
from types import MappingProxyType
from typing import ClassVar

from .wacca_data import SONG_DATA


class WaccaCollections:
    """wip"""

    STARTING_CODE = 1

    PROGRESSION_NAME: str = "Wedge"
    PROGRESSION_CODE: int = STARTING_CODE

    VERSIONS = MappingProxyType({"WACCA": 1, "Lily": 2, "Reverse": 3, "Plus": 4})

    song_items = SONG_DATA
    song_locations: ClassVar[dict[str, int]] = {}

    item_names_to_id: ChainMap = ChainMap({k: v.code for k, v in SONG_DATA.items()})
    location_names_to_id: ChainMap = ChainMap(song_locations)

    def __init__(self) -> None:
        self.item_names_to_id[self.PROGRESSION_NAME] = self.PROGRESSION_CODE

        location_id_index = self.STARTING_CODE
        for name in self.song_items.keys():
            self.song_locations[f"{name}-0"] = location_id_index
            self.song_locations[f"{name}-1"] = location_id_index + 1
            location_id_index += 2

    def get_songs_with_settings(
        self, versions: set[str], diff_min: int, diff_max: float, max_includes_plus: bool
    ) -> list[str]:
        """Gets a list of all songs that match the filter settings. Difficulty thresholds are inclusive."""

        # get the int version of the version strings
        numeric_versions = [self.VERSIONS[k] for k in versions]

        def compare_versions(song_version: int) -> bool:
            normalized_song_version = floor(song_version / 100)
            return normalized_song_version in numeric_versions

        filtered_list = []

        diff_max = diff_max + 1 if max_includes_plus else diff_max + 0.7

        for song_key, song_data in self.song_items.items():
            if not compare_versions(song_data.version):
                continue

            if diff_min <= song_data.normal < diff_max:
                filtered_list.append(song_key)
                continue

            if diff_min <= song_data.hard < diff_max:
                filtered_list.append(song_key)
                continue

            if diff_min <= song_data.expert < diff_max:
                filtered_list.append(song_key)
                continue

            if song_data.inferno is not None and diff_min <= song_data.inferno < diff_max:
                filtered_list.append(song_key)
                continue

        return filtered_list
