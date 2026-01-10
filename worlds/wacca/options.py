from dataclasses import dataclass

from frozenlist import FrozenList

from Options import Choice, DeathLink, DefaultOnToggle, OptionGroup, OptionSet, PerGameCommonOptions, Range

from .wacca_collection import WaccaCollections


class GameVersions(OptionSet):
    """
    Game versions to include.
    Options:
    - WACCA
    - Lily
    - Reverse
    - Plus
    """

    display_name = "Game version"
    valid_keys = FrozenList(WaccaCollections.VERSIONS.keys())
    default = FrozenList(["WACCA", "Lily", "Reverse", "Plus"])


class DifficultyMin(Range):
    """
    Minimum difficulty for selected songs.
    Specifying + is not supported, selection covers the full difficulty constant range (12.0-12.9)
    """

    display_name = "Minimum difficulty"
    range_start = 1
    range_end = 15
    default = 12


class DifficultyMax(Range):
    """
    Maximum difficulty for selected songs.
    Specifies the 10s digit. Including + difficulty is the next option.
    """

    display_name = "Maximum difficulty"
    range_start = 1
    range_end = 15
    default = 13


class MaxIncludePlus(DefaultOnToggle):
    """If enabled, the maximum difficulty will include + charts (12.6-12.9)"""

    display_name = "Add + to max difficulty"
    default = True


class StartingSongs(Range):
    """The number of songs that will automatically be unlocked"""

    range_start = 3
    range_end = 10
    default = 5
    display_name = "Starting song count"


class AdditionalSongs(Range):
    """
    The total number of songs that will be placed in the randomization pool.
    - This does not count any starting songs or the goal song.
    - The final song count may be lower due to other settings.
    """

    range_start = 15
    range_end = 600  # Note will probably not reach this high if any other settings are done.
    default = 40
    display_name = "Additional Song Count"


class ProgressionCountPercentage(Range):
    """
    Controls how many Wedges are added to the pool based on the number of songs, including starting songs.

    Higher numbers leads to more consistent game lengths, but will cause individual Wedges to be less important.
    """

    range_start = 10
    range_end = 40
    default = 20
    display_name = "Wedge Percentage"


class ProgressionWinCountPercentage(Range):
    """The percentage of Wedges in the item pool that are needed to unlock the winning song."""

    range_start = 50
    range_end = 100
    default = 80
    display_name = "Wedges Needed to Win"


class GradeNeeded(Choice):
    """
    Completing a song will require a grade of this value or higher in order to unlock items.
    """

    display_name = "Grade Needed"
    option_AnyClear = 0  # noqa: N815
    option_S = 7  # noqa: N815
    option_SP = 8  # noqa: N815
    option_SS = 9  # noqa: N815
    option_SSP = 10  # noqa: N815
    option_SSS = 11  # noqa: N815
    option_SSSP = 12  # noqa: N815
    default = 0


wacca_option_groups = [
    OptionGroup(
        "Song Choice",
        [
            GameVersions,
        ],
    ),
    OptionGroup("Difficulty", [GradeNeeded, DifficultyMin, DifficultyMax, MaxIncludePlus, DeathLink]),
]


@dataclass
class WaccaOptions(PerGameCommonOptions):
    game_versions: GameVersions
    starting_song_count: StartingSongs
    additional_song_count: AdditionalSongs

    progression_count_percentage: ProgressionCountPercentage
    progression_win_count_percentage: ProgressionWinCountPercentage

    difficulty_min: DifficultyMin
    difficulty_max: DifficultyMax
    max_include_plus: MaxIncludePlus

    death_link: DeathLink
    grade_needed: GradeNeeded
