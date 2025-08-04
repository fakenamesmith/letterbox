from PIL import Image, ImageOps


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
