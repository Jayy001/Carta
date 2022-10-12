#!/opt/bin/python

import subprocess
import os
import copy

from dataclasses import dataclass
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

    low: Optional[int] = 1
    high: Optional[int] = 10

    @property
    def convert(self):
        layout = ""

        if self.justify:
            layout += f"@justify {self.justify}\n"

        layout += f"{self.typ}:{self.id} {self.x} {self.y} {self.width} {self.height} "

        if self.typ == "range":
            layout += f"{self.low} {self.high} "

        layout += self.value

        if "\n" in self.value:
            layout = "[" + layout + "]"

        return layout

    def __post_init__(self):
        if self.typ == "image":
            if not os.path.exists(self.value):
                raise OSError(f"Image path ({self.value}) does not exist")

        if self.typ == "range":
            if not all({self.low, self.high}):
                raise LookupError("You have specified a slider type but have not provided a high and low values")

            '''
            int_check = int(self.value.__index__())
            if int_check < 1:
                raise ValueError('Expected positive integer for value')
            '''

        if type(self.value) is not str:
            self.value = str(self.value)

        self.id = "_".join(self.id.split())
        self.state = None


class ReMarkable:
    def __init__(self) -> None:
        self.command = ["/opt/bin/simple"]

        if "reMarkable 2.0" in str(
                subprocess.check_output(["cat", "/sys/devices/soc0/machine"])
        ):
            self.command.insert(0, "rm2fb-client")

        self.reset()  # Don't make this a function?

    def display(self) -> bytes | dict:
        if not self.screen:
            return {}

        script = f"@fontsize {self.fontsize}\n"

        if self.timeout:
            script += f"@timeout {self.timeout}\n"

        layout = []
        for widget in self.screen:
            compiled_widget = copy.copy(widget)

            if {widget.width, widget.height} == {None}:
                (
                    compiled_widget.width,
                    compiled_widget.height,
                ) = self.calculate_width_height(widget)

            if "%" in str(widget.x):
                starting_point = float(widget.x.strip("%")) / 100 * 1380
                compiled_widget.x = starting_point - compiled_widget.width / 2

            if "%" in str(widget.y):
                starting_point = float(widget.y.strip("%")) / 100 * 1820
                compiled_widget.y = starting_point - compiled_widget.height / 2

            layout.append(compiled_widget.convert)

        script += "\n".join(layout)

        event = subprocess.Popen(
            self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        stdout, stderr = event.communicate(script.encode())

        out = {}

        if stdout:
            stdout = stdout.decode("utf-8").strip().split(": ")[1:]

            if len(stdout) == 1:  # Button
                out[stdout[0]] = True
            else:
                out[stdout[0]] = stdout[-1]  # Other

        return out

    def lookup(self, id: object) -> object:
        for widget in self.screen:
            if widget.id == id:
                return widget

    def add(self, *args) -> None:
        """
        `add` adds widgets to the screen

        args:Iterable[Widget]
        """
        for widget in args:
            if widget.id in [screen_widget.id for screen_widget in self.screen]:
                raise ValueError(f"Widget with id {widget.id} already exists")
            self.screen.append(widget)

    @staticmethod
    def eclear():
        os.system("rm2fb-client /opt/bin/eclear")

    def reset(self) -> None:
        self.screen = []
        self.fontsize = 32
        self.timeout = None

    def remove(self, id: int = None, widget: Widget = None) -> None:
        if widget:
            self.screen.remove(widget)

        if id:
            for widget in self.screen[:]:
                if widget.id == id:
                    self.screen.remove(widget)

    def calculate_width_height(self, widget: Widget) -> tuple[int, int]:
        if widget.typ == "image":
            info = (
                subprocess.check_output(["file", widget.value])
                .decode()
                .replace(",", " ")
            )
            width, height = [int(char) for char in info.split() if char.isdigit()]

        elif widget.typ == "range":
            width = (widget.high - widget.low) * 20
            height = self.fontsize * 1.3125

        else:
            width = (self.fontsize / 1.7) * len(widget.value)
            height = self.fontsize * 1.3125

        return width, height


"""
Make the images appear
Paragraph % length
"""
