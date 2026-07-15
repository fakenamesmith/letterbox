from typing_extensions import Annotated
import os
import configparser
import typer
from .config import reset_config, read_config, generate_output_path_from_config, config_location
from .gui import select_files
from .image_ops import pad_file_set

cli = typer.Typer()


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

            output_paths.append(output_path)

            number = number + 1

        # Otherwise, let the user know we're skipping a file.
        else:
            file_list.remove(i)
            print(f"The file {i} is of an unsupported format and was skipped.")

    # Send the files off to be padded.
    pad_file_set(aspect_width, aspect_height, file_list, output_paths, color)
    # Let the user know how much we padded
    print(f"Padded {number} files. Exiting.")
