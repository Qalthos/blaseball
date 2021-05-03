from enum import IntEnum


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


Tarot = IntEnum(
    "Tarot",
    [
        "Fool",
        "I The Magician",
        "II The High Priestess",
        "III The Empress",
        "IIII The Emperor",
        "V The Heirophant",
        "VI The Lover",
        "VII The Chariot",
        "VIII Justice",
        "VIIII The Hermit",
        "X The Wheel of Fortune",
        "XI Strength",
        "XII The Hanged Man",
        "XIII The Moon",
        "XIIII Temperence",
        "XV The Devil",
        "XVI The Tower",
        "XVII The Star",
        "XVIII The Moon",
        "XVIIII The Sun",
        "XX Judgement",
        "XXI The World",
    ],
    start=0,
)
