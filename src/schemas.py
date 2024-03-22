from dataclasses import dataclass


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
    level: int
    status: int

    @property
    def available_slot(self):
        slots = self.ccu_max - self.ccu_current
        return slots if slots > 0 else 0


@dataclass
class Response:
    status: bool
    error_code: int
    paged: int
    total_paged: int
    user: User
    data: list[Room]
