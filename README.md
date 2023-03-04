# Carta
Python library for making GUI applications on the reMarkable tablet wrapped around the ["simple"](https://rmkit.dev/apps/sas) application

# Simulating the ReMarkable device
It can be a pain having to transfer the script & run the script from the RM each time. Especially if you want to use the device for something else at the time. To help with this, I've made the option to manually set the command to a `simple` x64 binary that can be run on linux which will write to `fb.pnm` - This is the framebuffer file that you'll need to read from. 

In the `misc` folder I've provided the binary and a basic script as an example. To use this, just initialize the ReMarkable object like so:

```python
rm = ReMarkable(simple="path/to/simple/binay") 
```

Finally, checkout [remarkable-sim](https://github.com/Evidlo/remarkable_sim/) for events (like button clicking) support

# Using Carta
Carta's purpose is to function as a Python wrapper around [*sas*](https://rmkit.dev/apps/sas) - the simple app script for making apps on the reMarkable without need to compiling code.
It's written in python and is designed to be as user-friendly and easy to use as possible.

To use it, you'll need to install a few things onto your reMarkable, in an SSH session:
- [`toltec`](https://toltec-dev.org/) - an unofficial reMarkable-specific package manager
  See instructions on toltec's website.
- `simple`
  `opkg install simple`
- rM2 users need `display`
  `opkg install display`
- `pip` - the package manager for python
  ```
  wget https://bootstrap.pypa.io/get-pip.py
  python get-pip.py
  ```
- `carta` - this library
  `pip install carta`

After having installed all the prerequisites, you are ready to start developing.
Make a python script on the rM and run `chmod +x` on the script to make it executable.
You'll also need to add a `shebang` to the script (`#!/opt/bin/python` at the top) so that it knows what to run it with.

Here's an example script that you can copy:

```python
#!/opt/bin/python 
from carta import ReMarkable, Widget 
rm = ReMarkable() 

my_button = Widget(id="but1", typ="button", value="Hello!", x="50%", y="50%")

rm.add(my_button)
rm.display()
```

Let's walk through it line by line, 

```python
from carta import ReMarkable, Widget 
rm = ReMarkable() 
```

This imports the necessary "parts" for the library to function. The `ReMarkable` class is the main "driver" code and handles everything from interacting with `simple` to display your app to managing the widgets themselves. The `widget` dataclass are the actual contents themselves and there are 6 **core types**;
* Label
* Paragraph
* Button
* TextInput
* Text Area
* Image

Please refer to [the `simple` spec](https://rmkit.dev/apps/sas/spec) for more detailed information. 

```python
my_button = Widget(id="but1", type="button", value="Hello!", x="50%", y="50%")
```

Here we are making a new `Widget` which we have assigned to `my_button`.
The following is a table outlining information about supported arguments which can be given. 

| Argument | Required                      | Use                                                               | Supported inputs                                                                          | Notes                                                                                                               |
| -------- | ----------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| id       | Yes                           | Used to uniquely identify a widget when being interacted with     | Any string that hasn't been used before                                                   | Spaces will be converted to `_`                                                                                     |
| typ     | Yes                           | Gives a widget specific properties so it knows what to be used as | Any from the following: `label`, `paragraph`, `burtton`, `textinput`, `textarea`, `image` | Range is a WIP                                                                                                      |
| value    | Yes                           | What will be displayed on the widget                              | Any string (Image path for the `image` widget type)                                       | Be careful about using new lines                                                                                    |
| x        | Yes                           | Used to calculate the rendering position of the widget            | A percentage, keyword or an integer                                                       | Supported keywords are `same` (same value as previous item) and `step` (previous item's cord + previous items size) |
| y        | Yes                           | Used to calculate the rendering position of the widget            | A percentage, keyword or an integer                                                       | Supported keywords are `same` (same value as previous item) and `step` (previous item's cord + previous items size) |
| width    | No (Automatically calculated) | The width of the widget                                           | Any integer                                                                               | You might have some trouble with getting the right value for this                                                   |
| height   | No (Automatically calculated) | The height of the widget                                          | Any integer                                                                               | You might have some trouble with getting the right value for this                                                   |
| justify         | No (Optional for buttons) | Where the text sits in a button                                | Any string from the following: `center`, `right`, `left`                                                                                          |                                                                                                                     |

Finally, we want to add the widget to the actual screen. 

```python
rm.add(my_button)
rm.display()
```

I've made the decision to have widgets be manually added like this to make it easier to manage when making apps).
We can do this easily with `add(args*)`, where `args*` are any `Widget` types - For example,

```python
rm.add(my_button, label1, logo)
```

And then display it to the rM! The `display()` function will take all the currently active `Widgets` and convert them into something that simple can understand and render. The active widgets are all stored in the `screen` list (in this case `rm.screen`) and you can easily access and modify any of the widgets in there at any time via the `lookup` function which will return the `Widget` object that has the corresponding ID 

```python
print(rm.lookup("<id>"))
```

To remove a `Widget` you can use the `remove()` function and either supply it an `ID` or `Widget` object like so

```python
rm.remove("<id>")

rm.remove(my_button)
```

In case you want to fully clear the screen, you can use the `eclear()` function - however this does require the modified updated simple binary which `okeh` can provide for you! 

```python
rm.eclear()
```

Finally, there are two other options that the `ReMarkable` class has that we can modify. 
* Fontsize - Changes the fontsize of the text on the screen
* Timeout - The time after `simple` quits if no input is given
	* In this case, carrying on the program after `rm.display()`  has been run and no input has been given after a set time

For example, if we wanted to make the `fontsize` 24 and timeout the program after `30` seconds we would do

```python
rm.timeout = 32
rm.fontsize = 24
```

When you run the `display` function, carta will wait on any input being given **OR** the timeout being reached. When it's done this, it will return a `dict` object with the input given.

```python
clicked = rm.display()

print(clicked) # {"<id>": True}
```

If it's a `button` that has been pressed it will return `True` as the value, if anything else has been given it will use that specific input (for example, from the keyboard) as the value.


Hope this guide was helpful, feel free to ask if you need some help (`Jayy#6024` on discord)
