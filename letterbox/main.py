#

from PIL import Image, ImageOps
import tkinter as tk
from tkinter import filedialog
from typing_extensions import Annotated

# from typing import List
from typing import Union
import os
import configparser
import typer


cli = typer.Typer()

self_directory = os.path.dirname(os.path.realpath(__file__))

config_location = self_directory + ("/config.ini")


def reset_config():
    """Makes a new config and sets it to the default values."""
    config = configparser.ConfigParser(allow_no_value=True)
    config.add_section("Output Location")
    config.set("Output Location", "use_parent_dir", "True")
    config.set("Output Location", "subfolder", "None")
    config.set("Output Location", "output_file_path", "None")
    config.add_section("Output Filename")
    config.set("Output Filename", "use_original_filename", "True")
    config.set("Output Filename", "new_filename", "None")
    config.set("Output Filename", "suffix", "None")
    config.set("Output Filename", "prefix", "PADDED_")
    config.set("Output Filename", "overwrite_protection", "True")

    with open(config_location, "w") as configfile:
        config.write(configfile)
    return


# TODO: Add a config() function so you can set up the config from the command


def read_config(filepath: str) -> dict:
    """Reads a config file and returns a config dictionary.

    Args:
        filepath (str): path to config file

    Returns:
        dict[str:str]: config dictionary
    """
    config = configparser.ConfigParser()
    config.read(filepath)

    config = {
        "use_parent_dir": config.getboolean("Output Location", "use_parent_dir"),
        "subfolder": config.get("Output Location", "subfolder"),
        "output_file_path": config.get("Output Location", "output_file_path"),
        "use_original_filename": config.getboolean(
            "Output Filename", "use_original_filename"
        ),
        "new_filename": config.get("Output Filename", "new_filename"),
        "prefix": config.get("Output Filename", "prefix"),
        "suffix": config.get("Output Filename", "suffix"),
        "overwrite_protection": config.getboolean(
            "Output Filename", "overwrite_protection"
        ),
    }

    return config


def select_files() -> list[str]:
    """Opens a GUI window to select files. Returns selected files.

    Returns:
        list[str]: list of file picked paths
    """

    # Enable high-DPI scaling (for Windows systems)
    try:
        from ctypes import windll  # type: ignore

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        # If we're not on Windows or the module isn't available, do nothing
        pass
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    try:
        # Get the user's home directory and set it to the Pictures folder
        pictures_dir = os.path.expanduser("~/Pictures")

        # Open file dialog to select multiple files
        file_paths = filedialog.askopenfilenames(
            title="Select Pictures",
            initialdir=pictures_dir,
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                ("All Files", "*.*"),
            ],
        )

        # Convert the tuple of file paths to a list
        return list(file_paths)
    finally:
        # Ensure the Tkinter root window is properly destroyed
        root.destroy()


def add_padding(
    aspect_width: float,
    aspect_height: float,
    image_path: str,
    output_path: str,
    centering: tuple[float, float] = (0.5, 0.5),
    color: str = "black",
):
    """Pad a single image to an output path. Will overwrite files.

    Args:
        aspect_width (float): _description_
        aspect_height (float): _description_
        image_path (str): _description_
        output_path (str): _description_
        centering (tuple[float, float], optional): _description_. Defaults to (0.5, 0.5).
        color (str, optional): _description_. Defaults to "black".
    """

    aspect_ratio = (aspect_width, aspect_height)
    img = Image.open(image_path)
    width, height = img.size
    target_width, target_height = aspect_ratio

    # Calculate the target size
    target_aspect_ratio = target_width / target_height
    current_aspect_ratio = width / height

    if current_aspect_ratio > target_aspect_ratio:
        new_height = int(width / target_aspect_ratio)
        new_width = width
    else:
        new_width = int(height * target_aspect_ratio)
        new_height = height

    # Create a new image with the target size and a background color
    new_img = ImageOps.pad(
        img, (new_width, new_height), color=color, centering=centering
    )
    new_img.save(output_path)


def generate_output_path_from_config(config: Union[dict, str], filepath: str, sequence_number=0) -> str:  # type: ignore
    """Generates an output path, using the settings in the config.

    Args:
        config (Union[dict, str]): A path to the config file, or a dict representing the config.
        filepath (str): The original filepath (may not be necesarry, in that case use a dummy path for now).
        sequence_number (int, optional): _description_. Defaults to 0.

    Raises:
        NoValidOutputPathException: _description_
        NoValidOutputPathException: _description_
        NoValidOutputPathException: _description_

    Returns:
        str: output filepath
    """

    class NoValidOutputPathException(Exception):
        pass

    if isinstance(config, str):
        config = read_config(config)

    working_dir_name = os.path.dirname(filepath)
    file_extension = os.path.splitext(filepath)[1]
    original_filename = os.path.basename(filepath)[: ((-1) * len(file_extension))]

    config: dict = config

    # Generate directory
    if config["use_parent_dir"]:
        output_dir = working_dir_name
        if config["subfolder"] not in [None, "None"]:
            output_dir = output_dir + "/" + str(config["subfolder"])

    elif config["output_file_path"] not in [None, "None"]:
        output_dir = str(config["output_file_path"])
    else:
        raise NoValidOutputPathException(
            "No valid output file directory was generated from config. Check or reset config."
        )

    # Generate filename
    if config["use_original_filename"]:
        output_name = original_filename
        if config["prefix"] not in [None, "None"]:
            output_name = str(config["prefix"]) + output_name
        if config["suffix"] not in [None, "None"]:
            output_name = output_name + str(config["suffix"])
    elif config["new_filename"] not in [None, "None"]:
        output_name = config["new_filename"] + "_" + str(sequence_number)
    else:
        raise NoValidOutputPathException(
            "No valid output file name was generated from config. Check or reset config."
        )

    output_filepath = output_dir + "/" + output_name + file_extension

    # Overwrite protection
    if output_filepath == filepath and config["overwrite_protection"]:
        raise NoValidOutputPathException(
            "Original file path is same as output file path, but override protection is enabled. Check config."
        )

    return output_filepath


def pad_file_set(
    aspect_width: float,
    aspect_height: float,
    file_paths: list[str],
    output_paths: list[str],
    color: str,
    verbose: bool = False,
):
    """Adds colored bars to a list of files to some aspect ratio. Saves new files according to save_mode.

    Args:
        aspect_width (float): aspect width (e.g, <3> for a ratio of <3:2>)
        aspect_height (float): aspect height (e.g. <2> for a ratio of <3:2>)
        file_paths (list[str]): a list of paths in which to find the files to pad.
        output_paths (list[str]): a list of paths to which to output.
        color (str): background color (eg "black").
        overwrite_protect (bool, optional): Will raise an error when trying to overwrite an existing file. Default False
    """

    # TODO Validate lists for overwrites and formats!!!!

    if len(output_paths) != len(file_paths):
        raise ValueError("output_paths length does not match file_paths.")

    for i in range(len(file_paths)):
        file_path = file_paths[i]
        output_path = output_paths[i]
        add_padding(aspect_width, aspect_height, file_path, output_path, color=color)
        if verbose:
            print(
                f"Padded image at {file_path} and saved it in {file_path} to ratio "
                "{aspect_width}:{aspect_height} with the color {color}."
            )


def pad_files_with_config(
    aspect_width: float = None,
    aspect_height: float = None,
    file_paths: list = [],
    color: str = "black",
    use_gui: bool = False,
):
    """Pads files, respecting the config file. Prompts for missing info.

    Args:
        aspect_width (float, optional): aspect width (e.g, <3> for a ratio of <3:2>). Defaults to None.
        aspect_height (float, optional): aspect height (e.g. <2> for a ratio of <3:2>. Defaults to None.
        file_paths (list, optional): a list of paths in which to find the files to pad.. Defaults to [].
        color (str, optional): Background color. Defaults to "black".
        use_gui (bool, optional): Whether to use the graphical filepicker. Defaults to False.
    """

    # Prompt for aspect width and height if it doesn't exist:

    if aspect_width is None or aspect_height is None:
        aspect_width = typer.prompt("Aspect width", type=float)
        aspect_height = typer.prompt("Aspect height", type=float)
    # Get file list
    if use_gui and (file_paths != []):
        if typer.confirm(
            "You both provided files and asked for a graphical"
            + " interface to pick them. Add files using graphical filepicker?"
        ):
            file_list = file_paths + select_files()

    elif file_paths != []:
        file_list = file_paths

    elif use_gui:
        file_list = select_files

    elif typer.confirm(
        "No files to pad provided or GUI " + "flag specified. Use GUI selection?"
    ):
        file_list = select_files()
    else:
        print("No files provided. Exiting.")
        exit()

    # Remove duplicates in file list.
    file_list = list(set(file_list))  # Casting a list to a set back to a list.

    # Pad file list

    # TODO: Generate a list of output files. Then pass this effort to pad_file_list.
    number = 0
    output_paths = []
    for i in file_list[
        :
    ]:  # Iterating over a copy of file list so we can mutate it without bugs.
        # If the image is of a correct format, pad it.
        if os.path.splitext(i)[1] in [".jpeg", ".jpg", ".bmp", ".png", ".gif"]:
            # Generate a new path for the file based on config preferences.
            try:
                config = read_config(config_location)
            except configparser.NoSectionError:
                if typer.prompt("No config file found. Regenerate?", type=bool):
                    reset_config()
                    config = read_config(config_location)

            output_path = generate_output_path_from_config(config, i, number)
            print(output_path)
            # add_padding(aspect_width, aspect_height, i, output_path, color=color)
            # Instead of padding the file, we will just build the output path list.

            output_paths.append[output_path]

            number = number + 1

        # Otherwise, let the user know we're skipping a file.
        else:
            file_list.remove(i)
            print(f"The file {i} is of an unsupported format and was skipped.")

    # Send the files off to be padded.
    pad_file_set(aspect_width, aspect_height, file_list, output_paths, color)
    # Let the user know how much we padded
    print(f"Padded {number} files. Exiting.")


@cli.command(
    help="Pad a set of files into an output location as specified in <config.ini>."
)
def pad(
    inputs: Annotated[
        list[str],
        typer.Argument(
            help="Aspect ratio followed by file list (eg, 3 2 Image1.png Image2.png) to get a 3:2 image. "
            "Will prompt for missing arguments."
        ),
    ] = None,
    color: Annotated[
        str, typer.Option("-c", "--color", help="Color of crop bars.")
    ] = "black",
    use_gui: Annotated[
        bool, typer.Option(help="Use gui to select files, instead of -f.")
    ] = False,
    prompt: Annotated[bool, typer.Option(help="Prompt for missing arguments.")] = True,
):

    # Set default values before parsing input array.
    aspect_width = None
    aspect_height = None
    files = []

    # Dynamically parse the input array.

    if inputs is None:
        inputs = []  # Bandaid on a bug.

    arg_position = 0
    for arg in inputs:
        if (
            arg_position <= 1
        ):  # At this point, it could be either any of the three: a width, height, or filename.

            try:
                number = float(arg)
                argIsNumber = True

            except Exception:
                number = None
                argIsNumber = False

            if aspect_width is None and argIsNumber:
                aspect_width = number
            elif aspect_height is None and argIsNumber:
                aspect_height = number
            else:
                files.append(arg)
        else:
            files.append(arg)

        arg_position += 1

    if (not prompt) and (
        (files == [] and not use_gui) or aspect_width is None or aspect_height is None
    ):
        print("Missing or invalid arguments. Try <letterbox pad --help>. ")
        raise typer.Exit()

    # Handles the rest of the prompting work, respecting the config.
    pad_files_with_config(aspect_width, aspect_height, files, color, use_gui)


@cli.command("reset-config")
def click_reset_config():
    reset_config()
    return


# @ cli.command("save")
# def click_add_padding(
#     aspect_width: Annotated[float, typer.Argument()],
#     aspect_height: Annotated[float, typer.Argument()],
#     file_path: Annotated[str, typer.Argument()],
#     output_path: Annotated[str, typer.Argument()],
#     color: Annotated[str, typer.Option("--color", "-c")] = "black"
# ):
#     add_padding(aspect_width, aspect_height,
#                 file_path, output_path, color=color)


if __name__ == "__main__":
    try:
        cli()
    except TypeError:
        print("Argument Error. Defaulting to interactive version.")
        pad_files_with_config()
