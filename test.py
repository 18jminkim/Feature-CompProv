import numpy as np
import tensorflow_decision_forests as tfdf
import pandas
import tensorflow
import os
import sys
import csv


"""
Test a trained model with given test dataset

Usage:

$ python test.py {model_path} {test_path}

model_path: path of the model trained and saved by train.py
test_path: path of the .csv file created by preprocess.py
"""


# Write compilers of interest here
labels = ['clang', 'gcc', 'icc']


def get_files_from_directory(dir_path):
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)

        if not os.path.isfile(file_path):
            continue
        else:
            yield file_path


def get_expected(features_path):
    """
    Get ground truth labels from each vector in features list
    """
    with open(features_path, newline='') as file:
        reader = csv.reader(file)
        expected = list()
        # Skip header
        next(reader, None)

        for row in reader:
            expected.append(labels.index(row[0]))

    return expected


def print_accuracy(expected, prediction):

    # Binary classification
    if prediction.shape[1] < 2:
        predicted_labels = np.round(prediction)
    # Multi-class
    else:
        predicted_labels = np.argmax(prediction, axis=1)
        
    correct = 0
    total = len(expected)

    for i in range(total):
        if expected[i] == predicted_labels[i]:
            correct += 1
    
    print(f'Test accuracy:\t{correct / total}\t({correct} / {total})')


def test(model_path, test_path):
    
    # Load model
    model: tfdf.keras.RandomForestModel = \
        tensorflow.keras.models.load_model(model_path)

    # Load test dataset from csv
    test_df = pandas.read_csv(test_path)
    test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test_df, label='label')

    # Get ground truth
    expected = get_expected(test_path)

    # Predict from model
    prediction = model.predict(test_ds)
    for p in prediction:
        print(p)
    print_accuracy(expected, prediction)
    

if __name__ == "__main__":
    model_path = sys.argv[1]
    test_path = sys.argv[2]
    test(model_path, test_path)
