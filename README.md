# Feature-CompProv

+ Feature-CompProv is a simple compiler provenance project using human-interpretable, intuitive features.
+ Features from elf binaries are extracted to be fed into 
a basic Tensorflow Decision Tree model as training data.
+ Please refer to the PDF file in `slides` directory for further details.


## Requirements

+ Please see `requirements.txt` for all required packages.


## Preprocess

+ IMPORTANT: Every ELF file for preprocessing must include its ground-truth compiler name
in its file name.
    ex) `binutils-2.31.1_x64_clang_nopie_o0_addr2line`, 
        `coreutils-8.30_x64_icc_pie_os_sleep`

+ Run the preprocess script `preprocess.py`:
  ```bash
  python preprocess.fsx {{dir_path}} {{csv_name}}
  ```
+ Features are stored as .csv files in `features` directory with name `{{csv_name}}.csv`.


## Train

+ Run the train script `train.py`:
  ```bash
  python train.py {{features_path}}.
  ```
  where `{{features_path}}` is the path to the .csv file obtained from  `preprocess.py`.


## Test

+ Run the test script `test.py`:
  ```bash
  python test.py {{model_path}} {{test_path}}
  ```
  where
  + `{{model_path}}` is the path of the model stored by `train.py`,
  + `{{test_path}}` is the path of the .csv file created by `preprocess.py` for testing the model.


## Credits

+ This project was guided and advised by SoftSec Lab, KAIST.
  https://github.com/SoftSec-KAIST