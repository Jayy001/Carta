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

    fontsize: Optional[str] = None
    justify: Optional[str] = None

    low: Optional[int] = 1
    high: Optional[int] = 10

    rawfile: Optional[str] = "out.raw"
    pngfile: Optional[str] = "out.png"

    @property
    def convert(self):
        layout = ""

        layout += f"{self.typ}:{self.id} {self.x} {self.y} {self.width} {self.height} "

        if self.typ == "range":
            layout += f"{self.low} {self.high} "

        elif self.typ == "canvas":
            layout += f"{self.rawfile} {self.pngfile}"

        layout += self.value

        if "\n" in self.value:
            layout = "[" + layout + "]"

        if self.justify:
            layout = f"@justify {self.justify}\n{layout}"

        if self.fontsize:
            layout = f"@fontsize {self.fontsize}\n{layout}"

        return layout

    def initialize(self):
        if self.typ == "image":
            if not os.path.exists(self.value):
                # print(f"Image path ({self.value}) does not exist locally")
                pass

            if not all((self.width, self.height)):
                if os.name == "nt":
                    info = subprocess.check_output(
                        ["identify.exe", "-ping", "-format", "%w %h", self.value]
                    ).decode()
                elif os.name == "posix":
                    info = (
                        subprocess.check_output(["file", self.value])
                        .decode()
                        .replace(",", " ")
                    )

                self.width, self.height = [
                    int(char) for char in info.split() if char.isdigit()
                ]

        if self.typ == "range":
            if not all({self.low, self.high}):
                raise LookupError(
                    "You have specified a slider type but have not provided a high and low values"
                )

            int_check = int(self.value.__index__())
            if int_check < 1:
                raise ValueError("Expected positive integer for value")

        if type(self.value) is not str:
            self.value = str(self.value)

        self.id = "_".join(self.id.split())
        self.state = None

    def __post_init__(self):
        self.initialize()


class ReMarkable:
    def __init__(
        self,
        simple="/opt/bin/simple",
        justify="centre",
        timeout=None,
        fontsize=32,
        remote=False,
        directory=None,
        rm2fb=False,
        debug=False,
    ) -> None:
        self.debug = debug
        self.command = [simple]

        if rm2fb:
            self.command.insert(0, "rm2fb-client")

        if directory:
            self.command = ["cd", directory, "&&"] + self.command

        if remote:
            self.command = ["ssh", "root@" + remote] + self.command
        else:
            if not os.path.exists(simple):
                raise OSError("Simple binary not found")

        self.reset()

        self.fontsize = fontsize
        self.timeout = timeout
        self.justify = justify

    def display(self) -> bytes | dict:
        if not self.screen:
            return {}

        script = ""

        if self.timeout:
            script += f"@timeout {self.timeout}\n"

        layout = []

        for widget in self.screen:
            compiled_widget = copy.copy(widget)

            if compiled_widget.fontsize is None:
                layout.append(f"@fontsize {self.fontsize}")

            if compiled_widget.justify is None:
                layout.append(f"@justify {self.justify}")

            if (
                widget.width is None or widget.height is None
            ):  # TODO: Calculate width, height independently
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

        script += "\n".join(layout)  # TODO: Fix duplication

        if self.debug:
            print(script)

        event = subprocess.Popen(
            self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )
        stdout, stderr = event.communicate(script.encode())

        out = ()

        if stdout:
            stdout = stdout.decode("utf-8").strip().split(": ")[1:]

            if len(stdout) == 1:  # Button
                out = (stdout[0], True)
            else:
                out = (stdout[0], stdout[-1])  # Other

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

    def eclear(self):
        try:
            os.system(
                ' '.join(self.command[:-1] + ["/opt/bin/eclear"])
            ) 
            return True
        except Exception:
            return False 

    def reset(self) -> None:
        self.screen = []
        self.fontsize = 32
        self.justify = "centre"
        self.timeout = None

    def remove(self, id: int = None, widget: Widget = None) -> None:
        if widget:
            self.screen.remove(widget)

        if id:
            for widget in self.screen[:]:
                if widget.id == id:
                    self.screen.remove(widget)

    def calculate_width_height(self, widget: Widget) -> tuple[int, int]:
        if widget.typ == "range":
            width = (widget.high - widget.low) * 20
            height = self.fontsize * 1.3125

        else:
            if "\n" in widget.value:
                lines = widget.value.split("\n")
                width = (self.fontsize / 1.7) * len(max(lines))
                height = self.fontsize * 1.3125 * len(lines)

            else:
                width = (self.fontsize / 1.7) * len(widget.value)
                height = self.fontsize * 1.3125

        return width, height


"""
Paragraph % length
"""
