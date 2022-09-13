import sys
import re
import subprocess
import utils



compilers = ['clang', 'gcc', 'icc']

def list_sections_in_elf(readelf: str):

    lines = readelf.split('\n')
    sections = list()

    for l in lines:
        if not re.search(r'\[\s*[0-9]*\]', l):
            continue
        
        lstrip_idx = l.index(']')
        l = l[lstrip_idx + 1: ]
        section = l.split()[0]
        sections.append(section)
    
    return sections


def get_section_statistics(dir_path: str, compiler: str):
    stats = dict()

    def add_stats(sections: list[str]):
        for section in sections:
            if section not in stats.keys():
                stats[section] = 0
            stats[section] += 1
            
    file_paths = utils.get_file_paths(dir_path)
    for path in file_paths:
        if compiler not in path:
            continue

        readelf = subprocess.getoutput(f'readelf -S {path}')
        sections = list_sections_in_elf(readelf)

        add_stats(sections)
    
    return stats


def list_sections_in_dir(dir_path: str):
    file_paths = utils.get_file_paths(dir_path)
    sections = set()
    for path in file_paths:
        readelf = subprocess.getoutput(f'readelf -S {path}')
        file_sections = list_sections_in_elf(readelf)
        
        for fs in file_sections:
            sections.add(fs)

    # Remove debugging sections
    for sec in sections.copy():
        if 'debug' in sec:
            sections.remove(sec)
    
    return sorted(list(sections))


def get_feature_vector(file_path: str, sections: list[str]):
    feature_vector = list()
    readelf = subprocess.getoutput(f'readelf -S {file_path}')
    # print(readelf)
    file_sections = list_sections_in_elf(readelf)
    # print(file_sections)

    for sec in sections:
        if sec in file_sections:
            feature_vector.append(1)
        else:
            feature_vector.append(0)
    
    return feature_vector


def main(dir_path: str):
    stats_list = list()
    all_sections = set()

    for comp in compilers:
        stats = get_section_statistics(dir_path, comp)
        stats_list.append(stats)

        for key in stats.keys():
            if 'debug' not in key:
                all_sections.add(key)

    print(f'{"Section":<20}{compilers[0]:<10}{compilers[1]:<10}{compilers[2]}')

    for section in sorted(list(all_sections)):
        print(f'{section:<20}', end='')
        for stats in stats_list:
            if section in stats.keys():
                print(f'{stats[section]:<10}', end='')
            else:
                print(f'{0:<10}', end='')
        print()



if __name__ == "__main__":
    dir_path = sys.argv[1]
    main(dir_path)

