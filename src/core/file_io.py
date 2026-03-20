import os
import time
import numpy as np
from src.core import config as dir_and_var_declaration
from RsInstrument import RsInstrException, TimeoutException, StatusException

def _get_zva():
    from src.core.scripts_and_functions import zva
    return zva

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

    # Return the file name and the extension.
    return file, extension

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
        _, extension = extension_detector(file)
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

def saves3p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    print(directory)
    zva = _get_zva()
    try:
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORT 1, '{}.s3p' , LOGPhase, 1,2,3".format(filename))
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s3p'".format(filename))
        print(r"s3p file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('Status Error \n')
        zva.visa_timeout = 1000

def saves2p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    zva = _get_zva()
    try:
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory), timeout=1000)
        time.sleep(1)
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:PORTs 1, '{}.s2p', LOGPhase, 1,2".format(filename))
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s2p'".format(filename))
        print(r"sp file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('RsInstrException Error \n')
    finally:
        if zva: zva.visa_timeout = 1000

def saves1p(filename: str) -> None:
    directory = dir_and_var_declaration.zva_parameters["zva_traces"]
    zva = _get_zva()
    try:
        # print(zva.query_str_with_opc(r"MMEMory:CDIRectory?"), end='\n')
        zva.write_str_with_opc(r"MMEMory:CDIRectory '{}'".format(directory))
        # time.sleep(1)
        zva.write_str_with_opc(r"MMEMory:STORe:TRACe 'Trc1', '{}.s1p'".format(filename))
        # zva.write_str_with_opc(r"MMEMory:STORe:TRACe:CHAN 1, '{}.s1p'".format(filename))
        print(r"sp file saved in ZVA at {}".format(directory), end='\n')
    except TimeoutException as e:
        print(e.args[0])
        print('Timeout Error \n')

    except StatusException as e:
        print(e.args[0])
        print('Status Error \n')

    except RsInstrException as e:
        print(e.args[0])
        print('Status Error \n')
    finally:
        if zva: zva.visa_timeout = 1000

def file_get(filename: str, zva_file_dir: str = dir_and_var_declaration.ZVA_File_Dir_ZVA67,
             pc_file_dir: str = dir_and_var_declaration.PC_File_Dir, extension: str = 's2p') -> None:
    zva_file_dir = dir_and_var_declaration.zva_parameters["zva_traces"]
    zva = _get_zva()
    
    if extension == 's3p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}/{}.s3p".format(zva_file_dir, filename),
                                                r"{}/{}.s3p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            if zva: zva.visa_timeout = 1000
    if extension == 's2p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}/{}.s2p".format(zva_file_dir, filename),
                                                r"{}/{}.s2p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            if zva: zva.visa_timeout = 1000
    if extension == 's1p':
        try:
            zva.read_file_from_instrument_to_pc(r"{}/{}.s1p".format(zva_file_dir, filename),
                                                r"{}/{}.s1p".format(pc_file_dir, filename),
                                                append_to_pc_file=False)
        except TimeoutException as e:
            print(e.args[0])
            print('TimeoutException Error \n')
        except StatusException as e:
            print(e.args[0])
            print('StatusException Error \n')
        except RsInstrException as e:
            print(e.args[0])
            print('RsInstrException Error \n')
        finally:
            if zva: zva.visa_timeout = 1000

def check_if_file_name_exists(filename: str, directory: str) -> bool:
    listed_files: list = []
    if '.txt' in filename:
        listed_files = filetypes_dir(directory)[2]
    elif '.s1p' in filename:
        listed_files = filetypes_dir(directory)[3]
    elif '.s2p' in filename:
        listed_files = filetypes_dir(directory)[1]
    elif '.s3p' in filename:
        listed_files = filetypes_dir(directory)[0]
    # print(listed_files)
    if filename in listed_files:
        return True
    else:
        return False
