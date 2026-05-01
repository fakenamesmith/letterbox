Command line tool for adding crop bars to multiple images to bring them to a given aspect ratio.

## Installation:
Use pip or pipx to install the wheel file in `/dist`:
```
git clone https://github.com/fakenamesmith/letterbox
pipx install dist/letterbox-0.1.0-py3-none-any.whl

```

You may need to ensure the tkinter module comes with your Python. If it doesn't:
```
sudo apt install python3-tk
```

## Using the project:

Usage:
`letterbox --help`

Commands will prompt you for missing arguments, and offer a GUI selection prompt for images. You can edit the auto-generated config file to change output location. Some example commands are:

`letterbox pad`

`letterbox pad 3 2 path/to/Image1.png, path/to/Image2.png`

## Making changes:
Development:
Project uses poetry. Start with `poetry install`, then `poetry env activate`, and run the command it gives you. You can then run `poetry run letterbox [args]` to run the project and test your changes.
