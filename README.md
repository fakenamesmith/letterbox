Command line tool for adding crop bars to multiple images to bring them to a given aspect ratio.

Installation:
Use pip or pipx to install the wheel file in `/dist`.

Usage:
`letterbox --help`

Commands will prompt you for missing arguments, and offer a GUI selection prompt for images. You can edit the auto-generated config file to change output location. Some example commands are:

`letterbox pad`

`letterbox pad 3 2 path/to/Image1.png, path/to/Image2.png`

Development:
Project uses poetry. Start with `poetry install`, then `poetry env activate`, and run the command it gives you. You can then run `poetry run letterbox [args]` to run the project.
