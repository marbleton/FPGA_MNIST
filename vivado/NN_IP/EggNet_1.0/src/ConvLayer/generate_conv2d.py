# -*- coding: utf-8 -*-

import os
import shutil
import numpy as np
import re
import json
import argparse
import typing

BITS = 8
num_layers = 2

WEIGHT_QUANT_INT8_CONFIG_FILE = "../../../../../net/final_weights/int8_fpi/config.json"
WEIGHTS_QUANT_INT8_FILES_TXT = ["../../../../../net/final_weights/int8_fpi/cn1.k.txt",
                                "../../../../../net/final_weights/int8_fpi/cn2.k.txt"]

WEIGHTS_QUANT_INT8_FILES_BIN = ["../../../../../net/final_weights/int8_fpi/cn1.k.npy",
                                "../../../../../net/final_weights/int8_fpi/cn2.k.npy"]

WEIGHTS_NLQ3_FAKE = '../../../../../net/final_weights/nl3/fake.npz'
WEIGHTS_NLQ3_SHIFT = '../../../../../net/final_weights/nl3/shifts.npz'
WEIGHTS_NLQ3_SIGNS = '../../../../../net/final_weights/nl3/signs.npz'
WEIGHTS_NLQ3_CONFIG = '../../../../../net/final_weights/nl3/config.json'
WEIGHTS_NLQ4_FAKE = '../../../../../net/final_weights/nl4/fake.npz'
WEIGHTS_NLQ4_SHIFT = '../../../../../net/final_weights/nl4/shifts.npz'
WEIGHTS_NLQ4_SIGNS = '../../../../../net/final_weights/nl4/signs.npz'
WEIGHTS_NLQ4_CONFIG = '../../../../../net/final_weights/nl4/config.json'
WEIGHTS_NLQ5_FAKE = '../../../../../net/final_weights/nl5/fake.npz'
WEIGHTS_NLQ5_SHIFT = '../../../../../net/final_weights/nl5/shifts.npz'
WEIGHTS_NLQ5_SIGNS = '../../../../../net/final_weights/nl5/signs.npz'
WEIGHTS_NLQ5_CONFIG = '../../../../../net/final_weights/nl5/config.json'
TEMPLATE_CONV_CHANNEL_SHIFT_REL_PATH = 'conv_channel_shift_template.in'

if BITS == 4:
    WEIGHT_QUANT_INT8_CONFIG_FILE = "../../../../../net/final_weights/int4_fpi/config.json"
    WEIGHTS_QUANT_INT8_FILES_TXT = ["../../../../../net/final_weights/int4_fpi/cn1.k.txt",
                                    "../../../../../net/final_weights/int4_fpi/cn2.k.txt"]
    file_names_bias = ["../../../../../net/final_weights/int4_fpi/cn1.b.txt",
                       "../../../../../net/final_weights/int4_fpi/cn2.b.txt"]
elif BITS == 8:
    WEIGHT_QUANT_INT8_CONFIG_FILE = "../../../../../net/final_weights/int8_fpi/config.json"
    WEIGHTS_QUANT_INT8_FILES_TXT = ["../../../../../net/final_weights/int8_fpi/cn1.k.txt",
                                    "../../../../../net/final_weights/int8_fpi/cn2.k.txt"]
    file_names_bias = ["../../../../../net/final_weights/int8_fpi/cn1.b.txt",
                       "../../../../../net/final_weights/int8_fpi/cn2.b.txt"]

AUTO_GEN_FILE_PREEMBLE = """--
-- {{ file_name }}
--  
-- This file is autogenerated. Do not modify unless you know what you're doing.
-- 
-- (c) 2020, Yellow of the Egg Coders
--



"""


def main():
    # ----------------------
    # --- Clean Up Work Dir
    # ----------------------

    # %% create tmp folder, delete folder if not tmp exists and create new one

    if os.path.isdir(script_relative_path_to_abspath('channels')):
        shutil.rmtree(script_relative_path_to_abspath('channels'))
        shutil.rmtree(script_relative_path_to_abspath('channels_ben'))
        shutil.rmtree(script_relative_path_to_abspath('channels_shift'))
    os.makedirs(script_relative_path_to_abspath('channels'), exist_ok=True)
    os.makedirs(script_relative_path_to_abspath('channels_ben'), exist_ok=True)
    os.makedirs(script_relative_path_to_abspath('channels_shift'), exist_ok=True)

    # ----------------------
    # --- Setup Conv Layers
    # ----------------------

    weight_paths = list(map(script_relative_path_to_abspath, WEIGHTS_QUANT_INT8_FILES_BIN))
    template_path = script_relative_path_to_abspath('conv_channel_template_ben.in')

    with open(WEIGHT_QUANT_INT8_CONFIG_FILE, 'r') as fp_json:
        config_data = json.load(fp_json)

    # --- Read weights
    cn1_k = np.load(weight_paths[0])
    cn2_k = np.load(weight_paths[1])

    # --- Generate Channels for Layer 1
    for i in range(cn1_k.shape[-1]):
        output_path = script_relative_path_to_abspath(f'channels_ben/conv2d_l1_{i}.vhd')
        create_conv_channel(template_file_path=template_path,
                            output_file_path=output_path,
                            conv_weights=cn1_k[:, :, :, i],
                            conv_channel_name=f'conv2d_channel_l1_{i}')

    # --- Generate Channels for Layer 2
    for i in range(cn2_k.shape[-1]):
        output_path = script_relative_path_to_abspath(f'channels_ben/conv2d_l2_{i}.vhd')
        create_conv_channel(template_file_path=template_path,
                            output_file_path=output_path,
                            conv_weights=cn2_k[:, :, :, i],
                            conv_channel_name=f'conv2d_channel_l2_{i}')

    # ----------------------
    # --- Setup Shift Layers
    # ----------------------

    # --- Read weights
    w_shifts = np.load(script_relative_path_to_abspath(WEIGHTS_NLQ3_SHIFT))
    w_signs = np.load(script_relative_path_to_abspath(WEIGHTS_NLQ3_SIGNS))
    w_fake = np.load(script_relative_path_to_abspath(WEIGHTS_NLQ3_FAKE))

    # --- Read Config
    with open(script_relative_path_to_abspath(WEIGHTS_NLQ3_CONFIG), "r") as f:
        config = json.load(f)

    # -- Read in template
    conv_shift_template = AUTO_GEN_FILE_PREEMBLE + read_conv_channel_shift_template()

    for i_layer in [1, 2]:
        # The keys to access the data in the dictionary
        key_kernel = f'cn{i_layer}.k'
        key_bias = f'cn{i_layer}.b'

        # -- Create all the channel files
        # Iterate over the output channels -> last index
        for i_kernel_out in range(w_shifts[key_kernel].shape[-1]):
            file_name = f'conv_channel_l{i_layer}_{i_kernel_out}.vhd'
            output_path = script_relative_path_to_abspath(os.path.join('channels_shift', file_name))

            # Select Data
            kernel_shift = w_shifts[key_kernel][:, :, :, i_kernel_out]
            kernel_sign = w_signs[key_kernel][:, :, :, i_kernel_out]

            # Make the arrays conform to VHDL: 0 -> positive and 1 -> negative
            kernel_sign[kernel_sign == 1] = 0
            kernel_sign[kernel_sign == -1] = 1

            bias_shift = w_shifts[key_bias][i_kernel_out].astype(np.int)
            bias_sign = w_signs[key_bias][i_kernel_out].astype(np.int)

            # Convert Numpy Arrays using a helper function
            conv_channel_weights_s = npweights2vhdl_conv_channel(kernel_shift)
            conv_channel_signs_s = npweights2vhdl_conv_channel(kernel_sign, value_map_func=to_std_logic_str)

            data_dict = {
                'file_name': file_name,
                'conv_channel_name': f'cn_l{i_layer}_{i_kernel_out}',
                'input_bits': config['input_bits'][i_layer],
                'input_fac': config['input_frac'][i_layer],
                'output_bits': config['output_bits'][i_layer],
                'output_frac': config['output_frac'][i_layer],
                'output_max_value': config['out_max'][i_layer],
                'output_min_value': config['out_min'][i_layer],
                'output_shift': config['shifts'][i_layer],
                'weight_bits': config['nl_weight_bits'],
                'accumulator_additional_bits': config['accumulator_additional_bits'][i_layer],
                'conv_channel_weights': conv_channel_weights_s,
                'conv_channel_signs': conv_channel_signs_s,
                'n_input_channels': str(kernel_shift.shape[2]),
                'bias': str(bias_shift),
            }

            output_data = generic_template_match(conv_shift_template, data_dict=data_dict)
            with open(output_path, "w") as f:
                f.write(output_data)

        # -- Create the combined Conv2D Entity

    # ----------------------
    # --- Original Gen Code
    # ----------------------

    num_input_channels = [None] * num_layers
    num_output_channels = [None] * num_layers
    kernel_arrays = [None] * num_layers
    kernel_strings = [None] * num_layers
    channel_strings = [None] * num_layers
    msb = [None] * num_layers
    biases = [None] * num_layers

    for i in range(0, num_layers):
        msb[i] = config_data["shifts"][i] + config_data["output_bits"][i] - 1
        file = open(WEIGHTS_QUANT_INT8_FILES_TXT[i], 'r')
        file_bias = open(file_names_bias[i], 'r')
        def_line = file.readline()
        regex = re.compile(r"# \(3, 3, (.*?)\)\n")
        channel_def = list(map(int, regex.match(def_line).group(1).split(',')))
        num_input_channels[i] = channel_def[0]
        num_output_channels[i] = channel_def[1]
        kernel_arrays[i] = list(np.loadtxt(file, dtype=np.int8))
        kernel_arrays[i] = np.array(kernel_arrays[i]).reshape((3, 3, num_input_channels[i], num_output_channels[i]))
        kernel_strings[i] = np.ndarray((num_input_channels[i], num_output_channels[i]), dtype=object)
        biases[i] = list(np.loadtxt(file_bias, dtype=np.int16))

        for x in range(0, num_input_channels[i]):
            for y in range(0, num_output_channels[i]):
                kernel_strings[i][x][y] = "(" + \
                                          str(kernel_arrays[i][0][0][x][y]) + ", " + \
                                          str(kernel_arrays[i][1][0][x][y]) + ", " + \
                                          str(kernel_arrays[i][2][0][x][y]) + ", " + \
                                          str(kernel_arrays[i][0][1][x][y]) + ", " + \
                                          str(kernel_arrays[i][1][1][x][y]) + ", " + \
                                          str(kernel_arrays[i][2][1][x][y]) + ", " + \
                                          str(kernel_arrays[i][0][2][x][y]) + ", " + \
                                          str(kernel_arrays[i][1][2][x][y]) + ", " + \
                                          str(kernel_arrays[i][2][2][x][y]) + ")"
        channel_strings[i] = []
        for y in range(0, num_output_channels[i]):
            channel_strings[i].append('')
            channel_strings[i][y] += '('
            for x in range(0, num_input_channels[i]):
                channel_strings[i][y] += str(x) + " => "
                channel_strings[i][y] += kernel_strings[i][x][y]
                if x != num_input_channels[i] - 1:
                    channel_strings[i][y] += ', '
            channel_strings[i][y] += ')'
        file.close()
        file_bias.close()

    tp_file = open('conv_channel_template.in', 'r')
    tp_str = tp_file.read()
    i_convchan = 0
    for i in range(0, num_layers):
        for j in range(0, len(channel_strings[i])):
            tp_str_new = tp_str.replace("ConvChannelTemplate", "ConvChannel" + str(i_convchan))
            tp_str_new = re.sub("constant KERNELS : kernel_array_t :=[^\n]*\n",
                                "constant KERNELS : kernel_array_t := " + channel_strings[i][j] + ";\n", tp_str_new)
            tp_str_new = re.sub("\tN : integer :=[^\n]*\n", "\tN : integer := " + str(num_input_channels[i]) + ";\n",
                                tp_str_new)
            tp_str_new = re.sub("\tOUTPUT_MSB : integer :=[^\n]*\n", "\tOUTPUT_MSB : integer := " + str(msb[i]) + ";\n",
                                tp_str_new)
            tp_str_new = re.sub("\tBIAS : integer :=[^\n]*\n", "\tBIAS : integer := " + str(biases[i][j]) + "\n",
                                tp_str_new)
            tp_str_new = re.sub("\tBIT_WIDTH_IN : integer :=[^\n]*\n",
                                "\tBIT_WIDTH_IN : integer := " + str(config_data["input_bits"][i]) + ";\n", tp_str_new)
            tp_str_new = re.sub("\tBIT_WIDTH_OUT : integer :=[^\n]*\n",
                                "\tBIT_WIDTH_OUT : integer := " + str(config_data["output_bits"][i]) + ";\n",
                                tp_str_new)
            tp_str_new = re.sub("\tKERNEL_WIDTH_OUT : integer :=[^\n]*\n", "\tKERNEL_WIDTH_OUT : integer := " + str(
                config_data["output_bits"][i] + config_data["input_bits"][i] + int(np.ceil(np.log2(9)))) + ";\n",
                                tp_str_new)
            tp_file_new = open("channels/convchannel" + str(i_convchan) + ".vhd", 'w')
            tp_file_new.write(tp_str_new)
            tp_file_new.close()
            i_convchan += 1
    tp_file.close()

    tp_file = open('conv2d_template.in', 'r')
    tp_str = tp_file.read()
    entity_str = \
        "  convchan{I}" + " : entity " + "ConvChannel{J} \n" + \
        "  generic map( \n\
    BIT_WIDTH_IN => BIT_WIDTH_IN, \n\
    BIT_WIDTH_OUT => BIT_WIDTH_OUT) \n" + \
        "  port map(\n\
    Clk_i, n_Res_i,\n\
    Valid_i, valid_out({K}), Last_i, last_out({K}), Ready_i, ready_out({K}),\n" + \
        "    X_i,\n\
    Y_o({I+1}*BIT_WIDTH_OUT - 1 downto {I}*BIT_WIDTH_OUT)\n\
  ); \n\n"
    i_convchan = 0
    for i in range(0, num_layers):
        use_str = ""
        i_convchan_old = i_convchan
        for y in range(0, num_output_channels[i]):
            use_str += "use work.ConvChannel" + str(i_convchan) + ";\n"
            i_convchan += 1
        i_convchan = i_convchan_old
        tp_str_new = tp_str.replace(
            "use work.kernel_pkg.all;\n", "use work.kernel_pkg.all;\n" + use_str)
        tp_str_new = tp_str_new.replace("Conv2DTemplate", "Conv2D_" + str(i))
        tp_str_new = re.sub("INPUT_CHANNELS : integer := [^\n]*\n", "INPUT_CHANNELS : integer := " + str(
            num_input_channels[i]) + ";\n", tp_str_new)
        tp_str_new = re.sub("OUTPUT_CHANNELS : integer := [^\n]*\n", "OUTPUT_CHANNELS : integer := " + str(
            num_output_channels[i]) + "\n", tp_str_new)
        tp_str_new += "\narchitecture beh of " + "Conv2D_" + str(i) + " is\n " + \
                      "  signal ready_out :std_logic_vector(OUTPUT_CHANNELS-1 downto 0);\n" + \
                      "  signal valid_out :std_logic_vector(OUTPUT_CHANNELS-1 downto 0);\n" + \
                      "  signal last_out :std_logic_vector(OUTPUT_CHANNELS-1 downto 0);\n" + \
                      "begin\n" + \
                      "  Ready_o <= ready_out(0);\n" + \
                      "  Valid_o <= valid_out(0);\n" + \
                      "  Last_o <= last_out(0);\n"

        for y in range(0, num_output_channels[i]):
            entity_str_new = entity_str.replace("{J}", str(i_convchan))
            entity_str_new = entity_str_new.replace("{I}", str(y))
            entity_str_new = entity_str_new.replace(
                "{K}", str(i_convchan - i_convchan_old))
            entity_str_new = entity_str_new.replace("{I+1}", str(y + 1))
            tp_str_new += entity_str_new
            i_convchan += 1

        tp_str_new += "end beh;"
        tp_file_new = open("conv2d_" + str(i) + ".vhd", 'w')
        tp_file_new.write(tp_str_new)
        tp_file_new.close()
    tp_file.close()


def to_std_logic_str(x):
    return "'" + str(x) + "'"


def npweights2vhdl_conv_channel(kernel, value_map_func=str):
    # Split the kernels in 3x3 portions
    kernel_3x3s = np.split(kernel, kernel.shape[-1], axis=-1)

    # Define Helper Functions
    def npkernel2vhdl(k):
        # 1) Flatten in Fortran order gives us exactly the right ordering (rows first)
        # 2) Map every entry to string
        # 3) Join entries with commas and add parenthesis
        return '(' + ', '.join(map(value_map_func, k.flatten(order='F'))) + ')'

    def combine_kernels_index(index_and_kernel_tuple: typing.Tuple):
        ix, kernel_string = index_and_kernel_tuple
        return f'{ix} => {kernel_string}'

    # Combine all (from inner to outer):
    # 1) Map every np kernel to string using helper function
    # 2) combine it with a simple index array of the same size and zip them together
    # 3) Map every (index,kernel_string) pair to its VHDL form
    # 4) Finally combine all to a single string separated by commas and enclosed by parenthesis
    conv_channel_weights_s = '(' + ', '.join(map(
        combine_kernels_index,
        zip(range(kernel.shape[-1]),
            map(npkernel2vhdl, kernel_3x3s))
    )) + ')'
    return conv_channel_weights_s


def script_dir():
    """
    The current absolute directory
    Returns:

    """
    return os.path.dirname(os.path.abspath(__file__))


def create_conv_channel(template_file_path, output_file_path, conv_weights, conv_channel_name):
    """
    Refined creation of the convolutional channels
    Args:
        template_file_path:
        output_file_path:
        conv_weights:
        conv_channel_name:
    """
    with open(template_file_path, 'r') as ftemp:
        template = ftemp.read()

    # Replace all conv_channel_names by their names
    template = re.sub(
        pattern=r'{{[ ]*conv_channel_name[ ]*}}',
        repl=lambda x: conv_channel_name,
        string=template
    )

    # Convert weights to (x,y,z) format
    # By using order 'F' we flatten from the first axis to the last
    conv_weight_str = '(' + ','.join(map(str, conv_weights.flatten(order='F'))) + ')'
    # Replace all conv_channel_weights by their weights
    template = re.sub(
        pattern=r'{{[ ]*conv_channel_weights[ ]*}}',
        repl=lambda x: conv_weight_str,
        string=template
    )

    with open(output_file_path, 'w') as f:
        f.write(template)


_MATCH_STRING = r"{{[ ]*([a-zA-Z0-9_]+)[ ]*}}"


def replace_with_dict(d: typing.Dict[str, str], mo) -> str:
    """
    Returns the string representation of the matched object
    Args:
        d: Dictionary with the keys
        mo: Regex Match object

    Returns:
        A string
    """

    # mo is matchobject
    return str(d[mo.group(1)])


def generic_template_match(string: str, data_dict: typing.Dict[str, str]) -> str:
    """
    Helper function which searches for keys in the data string and replaces it with values provided by the data
    dictionary. Template tokens in the string must be in the form of '{{ token_123 }}' meaning the function searches for
    names enclosed by two curly braces. This name is then looked up in the dictionary and replaced by the found value.
    Token names can consist of letter, numbers and underscores.

    Args:
        string: The template string where the keys are searched
        data_dict: The dictionary containing the values

    Returns:
        The template string where all keys are replaced with the values of the dictionary.
    """
    f_repl = lambda mo: replace_with_dict(data_dict, mo)
    return re.sub(pattern=_MATCH_STRING, repl=f_repl, string=string)


def script_relative_path_to_abspath(fpath):
    """
    Appends the path to the script path and converts the result to an absolute path
    Args:
        fpath: Path to append

    Returns:
        The absolute combined path
    """
    return os.path.abspath(os.path.join(script_dir(), fpath))


def read_conv_channel_shift_template():
    with open(script_relative_path_to_abspath(fpath=TEMPLATE_CONV_CHANNEL_SHIFT_REL_PATH)) as f:
        return f.read()


if __name__ == '__main__':
    main()