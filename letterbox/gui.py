import tkinter as tk
from tkinter import filedialog
import os


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
