import os
import sys
import re
import subprocess
import utils


compilers = ['clang', 'gcc', 'icc']
# List of reg expressions to exclude / include matches
include_filters = []
exclude_filters = []
indicator_sections = [\
    '.data.rel.ro', 
    '.hash',
    '.init',
    '.init_array',
    '.note.gnu.build-i',
    '.rela.dyn',
    'rela.plt',
    '.tm_clone_table'
]


# np.set_printoptions(suppress=True)
def get_feature_names():
    """
    Return list of str 'nop type'
    """
    features_list = \
    [
        'nop_total',
        '1B_R',
        '2B_R',
        '3B_R',
        '4B_R',
        '5B_R',
        '6B_R',
        '7B_R',
        '8B_R',
        '9B_R',
        '10B_V',
        '11B_V',
        '12B_V',
        '13B_V',
        '14B_V',
        '15B_V',
        'OTHERS'
    ]

    return features_list


def get_standard_nops():
    nops = \
    [
        # Recommended nops
        '90',
        '66 90',
        '0F 1F 00',
        '0F 1F 40 00',
        '0F 1F 44 00 00',
        '66 0F 1F 44 00 00',
        '0F 1F 80 00 00 00 00',
        '0F 1F 84 00 00 00 00 00',
        '66 0F 1F 84 00 00 00 00 00',
        # Non-documented nops
        '66 2e 0f 1f 84 00 00 00 00 00',
        '66 66 2e 0f 1f 84 00 00 00 00 00',
        '66 66 66 2e 0f 1f 84 00 00 00 00 00',
        '66 66 66 66 2e 0f 1f 84 00 00 00 00 00',
        '66 66 66 66 66 2e 0f 1f 84 00 00 00 00 00',
        '66 66 66 66 66 66 2e 0f 1f 84 00 00 00 00 00'
    ]
    return [n.lower() for n in nops]


def get_header():
    return ['label'] + get_feature_names()


def filter_files(file_list: list[str]):
    filtered = set()
    exclude = set()
    for file_path in file_list:
        file_name = os.path.basename(file_path)

        for include_query in include_filters:
            if re.search(include_query, file_name):
                filtered.add(file_path)
        
        for i in range(len(exclude_filters)):
            if re.search(exclude_filters[i], file_name):
                print(f'{file_name}\t{exclude_filters[i]}\t{re.search(exclude_filters[i], file_name)}')
                exclude.add(file_path)
        
    for file_path in file_list:
        if file_path not in exclude:
            filtered.add(file_path)
    
    return list(filtered)


def is_instruction(line: str):
    return bool(re.search(r'[0-9a-f]+:\s', line))


def safe_div(num, denom):
    return  num / denom if denom else 0


def get_instruction_bytes(line: str, opcode_position: int):
    """Extract instruction bytes from line"""
    left_bound = line.index(':') + 1
    return line[left_bound : opcode_position].strip()


def get_assembly(line:str, opcode_position):
    return line[opcode_position:].strip()


def get_opcode_position(lines: list[str]):
    for line in lines:
        if '\tmov' not in line:
            continue
        return line.index('\tmov') + 1


def count_nops_in_file(file_path: str):
    """
    Extract nop features from a file
    """
    standard_nops = get_standard_nops()
    # Counts standard nops + other nops
    nop_counts = [0] * (len(standard_nops) + 1)
    # Final output
    nop_features = list()
    # Record for display
    nop_records = dict()

    print(file_path)
    with open(file_path) as file:

        objdump = subprocess.getoutput(f'{utils.objdump_path} -D -j .text {file_path}')
        objdump_lines = objdump.split('\n')

        lines = [l for l in objdump_lines if is_instruction(l)]

        opcode_position = get_opcode_position(lines)

        def add_record(instruction_bytes, line):
            if instruction_bytes not in nop_records.keys():
                assembly = get_assembly(line, opcode_position)
                nop_records[instruction_bytes] = [assembly, 0]
            nop_records[instruction_bytes][1] += 1

        for i in range(len(lines)):
            instruction_bytes = get_instruction_bytes(lines[i], opcode_position)

            # Extended line
            offset = 1
            while i + offset < len(lines) and len(lines[i + offset]) < opcode_position + 1:
                instruction_bytes += ' ' + get_instruction_bytes(lines[i + offset], opcode_position)
                offset += 1
            
            # Standard nop found
            if instruction_bytes in standard_nops:
                nop_counts[standard_nops.index(instruction_bytes)] += 1
                add_record(instruction_bytes, lines[i])
            # Non-standard nop found
            elif re.search(r'\snop', lines[i]):
                print('Alert: non-standard NOP found.')
                nop_counts[-1] += 1
                print(instruction_bytes)
                print(get_assembly(lines[i], opcode_position))
                add_record(instruction_bytes, lines[i])
                # return []

    nop_ratio = sum(nop_counts) / len(lines)
    nop_counts = [safe_div(i, sum(nop_counts)) for i in nop_counts]
    nop_features = [nop_ratio] + nop_counts

    return nop_features, nop_records


def count_nops(dir_path: str):
    # str "0x90" -> int number of occurrences
    nop_counts = dict()

    for file_path in utils.get_file_paths(dir_path):
        print(file_path)
        with open(file_path) as file:

            lines = [l for l in file.readlines() if is_instruction(l)]
            # print(f'{len(lines)} lines')

            for i in range(len(lines)):
                if re.search(r'\snop[lw\n]', lines[i]):
                    instruction_bytes = get_instruction_bytes(lines[i], False)

                    # Extended line
                    if i < len(lines) - 1 and len(lines[i + 1]) < 30:
                        # print(lines[i + 1])
                        instruction_bytes += ' ' + get_instruction_bytes(lines[i + 1], True)

                    if instruction_bytes not in nop_counts.keys():
                        assembly = get_assembly(lines[i])
                        nop_counts[instruction_bytes] = [assembly, 0]

                    nop_counts[instruction_bytes][1] += 1

    for key in sorted(nop_counts.keys(), key=len):
        # print(key + '\t' + str(nop_counts[key])) 
        print(f'{len(key.split(" "))}B\t{key}\t{nop_counts[key]}')   


def get_feature_vector(file_path: str):
    nop_feature_vector, nop_record = count_nops_in_file(file_path)
    
    return nop_feature_vector


def main():
    dir_path = sys.argv[1]
    csv_name = sys.argv[2]
    
    for f in utils.get_file_paths(dir_path):
        print(get_feature_vector(f))


if __name__=='__main__':
    main()
            