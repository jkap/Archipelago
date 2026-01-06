from math import floor
from typing import List, ClassVar, Type

from BaseClasses import Item, ItemClassification, Region
from Options import PerGameCommonOptions, OptionError
from worlds.AutoWorld import World, WebWorld
from .Items import WaccaFixedItem, WaccaSongItem
from .Locations import WaccaLocation
from .Options import WaccaOptions, wacca_option_groups
from .WaccaCollection import WaccaCollections


class WaccaWebWorld(WebWorld):
    """wip"""
    theme = "partyTime"

    option_groups = wacca_option_groups


class WaccaWorld(World):
    """WACCA is a rhythm game"""

    # world options
    game = "WACCA"
    options_dataclass: ClassVar[Type[PerGameCommonOptions]] = WaccaOptions
    options: WaccaOptions

    topology_present = False
    web = WaccaWebWorld()

    # necessary data
    wacca_collection = WaccaCollections()

    item_name_to_id = {name: code for name, code in wacca_collection.item_names_to_id.items()}
    location_name_to_id = {name: code for name, code in wacca_collection.location_names_to_id.items()}
    item_name_groups = {
        "Songs": {name for name in wacca_collection.song_items.keys()}
    }

    # working data
    victory_song_name: str = ""
    starting_songs: List[str]
    included_songs: List[str]
    needed_token_count: int
    location_count: int

    def generate_early(self):
        versions = self.options.game_versions
        difficulty_min = self.options.difficulty_min
        difficulty_max = self.options.difficulty_max
        max_includes_plus = self.options.max_include_plus

        # the minimum number of songs to make an ok rando would be Starting Songs + 10 interim songs + goal song
        # interim songs being equal to max starting song count.
        starter_song_count = self.options.starting_song_count.value

        while True:
            # this should only need to run once

            available_song_keys = self.wacca_collection.get_songs_with_settings(versions.value, difficulty_min.value,
                                                                                difficulty_max.value,
                                                                                max_includes_plus == True)

            available_song_keys = self.handle_plando(available_song_keys)

            count_needed_for_start = max(0, starter_song_count - len(self.starting_songs))
            if len(available_song_keys) + len(self.included_songs) >= count_needed_for_start + 11:
                final_song_list = available_song_keys
                break

            # if the above fails we need to adjust the difficulty thresholds.
            # easier first, then harder.
            if difficulty_min <= 1 and difficulty_max >= 15:
                raise OptionError("failed to find enough songs, even with max difficulty")

            elif difficulty_min <= 1:
                difficulty_max += 1
            else:
                difficulty_min -= 1

        self.create_song_pool(final_song_list)

        for song in self.starting_songs:
            self.multiworld.push_precollected(self.create_item(song))

    def handle_plando(self, available_song_keys: List[str]) -> List[str]:
        song_items = self.wacca_collection.song_items

        start_items = self.options.start_inventory.value.keys()

        self.starting_songs = [s for s in start_items if s in song_items]
        self.included_songs = []

        return [s for s in available_song_keys if s not in start_items]

    def create_song_pool(self, available_song_keys: List[str]):
        starting_song_count = self.options.starting_song_count.value
        additional_song_count = self.options.additional_song_count.value

        self.random.shuffle(available_song_keys)

        # First, we must double-check if the player has included too many guaranteed songs
        included_song_count = len(self.included_songs)
        if included_song_count > additional_song_count:
            # If so, we want to thin the list, thus let's get the goal song and starter songs while we are at it.
            self.random.shuffle(self.included_songs)
            if not self.victory_song_name:
                self.victory_song_name = self.included_songs.pop()
            while len(self.included_songs) > additional_song_count:
                next_song = self.included_songs.pop()
                if len(self.starting_songs) < starting_song_count:
                    self.starting_songs.append(next_song)
        elif not self.victory_song_name:
            # If not, choose a random victory song from the available songs
            chosen_song = self.random.randrange(0, len(available_song_keys) + included_song_count)
            if chosen_song < included_song_count:
                self.victory_song_name = self.included_songs[chosen_song]
                del self.included_songs[chosen_song]
            else:
                self.victory_song_name = available_song_keys[chosen_song - included_song_count]
                del available_song_keys[chosen_song - included_song_count]
        elif self.victory_song_name in available_song_keys:
            available_song_keys.remove(self.victory_song_name)

        # Next, make sure the starting songs are fulfilled
        if len(self.starting_songs) < starting_song_count:
            for _ in range(len(self.starting_songs), starting_song_count):
                if len(available_song_keys) > 0:
                    self.starting_songs.append(available_song_keys.pop())
                else:
                    self.starting_songs.append(self.included_songs.pop())

        # Then attempt to fulfill any remaining songs for interim songs
        if len(self.included_songs) < additional_song_count:
            for _ in range(len(self.included_songs), self.options.additional_song_count):
                if len(available_song_keys) <= 0:
                    break
                self.included_songs.append(available_song_keys.pop())

        self.location_count = 2 * (len(self.starting_songs) + len(self.included_songs))

    def create_item(self, name: str) -> Item:
        if name == self.wacca_collection.PROGRESSION_NAME:
            return WaccaFixedItem(name, ItemClassification.progression_deprioritized_skip_balancing,
                                  self.wacca_collection.PROGRESSION_CODE, self.player)

        song = self.wacca_collection.song_items[name]
        return WaccaSongItem(name, self.player, song)

    def create_items(self) -> None:
        song_keys_in_pool = self.included_songs.copy()

        # note: item count will be off if plando is involved
        item_count = self.get_progression_count()

        # add all goal song tokens
        for _ in range(0, item_count):
            self.multiworld.itempool.append(self.create_item(self.wacca_collection.PROGRESSION_NAME))

        # then add 1 copy of every song
        item_count += len(self.included_songs)
        for song in self.included_songs:
            self.multiworld.itempool.append(self.create_item(song))

        items_left = self.location_count - item_count
        if items_left <= 0:
            return

        # add some duplicate songs to fill the space
        while items_left > len(song_keys_in_pool):
            for key in song_keys_in_pool:
                item = self.create_item(key)
                item.classification = ItemClassification.useful
                self.multiworld.itempool.append(item)

            items_left -= len(song_keys_in_pool)
            continue

        self.random.shuffle(song_keys_in_pool)
        for i in range(0, items_left):
            item = self.create_item(song_keys_in_pool[i])
            item.classification = ItemClassification.useful
            self.multiworld.itempool.append(item)

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        self.multiworld.regions += [menu_region]

        # Make a collection of all songs available for this rando.
        # 1. All starting songs
        # 2. All other songs shuffled
        # Doing it in this order ensures that starting songs are first in line to getting 2 locations.
        # Final song is excluded as for the purpose of this rando, it doesn't matter.

        all_selected_locations = self.starting_songs.copy()
        included_song_copy = self.included_songs.copy()

        self.random.shuffle(included_song_copy)
        all_selected_locations.extend(included_song_copy)

        # adds 2 item locations per song to the menu region
        for i in range(0, len(all_selected_locations)):
            name = all_selected_locations[i]
            loc1 = WaccaLocation(self.player, name + "-0", self.wacca_collection.song_locations[name + "-0"],
                                 menu_region)
            loc1.access_rule = lambda state, place=name: state.has(place, self.player)
            menu_region.locations.append(loc1)

            loc2 = WaccaLocation(self.player, name + "-1", self.wacca_collection.song_locations[name + "-1"],
                                 menu_region)
            loc2.access_rule = lambda state, place=name: state.has(place, self.player)
            menu_region.locations.append(loc2)

    def set_rules(self) -> None:
        self.multiworld.completion_condition[self.player] = lambda state: \
            state.has(self.wacca_collection.PROGRESSION_NAME, self.player, self.get_progression_win_count())

    def get_progression_count(self) -> int:
        multiplier = self.options.progression_count_percentage.value / 100.0
        song_count = len(self.starting_songs) + len(self.included_songs)
        return max(1, floor(song_count * multiplier))

    def get_progression_win_count(self) -> int:
        multiplier = self.options.progression_win_count_percentage.value / 100.0
        chart_count = self.get_progression_count()
        return max(1, floor(chart_count * multiplier))

    def fill_slot_data(self):
        return {
            "victoryLocation": self.victory_song_name,
            "deathLink": self.options.death_link.value,
            "progressionWinCount": self.get_progression_win_count(),
            "gradeNeeded": self.options.grade_needed.value,
        }
