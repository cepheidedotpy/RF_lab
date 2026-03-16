import tkinter as tk
import ttkbootstrap as ttk
import os
from tkinter import scrolledtext
from typing import Optional, Literal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from dev import scripts_and_functions
from src.core.config import zva_parameters
from src.core import config as dir_and_var_declaration
from ttkbootstrap.constants import *

# ==============================================================================
# Globals
# ==============================================================================
tab_pad_x = 5
tab_pad_y = 5
default_style = 'darkly'


def add_tab(tab_name: str, notebook: ttk.Notebook, col: int, row: int) -> ttk.Labelframe:
    """
    Adds a tab to a notebook at the defined column and row and returns the tab instance.

    Parameters:
    tab_name (str): Name of the tab.
    notebook (ttk.Notebook): Notebook in which the tab is to be created.
    col (int): Column position within the notebook.
    row (int): Row position within the notebook.

    Returns:
    ttk.Frame: The created tab (frame) instance.
    """
    # Create a new frame (tab) with 'ridge' relief and a border width of 10.
    tab_inst = ttk.Labelframe(notebook, relief='ridge', borderwidth=10, name='{}'.format(tab_name.upper()))

    # Add the newly created tab to the notebook with the given tab name.
    notebook.add(tab_inst, text='{}'.format(tab_name))

    # Position the notebook at the specified column and row in the parent widget.
    notebook.grid(column=col, row=row, sticky="NSEW")

    # Return the created tab (frame) instance.
    return tab_inst


def add_button(tab: ttk.Labelframe | ttk.Frame, button_name: str, command: callable, col: int, row: int,
               style='TButton') -> ttk.Button:
    """
    Adds a button to a specified tab (Labelframe) with given name, command, column, and row.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the button is to be added.
    button_name (str): The text to be displayed on the button.
    command (callable): The function to be executed when the button is pressed.
    col (int): The column position within the Labelframe.
    row (int): The row position within the Labelframe.
    style (str): The style to apply to the button.

    Returns:
    ttk.Button: The created Button widget.
    """

    # Create a Button widget with the specified text and additional configurations.
    action = ttk.Button(
        tab,  # The parent Labelframe where the button is added.
        text=button_name,  # The text displayed on the button.
        command=command,  # The function to be executed on button press.
        style=style,
        bootstyle="outline"
    )

    # Place the Button widget at the specified column and row in the Labelframe.
    action.grid(column=col, row=row, sticky="nsew")

    # Return the created Button widget.
    return action


def update_button(button: ttk.Button) -> ttk.Button:
    """
    Changes the text on a button to 'Updated' for 500 milliseconds when the button is pressed,
    then changes it back to 'Update files'.

    Parameters:
    button (ttk.Button): The button whose text is to be changed.

    Returns:
    ttk.Button: The same button with updated behavior.
    """

    def update_text_back():
        # Change the button text back to 'Update files' after 500 milliseconds.
        button.configure(text='Update files')

    # Change the button text to 'Updated' immediately.
    button.configure(text='Updated')
    # Schedule the text to change back to 'Update files' after 500 milliseconds.
    button.after(ms=500, func=update_text_back)

    return button


def add_label(tab: ttk.Labelframe | ttk.Frame, label_name: str, col: int, row: int) -> ttk.Label:
    """
    Adds a Label widget to a specified tab (Labelframe) at the given column and row.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the Label is to be added.
    label_name (str): The text to be displayed on the Label.
    col (int): The column position within the Labelframe.
    row (int): The row position within the Labelframe.

    Returns:
    ttk.Label: The created Label widget.
    """
    # Create a Label widget with the specified text.
    label = ttk.Label(tab, text=label_name)

    # Place the Label widget at the specified column and row in the Labelframe.
    label.grid(column=col, row=row)

    # Return the created Label widget.
    return label


def add_scrolled_text(tab: ttk.Labelframe, scrolled_width: int, scrolled_height: int) -> scrolledtext.ScrolledText:
    """
    Adds a ScrolledText widget to a specified tab (Labelframe) with given width and height.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the ScrolledText is to be added.
    scrolled_width (int): The width of the ScrolledText widget.
    scrolled_height (int): The height of the ScrolledText widget.

    Returns:
    scrolledtext.ScrolledText: The created ScrolledText widget.
    """
    # Create a ScrolledText widget with the specified width, height, and other configurations.
    scroll = scrolledtext.ScrolledText(
        tab,  # The parent Labelframe where the ScrolledText is added.
        width=scrolled_width,  # Width of the ScrolledText widget.
        height=scrolled_height,  # Height of the ScrolledText widget.
        wrap=tk.WORD,  # Wrap text by words.
        border=2,  # Set border width of the widget.
        relief=tk.SUNKEN,  # Sunken relief appearance.
        pady=0  # Padding on the y-axis.
    )

    # Pack the ScrolledText widget to the top of the parent Labelframe.
    scroll.pack(side='top')

    # Return the created ScrolledText widget.
    return scroll


def add_label_frame(tab: ttk.Labelframe, frame_name: str, col: int, row: int, row_span: int = 1,
                    sticky=tk.N + tk.S + tk.W + tk.E) -> ttk.Labelframe:
    """
    Adds a Labelframe to a specified tab (Labelframe) with given name, column, row, and row span.
    The Labelframe is created with a 'ridge' relief and the label anchor set to North West.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the new Labelframe is to be added.
    frame_name (str): The text to be displayed on the Labelframe.
    col (int): The column position within the parent Labelframe.
    row (int): The row position within the parent Labelframe.
    row_span (int, optional): The number of rows the Labelframe should span. Default is 1.
    sticky: The sticky parameter for the grid layout.

    Returns:
    ttk.Labelframe: The created Labelframe widget.
    """
    # Create a Labelframe widget with the specified text, border width, relief, and label anchor.
    frame = ttk.Labelframe(
        tab,  # The parent Labelframe where the new Labelframe is added.
        text=frame_name,  # The text displayed on the Labelframe.
        borderwidth=5,  # Set the border width of the Labelframe.
        relief=tk.RIDGE,  # Set the relief style to 'ridge'.
        labelanchor='nw'  # Set the label anchor to North West.
    )

    # Place the Labelframe widget at the specified column and row in the parent Labelframe,
    # making it span the specified number of rows and stick to all sides of the cell.
    frame.grid(
        column=col,  # The column position within the parent Labelframe.
        row=row,  # The row position within the parent Labelframe.
        sticky=sticky,  # Make the Labelframe stick to all sides of the cell.
        rowspan=row_span  # Set the number of rows the Labelframe should span.
    )

    # Return the created Labelframe widget.
    return frame


def extension_detector(file: str) -> tuple:
    """
    Separates the file name and extension from a given file path.

    Parameters:
    file (str): The file path or file name to be processed.

    Returns:
    tuple: A tuple containing the file extension and the file name without the extension.
    """
    # Separate the file name and extension using os.path.splitext.
    file, extension = os.path.splitext(file)

    # Return the extension and the file name.
    return extension, file


def filetypes_dir(path: str) -> tuple[str]:
    """
    Separates different file types in the specified directory and returns tuples of s3p, s2p, and txt files.

    Parameters:
    path (str): The directory path to search for files.

    Returns:
    tuple: Three tuples containing s3p, s2p, and txt files, respectively.
    """
    if not path:
        return 'empty', 'empty'

    # List all files in the directory
    file_list = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

    # Initialize lists to store different types of files
    txt_files = []
    s1p_files = []
    s3p_files = []
    s2p_files = []

    # Loop through each file and classify by extension
    for file in file_list:
        extension, _ = extension_detector(file)
        if extension == '.txt':
            txt_files.append(file)
        elif extension == '.s3p':
            s3p_files.append(file)
        elif extension == '.s2p':
            s2p_files.append(file)
        elif extension == '.s1p':
            s1p_files.append(file)

    # Convert lists to tuples and return
    return tuple(s3p_files), tuple(s2p_files), tuple(txt_files), tuple(s1p_files)


def add_entry(tab: ttk.Labelframe | ttk.Frame, text_var: tk.StringVar | tk.DoubleVar, width: int, col: int,
              row: int) -> ttk.Entry:
    """
    Adds an Entry widget to a specified tab (Labelframe) with given text variable, width, column, and row.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the Entry is to be added.
    text_var (tk.StringVar or tk.DoubleVar): The text variable associated with the Entry widget.
    width (int): The width of the Entry widget.
    col (int): The column position within the parent Labelframe.
    row (int): The row position within the parent Labelframe.

    Returns:
    ttk.Entry: The created Entry widget.
    """
    # Create an Entry widget with the specified width, text variable, validation, and font.
    entered = ttk.Entry(
        tab,  # The parent Labelframe where the Entry is added.
        width=width,  # The width of the Entry widget.
        textvariable=text_var,  # The text variable associated with the Entry widget.
        validate='focus',  # Validation on focus.
        font=('Bahnschrift Light', 10)  # Font style and size.
    )

    # Place the Entry widget at the specified column and row in the parent Labelframe,
    # and make it stretch horizontally.
    entered.grid(
        column=col,  # The column position within the parent Labelframe.
        row=row,  # The row position within the parent Labelframe.
        sticky="WE"  # Make the Entry widget stretch horizontally.
    )

    # Return the created Entry widget.
    return entered


def add_combobox(tab: ttk.Labelframe, text: tk.StringVar, col: int, row: int, width: int) -> ttk.Combobox:
    """
    Adds a Combobox widget to a specified tab (Labelframe) with given text variable, column, row, and width.

    Parameters:
    tab (ttk.Labelframe): The parent Labelframe where the Combobox is to be added.
    text (tk.StringVar): The text variable associated with the Combobox widget.
    col (int): The column position within the parent Labelframe.
    row (int): The row position within the parent Labelframe.
    width (int): The width of the Combobox widget.

    Returns:
    ttk.Combobox: The created Combobox widget.
    """
    # Create a Combobox widget with the specified text variable, state, values, validation, width, height, and font.
    combobox = ttk.Combobox(
        master=tab,  # The parent Labelframe where the Combobox is added.
        textvariable=text,  # The text variable associated with the Combobox widget.
        state='readonly',  # Make the Combobox read-only.
        values=[''],  # Initialize the Combobox with an empty list of values.
        validate='focus',  # Validation on focus.
        width=width,  # The width of the Combobox widget.
        font=('Bahnschrift Light', 10)  # Font style and size.
    )

    # Place the Combobox widget at the specified column and row in the parent Labelframe.
    combobox.grid(
        column=col,  # The column position within the parent Labelframe.
        row=row  # The row position within the parent Labelframe.
    )

    # Return the created Combobox widget.
    return combobox


def add_Checkbutton(tab: ttk.Labelframe, text: tk.BooleanVar, col: int, row: int, off_value: int,
                    on_value: int, command: callable) -> ttk.Checkbutton:
    checkbutton = ttk.Checkbutton(
        master=tab,
        textvariable=text,
        state='readonly',
        command=command)

    checkbutton.grid(
        column=col,  # The column position within the parent Labelframe.
        row=row  # The row position within the parent Labelframe.
    )
    return checkbutton


def close_resources() -> None:
    """
    A function that acts as a wrapper to close all resources.

    Input:
        None - This function does not take any arguments.

    Output:
        None - This function does not return any value. It simply calls the
               `close_all_resources` method from the `scripts_and_functions` module
               to ensure that any open resources (e.g., files, connections, or other
               system resources) are properly closed and cleaned up.
    """
    scripts_and_functions.close_all_resources()


def call_s3p_config() -> None:
    """
    A function that calls the `load_config` function to load the S3P configuration file to the instrument.

    Input:
        None - This function does not take any arguments.

    Output:
        None - This function does not return any value. It invokes the `load_config` function
               with predefined file paths for the S3P configuration.

    Details:
        - Uses predefined file paths stored in the `dir_and_var_declaration.zva_parameters` dictionary:
          - `setup_s3p`: Path to the S3P configuration file on the PC.
          - `instrument_file`: Path to the instrument file location.
    """
    # Call the load_config function with predefined file paths for the S3P configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.zva_parameters["setup_s3p"],  # Path to the S3P configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
    )


def call_s2p_config() -> None:
    """
    A function that calls the `load_config` function to load the S2P configuration file to the instrument.

    Input:
        None - This function does not take any arguments.

    Output:
        None - This function does not return any value. It invokes the `load_config` function
               with predefined file paths for the S2P configuration.

    Details:
        - Uses predefined file paths stored in the `dir_and_var_declaration.zva_parameters` dictionary:
          - `setup_s2p`: Path to the S2P configuration file on the PC.
          - `instrument_file`: Path to the instrument file location.
    """
    # Call the load_config function with predefined file paths for the S2P configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.zva_parameters["setup_s2p"],  # Path to the S2P configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
    )


def call_s1p_config() -> None:
    """
    A function that calls the `load_config` function to load the S1P configuration file to the instrument.

    Input:
        None - This function does not accept any arguments.

    Output:
        None - This function does not return a value. Instead, it invokes the `load_config` function
               with predefined file paths for the S1P configuration.

    Details:
        - The file paths are retrieved from the `dir_and_var_declaration.zva_parameters` dictionary:
            - `setup_s1p` : The path to the S1P configuration file on the PC.
            - `instrument_file` : The path to the instrument file location on the target instrument.
    """
    # Call the load_config function with predefined file paths for the S1P configuration.
    scripts_and_functions.load_config(
        pc_file=dir_and_var_declaration.zva_parameters["setup_s1p"],  # Path to the S1P configuration file on the PC.
        inst_file=dir_and_var_declaration.zva_parameters["instrument_file"]  # Path to the instrument file location.
    )


def update_entries(directory: str, combobox: ttk.Combobox, filetype: str) -> ttk.Combobox:
    """
    Updates the values of a Combobox based on the specified file type from the given directory.

    Parameters:
    directory (str): The directory path to search for files.
    combobox (ttk.Combobox): The Combobox widget to update with file names.
    filetype (str): The file type to filter for updating the Combobox values.

    Returns:
    ttk.Combobox: The updated Combobox widget.
    """
    # Get the files in the directory classified by their extensions.
    files = filetypes_dir(directory)

    # Update the Combobox values based on the specified file type.
    if filetype == '.s2p':
        combobox['values'] = files[1]  # Update with s2p files.
    elif filetype == '.s3p':
        combobox['values'] = files[0]  # Update with s3p files.
    elif filetype == '.txt':
        combobox['values'] = files[2]  # Update with txt files.

    # Return the updated Combobox widget.
    return combobox


def create_canvas(figure: plt.Figure, frame: ttk.Labelframe | ttk.Frame,
                  toolbar_frame: Optional[ttk.Labelframe | ttk.Frame] = None,
                  toolbar: Optional[bool] = True, toolbar_side=tk.TOP, canvas_side=tk.RIGHT) -> FigureCanvasTkAgg:
    """
    Creates display Canvas in the specified frame, and optionally adds a toolbar.

    Parameters:
    figure (plt.Figure): The matplotlib figure to be displayed on the canvas.
    frame (ttk.Frame): The parent frame where the canvas is to be added.
    toolbar_frame (ttk.Frame, optional): The frame where the toolbar is to be added.
    If None, toolbar is added to the same frame as the canvas.
    toolbar (bool, optional): Whether to add a navigation toolbar. Default is True.
    toolbar_side (tk.TOP or tk.BOTTOM): Where to pack the toolbar. Default is tk.TOP.
    canvas_side (tk.RIGHT): Where to pack the canvas. Default is tk.RIGHT.

    Returns:
    FigureCanvasTkAgg: The created canvas with the matplotlib figure.
    """
    # Create a FigureCanvasTkAgg widget with the specified figure and parent frame.
    canvas = FigureCanvasTkAgg(figure, master=frame)

    # Pack the canvas widget with specified padding.
    canvas.get_tk_widget().pack(ipady=2, ipadx=2, expand=True, fill=tk.BOTH, side=canvas_side, anchor=tk.CENTER)

    # Optionally add a navigation toolbar.
    if toolbar:
        if toolbar_frame is None:
            toolbar_frame = frame  # Use the same frame if no separate toolbar frame is provided
        toolbar_widget = NavigationToolbar2Tk(canvas=canvas, window=toolbar_frame)
        toolbar_widget.update()
        toolbar_widget.pack(side=toolbar_side, fill=tk.BOTH, expand=False)

    # Return the created canvas widget.
    return canvas


def file_name_creation(data_list: list, text: tk.Text, end_characters: str = '') -> str:
    """
    Creates a filename by joining elements of a data list with hyphens and appending end characters.
    Updates a given text widget with the created filename and prints it.

    Parameters:
    data_list (list): List of strings to be joined into a filename.
    text (tkinter.Text): Text widget to be updated with the created filename.
    end_characters (str, optional): Characters to be appended at the end of the filename. Default is an empty string.

    Returns:
    str: The created filename.
    """
    # Clear the current content of the text widget.
    text.delete(index1="1.0", index2="1.end")

    # Create the filename by joining elements of the data list with hyphens and appending end characters.
    filename = '-'.join(data_list) + end_characters

    # Insert the created filename into the text widget at the beginning.
    text.insert(index="1.0", chars=filename)

    # Print the created filename.
    print(filename)

    # Return the created filename.
    return filename


def create_figure(num: int, figsize: tuple[float, float]):
    """Helper method to create a matplotlib figure."""
    return plt.figure(num=num, dpi=100, tight_layout=True, figsize=figsize, frameon=True)


def create_figure_with_axes(num: int, figsize: tuple[float, float]):
    """Helper method to create a matplotlib figure and its axes."""
    fig = create_figure(num, figsize)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid()
    return fig, ax


def add_slider(frame, _from, to, name, variable, step, orientation: Literal["horizontal", "vertical"] = tk.HORIZONTAL):
    slider_frame = ttk.Frame(frame, bootstyle=DARK, style=DARK)
    slider_frame.pack(pady=10)

    if orientation == tk.VERTICAL:
        # Create a canvas for the vertical text
        canvas = tk.Canvas(slider_frame, width=20, height=250)
        canvas.create_text(10, 125, text=name, angle=90, font=('Bahnschrift Light', 10))
        canvas.pack(side=tk.LEFT, padx=5, pady=5)

        # Create the vertical slider
        # slider = tk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, length=250, digits=2,
        #                    relief=tk.GROOVE, border=2, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
        #                    font=('Bahnschrift Light', 10))
        # slider.pack(side=tk.RIGHT, padx=5, pady=5)
        slider = ttk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, length=250,
                           bootstyle=default_style, variable=variable)
        slider.pack(side=tk.RIGHT, padx=5, pady=5)
    else:
        # Create the horizontal slider with a label
        # slider = tk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, label=name, length=250,
        #                    digits=2,
        #                    relief=tk.GROOVE, border=2, sliderrelief=tk.RIDGE, tickinterval=step, variable=variable,
        #                    font=('Bahnschrift Light', 10))
        slider = ttk.Scale(master=slider_frame, from_=_from, to=to, orient=orientation, length=250,
                           bootstyle=default_style, variable=variable)
        slider.pack()

    # Center the frame within the parent frame
    slider_frame.pack(side="left", anchor=tk.CENTER)

    return slider


def add_small_scale(frame: ttk.Frame, name: str, col: int, row: int) -> ttk.Scale:
    """
    Creates a label and a smaller-length horizontal scale widget in the given frame.

    Inputs:
        frame (ttk.Frame): The parent frame where the label and scale will be placed.
        name (str)       : The text to display on the label.
        col (int)        : The column position (for grid geometry) of the label and scale.
        row (int)        : The row position (for grid geometry) of the label and scale.

    Output:
        ttk.Scale: The created scale widget (not yet placed on the grid).

    Details:
        - A ttk.Label is created using the provided 'name' parameter, but the `.grid(...)`
          call is currently commented out to show flexibility in placement.
        - A ttk.Scale is created with a smaller length (100 pixels).
        - The scale's style ("TScale") is configured for appearance, including thickness.
        - This function returns the scale widget so that it can be placed or manipulated later.
    """

    # Create a label to display the provided name.
    label = ttk.Label(frame, text=name)
    # label.grid(column=col, row=row, padx=5, pady=5)
    # (Commented out for flexibility in positioning)

    # Create a horizontal scale with a smaller length (100px by default).
    scale = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL, length=100)
    # scale.grid(column=col + 1, row=row, padx=5, pady=5)
    # (Commented out for flexibility in positioning)

    # Configure the appearance of the scale via style settings.
    # scale.configure(style="TScale")
    # s = ttk.Style()
    # s.configure("TScale", thickness=10)  # Adjust thickness as needed

    # Return the scale so the caller can place it or further configure it.
    return scale
