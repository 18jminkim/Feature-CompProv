import numpy as np
import tensorflow_decision_forests as tfdf
import pandas
import sys
import os

"""
Train a simple random-forest model with .csv file created by preprocess.py

Usage:

$ python train.py {features_path}

features_path: path of the .csv file created by preprocess.py
"""

# {method} holds the name of the feature being used to train
method = 'misc'
# Dataset will be split into (1 - {test_ratio}) : test_ratio
# which will be trained and evaluated respectively
test_ratio = 0.95




# Split the dataset into a training and a testing dataset.
def split_dataset(dataset, test_ratio=0.10):
  """Splits a panda dataframe in two."""
  test_indices = np.random.rand(len(dataset)) < test_ratio
  return dataset[~test_indices], dataset[test_indices]


def train(features_path):

  print(features_path)
  # Extract features of test set if not already present
  feature_basename = os.path.basename(features_path).split('.')[0]

  dataset_df = pandas.read_csv(features_path)

  # Split dataset
  train_ds_pd, test_ds_pd = split_dataset(dataset_df, test_ratio=test_ratio)

  label = 'label'
  train_ds = tfdf.keras.pd_dataframe_to_tf_dataset(train_ds_pd, label=label)
  test_ds = tfdf.keras.pd_dataframe_to_tf_dataset(test_ds_pd, label=label)

  model = tfdf.keras.RandomForestModel()

  model.fit(train_ds)
  model.compile(metrics=["accuracy"])
  save_path = f'models/{method}/{feature_basename}'
  model.save(save_path, overwrite=True)

  print(model.summary())
  print(f'Saved model at {save_path}')

  # Evaluate
  evaluation = model.evaluate(test_ds, return_dict=True)
  print("{} examples in training, {} examples for testing.".format(
    len(train_ds_pd), len(test_ds_pd)))
  for name, value in evaluation.items():
    print(f"{name}: {value:.4f}")


if __name__ == "__main__":
    features_path = sys.argv[1]
    train(features_path)