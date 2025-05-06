"""
test_box_plot.py
"""

import random

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generate_dataset(n):
    return [random.randint(1, 1000) for _ in range(n)]


def test_box_plot():
    data = {
        'split': ['train'] * 50 + ['test'] * 50 + ['validation'] * 50,
        'word_count': generate_dataset(150)
    }
    df = pd.DataFrame(data)

    # Set the aesthetic style of the plots
    sns.set_style("whitegrid")

    # Create a box plot
    plt.figure(figsize=(10, 6))  # Adjust the size of the figure
    sns.boxplot(x='split', y='word_count', data=df)

    # Adding title and labels
    plt.title('Distribution of Word Counts Across Data Splits')
    plt.xlabel('Data Split')
    plt.ylabel('Word Count')

    # Show the plot
    plt.show()
