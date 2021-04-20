from enum import IntEnum

AdvancedStats = IntEnum(
    "AdvancedStats",
    {
        "Tragicness": 0,
        "Thwackability": 2,
        "Laserlikeness": 10,
        "Continuation": 11,
        "Ground Friction": 13,
        "Shakespearianism": 14,
        "Suppression": 15,
        "Unthwackability": 16,
        "Coldness": 17,
        "Overpowerment": 18,
        "Ruthlessness": 19,
        "Watchfulness": 23,
    },
)


Locations = IntEnum(
    "Locations",
    [
        "Lineup",
        "Rotation",
        "Shadow Lineup",
        "Shadow Rotation",
    ],
    start=0,
)


ModColor = IntEnum(
    "ModColor",
    [
        "#dbbc0b",
        "#c2157a",
        "#0a78a3",
        "#639e47",
    ],
    start=0,
)
