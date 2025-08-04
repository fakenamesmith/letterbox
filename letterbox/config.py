from typing import Union
import os
import configparser

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
