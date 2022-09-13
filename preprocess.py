import sys
import utils

import nop_features_x64
import prologue_epilogue
import list_sections


"""
Extract features from the ELF files in a given directory
Store the dataset as a .csv file

Usage:

$ python preprocess.py {dir_path} {csv_name}

dir_path: path of the directory containing the ELF files
csv_name: name of the .csv file that will be created
"""

dir_path = sys.argv[1]
csv_name = sys.argv[2]


#########
# OPTIONAL PARAMETERS
# List of reg expressions to exclude / include matches
include_filters = []
exclude_filters = []

labels = ['clang', 'gcc', 'icc']
kind = 'misc'
##########



"""
Feature function & header definition

Select a feature type from the following:
- nop_features_x64: 
    classifies compiler by 
    analyzing various types of nop instructions in .text section
    (only available in x86_64)
- list_sections:
    observes presence / absence of ELF sections to classify compiler
- prologue_epilogue:
    observes characteristics in function prologue & epilogues
    by disassembling the .text section


Uncomment the lines below the desired feature type,
and comment out all other feature types
to define {feature_function} and {header} parameters.
"""

# list_sections
# sections = list_sections.list_sections_in_dir(dir_path)
# print(sections)
# feature_function = lambda x: list_sections.get_feature_vector(x, sections=sections)
# header = ['label'] + sections


# nop_features_x64
# feature_function = nop_features_x64.get_feature_vector
# header = nop_features_x64.get_header()


# Prologue & epilogue
# arm64
# feature_function = prologue_epilogue.get_feature_arm64
# header = prologue_epilogue.get_header_arm64()


# mips64 (mipseb64)
feature_function = prologue_epilogue.get_feature_mips64
header = prologue_epilogue.get_header_mips64()



utils.write_csv(\
    dir_path, 
    header, 
    feature_function, 
    csv_name, 
    labels=labels,
    kind=kind
)