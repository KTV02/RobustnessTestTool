import tkinter as tk
from tkinter import filedialog


def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    file_path = filedialog.askopenfilename(filetypes=[('tar files', '*.tar')])
    if file_path is not None:
        return file_path
    else:
        return "False"


if __name__ == "__main__":
    result = open_file_dialog()
    print(result)
