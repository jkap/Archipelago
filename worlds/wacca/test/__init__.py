from typing import cast

from test.bases import WorldTestBase
from .. import WaccaWorld


class WaccaTestBase(WorldTestBase):
    game = "WACCA"

    def get_world(self) -> WaccaWorld:
        return cast(WaccaWorld, self.multiworld.worlds[1])
