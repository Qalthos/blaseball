from rich.layout import Layout
from rich.panel import Panel

layout = Layout()
layout.split(
    Layout(name="header"),
    Layout(name="content"),
)
layout["header"].size = 3
layout["content"].split(
    Layout(name="The Wild League"),
    Layout(name="The Mild League"),
    direction="horizontal",
)
