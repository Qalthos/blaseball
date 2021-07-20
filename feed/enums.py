from enum import IntEnum

Location = IntEnum(
    "Location",
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
