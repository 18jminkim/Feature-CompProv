import utils
import sys
import re
import utils
import subprocess


def get_header_arm64():
    return ['label', 'prologue_stp', 'epilogue_ldp']


def get_header_mips64():
    return ['label', 'sp_alloc_fifo', 'sp_alloc_filo']


def get_prologue_matches_arm64(objdump: str):
    return len(re.findall(r'[0-9a-f]+ <.*>:\n.*stp	x29, x30,', objdump))


def count_matches(regex: str, word: str):
    return len(re.findall(regex, word))


def get_feature_arm64(file_path: str):
    objdump = subprocess.getoutput(f'{utils.objdump_path} -D -j .text {file_path}')

    num_functions = len(re.findall(r'[0-9a-f]+ <.*>:', objdump))
    prologue_match_ratio = get_prologue_matches_arm64(objdump) / num_functions

    epilogue_match_ratio = count_matches(r'ldp	x29, x30,.*\n.*ret', objdump) / num_functions


    return [prologue_match_ratio, epilogue_match_ratio]

def is_filo_alloc_mips64(fucntion_slice: str, prologue_len=20, epilogue_len=20):
    lines = [l.strip() for l in fucntion_slice.split('\n')][1:]
    prologue_sd = list()
    epilogue_ld = list()
    
    if len(lines) < prologue_len + epilogue_len:
        return 0, 0

    
    
    for i in range(prologue_len):
        if re.search(r'\ssd\s[0-9a-z]+,[0-9]+\(sp\)', lines[i]):
            chunk = lines[i].split()[-1]
            sep = chunk.index(',')
            operand = chunk[:sep]
            prologue_sd.append(operand)

    if len(prologue_sd) < 2:
        return 0, 0

    for i in range(epilogue_len):
        if re.search(r'\sld\s[0-9a-z]+,[0-9]+\(sp\)', lines[-i]):
            chunk = lines[-i].split()[-1]
            sep = chunk.index(',')
            operand = chunk[:sep]
            epilogue_ld.append(operand)

    if prologue_sd == epilogue_ld:
        return -1, 1
    elif len(prologue_sd) == len(epilogue_ld):
        return 1, 1
    else:
        return 0, 0


def get_feature_mips64(file_path: str):
    objdump = subprocess.getoutput(f'{utils.objdump_path} -D -j .text {file_path}')
    fep_list = list(re.finditer(r'[0-9a-f]+ <.*>:', objdump))

    num_valid = 0

    sp_alloc_fifo = 0
    sp_alloc_filo = 0

    for idx, fep in enumerate(fep_list):
        function_start = fep.start()
        if idx < len(fep_list) - 1:
            function_end = re.search(r'\n\n', objdump[function_start:]).start() + function_start
        else:
            function_end = -1

        
        fucntion_slice = objdump[function_start:function_end]

        score, valid = is_filo_alloc_mips64(fucntion_slice, 10, 10)
        
        if score > 0:
            sp_alloc_fifo += 1
        elif score < 0:
            sp_alloc_filo += 1
        num_valid += valid
    
    return [utils.safe_div(sp_alloc_fifo, 1), utils.safe_div(sp_alloc_filo, 1)]


def function_order(file_path: str):
    objdump = subprocess.getoutput(f'{utils.objdump_path} -D -j .text {file_path}')
    feps = utils.get_feps(objdump)

    for fep in feps:
        line = objdump[fep.start():].split('\n')[0]
        # print(line)
        func_name_start = line.index('<') + 1
        func_name_end = line.index('>')
        func_name = line[func_name_start:func_name_end]

        print(func_name)



    print(len(feps))




def main():
    file_path = sys.argv[1]


if __name__ == '__main__':
    main()