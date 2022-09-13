#!/opt/bin/python

import subprocess
import os
import copy

from dataclasses import dataclass, asdict
from collections.abc import Iterable
from typing import Optional


@dataclass
class Widget:
    id: str
    typ: str
    value: str

    x: int | str = "step"
    y: int | str = "step"
    width: int | str | None = None
    height: int | str | None = None

    justify: Optional[str] = None

    def convert(self):
        layout = ""

        if self.justify:
            layout += f"@justify {self.justify}\n"

        layout += f"{self.typ}:{self.id} {self.x} {self.y} {self.width} {self.height} {self.value}"

        if "\n" in self.value:
            layout = "[" + layout + "]"

        return layout

    def __post_init__(self):
        if self.typ == "image":
            if not os.path.exists(self.value):
                raise OSError(f"Image path ({self.value}) does not exist")


class ReMarkable:
    def __init__(self, version: int) -> None:
        self.command = ["/opt/bin/simple"]

        if version == 2:
            self.command.insert(0, "rm2fb-client")

        self.reset()

    def display(self) -> str:
        if self.screen == None:
            return {}

        script = f"@fontsize {self.fontsize}\n"

        if self.timeout:
            script += f"@timeout {self.timeout}\n"

        layout = []
        for widget in self.screen:
            compiled_widget = copy.copy(widget)

            if set((widget.width, widget.height)) == {None}:
                (
                    compiled_widget.width,
                    compiled_widget.height,
                ) = self.caculate_width_height(widget)

            if "%" in str(widget.x):
                starting_point = (
                    float(widget.x.strip("%")) / 100 * 1380
                ) 
                compiled_widget.x = starting_point - compiled_widget.width / 2

            if "%" in str(widget.y):
                starting_point = (
                    float(widget.y.strip("%")) / 100 * 1820
                ) 
                compiled_widget.y = starting_point - compiled_widget.height / 2

            layout.append(compiled_widget.convert())

        script += "\n".join(layout)

        event = subprocess.Popen(
            self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        stdout, stderr = event.communicate(script.encode())

        return stdout

    def reset(self) -> None:
        self.screen = []
        self.fontsize = 32
        self.timeout = None

    def add_multiple(self, widgets: Iterable[Widget]) -> None:
        for widget in widgets:
            self.screen.append(widget)

    def add(self, widget: Widget) -> None:
        self.screen.append(widget)

    def remove(self, id: int = None, widget: Widget = None) -> None:
        if widget:
            self.screen.remove(widget)

        if id:
            for widget in self.screen[:]:
                if widget.id == id:
                    self.screen.remove(widget)

    def caculate_width_height(self, widget: Widget) -> tuple[int, int]:
        if widget.typ == "image":
            info = subprocess.check_output(['file', widget.value]).decode().replace(',', ' ')
            width, height = [int(char) for char in info.split() if char.isdigit()]

        else:
            width = (self.fontsize / 1.7) * len(widget.value)
            height = self.fontsize * 1.3125

        return width, height

rm = ReMarkable(2)
w1 = Widget(id="button1", typ="button", value="Click me!", x="50%", y="50%")
w2 = Widget(id="button1", typ="image", value="me.png", x="40%", y="10%")

rm.add_multiple([w1, w2])
rm.display()

'''
Make the images appear
Paragraph % length
'''