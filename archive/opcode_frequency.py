import csv
from ctypes import util
import os
import sys
import utils
import subprocess


# Set path to opcodes here
opcodes_path = "features/opcodes.txt"
compilers = ['clang', 'gcc', 'icc']



def get_header():
    return ['label'] + get_opcodes(opcodes_path)


def get_opcodes(opcodes_path):
    """
    Create a list of opcodes from opcodes_path
    """
    # List of all opcodes
    opcodes = list()

    # Import opcodes from file
    with open(opcodes_path, "r") as file:
        lines = file.readlines()

        for opc in lines:
            opcodes.append(opc.strip())
            # print(opc.strip())
    
    return opcodes


def get_opcode_frequency(file_path, opcodes: list[str]):
    """
    Get frequency vector of file in file_path
    """
    frequency_vector = [0] * len(opcodes)
    text_disassembly = subprocess.getoutput(f'objdump -D -j .text {file_path}')
    text_disassembly = text_disassembly.split('\n')
    
    lines = [l for l in text_disassembly if utils.is_instruction(l)]
    
    for line in lines:

        for idx, opc in enumerate(opcodes):
            if opc in line:
                frequency_vector[idx] += 1

    return [i / len(lines) for i in frequency_vector]


def get_files_from_directory(dir_path):
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)

        if not os.path.isfile(file_path):
            continue
        else:
            yield file_path

def write_csv(dir_path, feature_name, label='label'):
    """
    Create a csv file containing an opcode frequency vector for each file in dir_path
    """
    opcodes = get_opcodes(opcodes_path)
    header = [label] + opcodes

    labels = compilers

    output_path = f'features/{feature_name}.csv'

    with open(output_path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)

        # write the header
        writer.writerow(header)
        
        for file_path in get_files_from_directory(dir_path):

            file_basename = os.path.basename(file_path)

            # Identify label
            for l in labels:
                if '_' + l in file_basename:
                    label = l
                    break
            
            frequency_vector = get_opcode_frequency(file_path, opcodes)

            writer.writerow([label] + frequency_vector)


def main():
    dir_path = sys.argv[1]
    csv_name = sys.argv[2]

    opcodes = get_opcodes(opcodes_path)

    utils.write_csv(
        dir_path, 
        header = get_header(), 
        feature_function = lambda x: get_opcode_frequency(x, opcodes),
        csv_name = csv_name, 
        labels = compilers, 
        kind = 'opcode_frequency', 
        exclude_filters=[r'o[0123s]']
    )




if __name__=='__main__':
    main()
            

        

        
