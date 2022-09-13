import os
import re
import csv
import numpy as np


"""
Various utility functions and parameters to be used by multiple programs
"""


objdump_path = 'objdump/objdump'


# https://stackoverflow.com/questions/8625991/use-python-os-walk-to-identify-a-list-of-files
def get_file_paths(dir_path):
    matches = []
    for root, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            matches.append(os.path.join(root, filename))
    return matches


def is_instruction(line: str):
    return bool(re.search(r'\s+[0-9a-f]+:\s', line))


def safe_div(num, denom):
    return  num / denom if denom else 0


def get_feps(disassembly: str):
    return list(re.finditer(r'[0-9a-f]+ <.*>:', disassembly))


def filter_files(file_list: list[str], include_filters, exclude_filters):
    filtered = set()
    exclude = set()
    for file_path in file_list:
        file_name = os.path.basename(file_path)

        for include_query in include_filters:
            if re.search(include_query, file_name):
                filtered.add(file_path)
        
        for i in range(len(exclude_filters)):
            if re.search(exclude_filters[i], file_name):
                exclude.add(file_path)
        
    for file_path in file_list:
        if file_path not in exclude:
            filtered.add(file_path)

    return list(filtered)


def write_csv(\
    dir_path: str,
    header: list[str], 
    feature_function, 
    csv_name: str, 
    labels: list[str]=['clang', 'gcc', 'icc'], 
    kind: str=None,
    include_filters=[],
    exclude_filters=[]
    ):
    """
    Create a csv file containing a feature vector for each file in dir_path
    """
    if kind:
        output_path = f'features/{kind}/{csv_name}.csv'
    else:
        output_path = f'features/{csv_name}.csv'
    print(f'Writing CSV at {output_path}...')


    with open(output_path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        # write the header
        writer.writerow(header)

        files_list = filter_files(
            get_file_paths(dir_path), 
            include_filters, 
            exclude_filters
        )

        num_files = len(files_list)
        stats = np.zeros((num_files, len(header) - 1))

        for idx, file_path in enumerate(files_list):
            print(f'{idx+1}/{num_files}  {file_path}')
            file_basename = os.path.basename(file_path)
            # Identify ground truth from name
            for l in labels:
                if '_' + l in file_basename:
                    label = l
                    break
            
            feature_vector = feature_function(file_path)

            stats[idx] += np.array(feature_vector)

            row = [label] + feature_vector

            writer.writerow(row)
            print(row)
    
    features = header[:]
    features.remove('label')

    print(f'Finished writing on {output_path}')
    print('Features')
    print(f'{features}')
    print('Mean')
    print(np.mean(stats, axis=0))
    print('Standard Deviation')
    print(np.std(stats, axis=0))