import seaborn as sns
import pandas as pd
import sys


"""
Plot distribution of each feature of data with respect to its label

Usage:

$ python plot_features.py {csv_path}

csv_name: path of the .csv file created by preprocess.py

Plots are stored in features/plots/ directory
"""


csv_path = sys.argv[1]


print("Seaborn version : ", sns.__version__)
sns.set()
sns.set_style('whitegrid')
sns.set_color_codes()

current_palette = sns.color_palette()
sns.palplot(current_palette)

df = pd.read_csv(csv_path)


for idx, col in enumerate(list(df.columns)):
    if idx in [0]:
        continue
    print(col)
    plot = sns.catplot(x='label', y=col, kind="swarm", s=1, data=df)
    fig = plot.fig
    fig.savefig(f"features/plots/{col}.png") 

