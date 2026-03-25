import os
import sys
import subprocess
import shutil

def build():
    """
    Builds the TEMIS MEMS LAB application into a standalone executable.
    """
    print("Starting build process for TEMIS MEMS LAB...")

    # Name of the entry point script
    entry_point = "main.py"
    app_name = "TEMIS_MEMS_LAB"

    # Folders to include as data
    # Format: "source_path;destination_path" (for Windows)
    datas = [
        "src;src",
        "config;config",
        "setup;setup",
        ".env;."
    ]

    # Build the PyInstaller command
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--name", app_name,
        "--clean",
        "--noconfirm",
    ]

    # Add data files
    for data in datas:
        cmd.extend(["--add-data", data])

    # Add hidden imports if necessary
    # ttkbootstrap sometimes needs explicit inclusion of its themes
    hidden_imports = [
        "ttkbootstrap",
        "PIL.ImageTk",
        "PIL.Image",
        "pyvisa_py"
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # Specify the entry point
    cmd.append(entry_point)

    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild successful!")
        print(f"The executable can be found in the 'dist/{app_name}' directory.")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("\nError: PyInstaller not found. Please install it with 'pip install pyinstaller'.")
        sys.exit(1)

if __name__ == "__main__":
    build()
