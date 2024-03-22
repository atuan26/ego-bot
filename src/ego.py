# from .schemas import Response
import os
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class User:
    user_rank: str
    elo: int
    elo_user: dict


@dataclass
class Room:
    id: int
    name: str
    password: str
    ccu_current: int
    ccu_max: int
    type: int
    vpn_id: int
    status_class: str
    order: int
    rank_name: str
    rank: str
    level: int
    status: int

    @property
    def available_slot(self):
        slots = self.ccu_max - self.ccu_current
        return slots if slots > 0 else 0

    @property
    def avaiable_message(self):
        return f"🎇 {self.name}: {self.available_slot} slot"


@dataclass
class Response:
    status: bool
    error_code: int
    paged: int
    total_paged: int
    user: User
    data: List[Room]

    @property
    def available_rooms(self):
        return [Room(**room) for room in self.data if Room(**room).available_slot > 0]

    @classmethod
    def build_message(cls, rooms: List[Room]):
        res = []
        for room in rooms:
            res.append(f"- {room.name}: {room.available_slot} slot")
        res = "\n".join(res)
        return f"""
Available rooms:
{res}

Turn off notification: /off
        """


def get_room_status() -> tuple[User, list[Room]]:
    EGO_ROOM_STATUS_URL = os.getenv("EGO_ROOM_STATUS_URL")

    PARAMS = {
        "user_hash": os.getenv("EGO_USER_HASH"),
        "type": 3,
        "order": 1,
    }

    res = requests.get(EGO_ROOM_STATUS_URL, params=PARAMS)
    return Response(**res.json())
