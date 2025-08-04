from .cli import cli
from .cli import pad_files_with_config

if __name__ == "__main__":
    try:
        cli()
    except TypeError:
        print("Argument Error. Defaulting to interactive version.")
        pad_files_with_config()
