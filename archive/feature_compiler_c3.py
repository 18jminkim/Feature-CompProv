import numpy as np
import csv
import os
import pandas
import sys
import re

compilers = ['clang', 'gcc', 'icc']


def get_features_list():
    """
    Return dict (str 'feature_name' -> int 'feature_num')
    """
    features_dict = dict()
    features_list = \
    [
        'stack_size',
        'nop_ratio',
        'leaveq_ratio',
        'mov_ratio',
        'add_ratio',
        'inc_add_ratio',
        'shr_div_ratio'
    ]

    return features_list



def get_files_from_directory(dir_path):
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)

        if not os.path.isfile(file_path):
            continue
        else:
            yield file_path

# https://stackoverflow.com/questions/8625991/use-python-os-walk-to-identify-a-list-of-files
def fileList(source):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches

def write_csv(dir_path: str, feature_names: list[str], csv_name: str):
    """
    Create a csv file containing a feature vector for each file in dir_path
    """

    header = ['label'] + feature_names

    labels = compilers

    output_path = f'features/intuitive/{csv_name}.csv'

    with open(output_path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        # write the header
        writer.writerow(header)
        for file_path in fileList(dir_path):
            file_basename = os.path.basename(file_path)
            # Identify compiler / pie
            for l in labels:
                if '_' + l in file_basename:
                    label = l
                    break
            
            feature_vector = extract_features(file_path)

            writer.writerow([label] + feature_vector)

def is_instruction(line: str):
    return bool(re.search(r'[0-9a-f]+:\s', line))

def safe_div(num, denom):
    return  num / denom if denom else 0

def extract_features(file_path: str):
    """
    Extract interpretable features from given disassembly file
    """
    features_list = get_features_list()
    """
    features_list = \
    [
        'stack_size',
        'nop_ratio',
        'leaveq_ratio',
        'mov_ratio',
        'add_ratio',
        'inc_add_ratio',
        'shr_div_ratio'
    ]
    not on list:
        'num_zero_bytes',
        'instruction_length',
    """


    with open(file_path, 'r') as file:
        lines = [l for l in file.readlines() if is_instruction(l)]
        n = len(lines)

        num_stack_bytes = 0
        num_stack_instr = 0

        num_leaveq = 0
        num_add_rsp = 0

        num_zero_bytes = 0 
        
        # to-do?
        num_high_rsp_add = 0

        num_nops_strict = 0
        num_nops_total = 0

        num_mov = 0
        num_add = 0

        # inc_add_ratio
        num_inc = 0
        num_add_one = 0

        # shift_div_ratio
        num_shr = 0
        num_div = 0

        for line in lines:
            # stack_size
            instr = re.search(r'sub\s*\$0x[0-9a-f]+,%rsp', line)
            if instr:
                num_stack_instr += 1
                sub_instr = instr.group()
                num_bytes = int(sub_instr\
                    .lstrip(r'sub')\
                    .rstrip(r',%rsp')\
                    .strip()
                    .lstrip(r'$')
                    , 0
                )
                num_stack_bytes += num_bytes
            
            # leaveq
            if 'leaveq' in line:
                num_leaveq += 1
            if re.search(r'add.*%.*sp', line):
                num_add_rsp += 1

            # num_mov
            if 'mov' in line:
                num_mov += 1
            if 'add' in line:
                num_add += 1
            
            # nop_ratio
            if 'nop' in line:
                num_nops_total +=1
            if 'nop\n' in line:
                num_nops_strict += 1

            if 'inc' in line:
                num_inc += 1
            if re.search(r'add\s*[^-]0x1,', line):
                num_add_one += 1

            if re.search(r'\bshr', line):
                num_shr += 1
            if re.search(r'\bdiv', line):
                num_div += 1
        
        stack_size = safe_div(num_stack_bytes, num_stack_instr)
        nop_ratio = safe_div(num_nops_strict, num_nops_total)
        leaveq_ratio = safe_div(num_leaveq, num_add_rsp)
        mov_ratio = safe_div(num_mov, n)
        add_ratio = safe_div(num_add, n)
        inc_add_ratio = safe_div(num_inc, num_add_one)
        shr_div_ratio = safe_div(num_shr, num_div)

    features = [\
        stack_size,
        nop_ratio,
        leaveq_ratio,
        mov_ratio,
        add_ratio,
        inc_add_ratio,
        shr_div_ratio
    ]
    return features


def main():
    dir_path = sys.argv[1]
    csv_name = sys.argv[2]


    write_csv(dir_path, get_features_list() ,csv_name)




if __name__=='__main__':
    main()
            