from typing import NamedTuple, Optional

from BaseClasses import Item, ItemClassification


class SongData(NamedTuple):
    """Special data container for filtering"""
    code: Optional[int]
    id: int
    version: int

    normal: float
    hard: float
    expert: float
    inferno: Optional[float]


class WaccaSongItem(Item):
    game: str = "WACCA"

    def __init__(self, name: str, player: int, data: SongData) -> None:
        super().__init__(name, ItemClassification.progression, data.code, player)


class WaccaFixedItem(Item):
    game: str = "WACCA"

    def __init__(self, name: str, classification: ItemClassification, code: Optional[int], player: int) -> None:
        super().__init__(name, classification, code, player)
