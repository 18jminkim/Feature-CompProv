import utils
import numpy as np
import sys
import re
import os

dir_path = sys.argv[1]
compilers = ['clang', 'gcc', 'icc']

def count_opcode_in_file(opcode: str, file_path: str):
    opcode_count = 0
    with open(file_path, 'r') as file:

        lines = [i for i in file.readlines() if utils.is_instruction(i)]
        for l in lines:
            if re.search(opcode, l):
                opcode_count += 1
    
    return opcode_count, len(lines)

def count_opcode_in_dir(opcode: str, dir_path: str):
    count_sum = 0
    file_paths = utils.get_file_paths(dir_path)
    for file_path in file_paths:
        print(file_path)
        count_sum += count_opcode_in_file(opcode, file_path)
    
    return count_sum, len(file_paths)

def count_opcode_by_compiler(opcode: str, dir_path: str):
    freq_dict = dict()
    num_files_dict = dict()

    for c in compilers:
        freq_dict[c] = list()
        num_files_dict[c] = 0

    file_paths = utils.get_file_paths(dir_path)
    for file_path in file_paths:
        print(file_path)
        file_basename = os.path.basename(file_path)

        for c in compilers:
            if c in file_basename:
                comp  = c

        count, num_lines = count_opcode_in_file(opcode, file_path)

        freq_dict[comp].append(count / num_lines)
        num_files_dict[comp] += 1
    
    results = dict()
    for c in compilers:
        freq_array = np.array(freq_dict[c])
        mean = np.mean(freq_array)
        var = np.std(freq_array)
        results[c] = (mean, var)
    
    return results


mov_stats = count_opcode_by_compiler(r'\smov', dir_path)
add_stats = count_opcode_by_compiler(r'\sadd', dir_path)


print("mov:")
for key in mov_stats.keys():
    print(f'{key}: {mov_stats[key]}')

print("add:")
for key in add_stats.keys():
    print(f'{key}: {add_stats[key]}')
