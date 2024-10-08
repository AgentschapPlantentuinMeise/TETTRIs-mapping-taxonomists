import pandas as pd
import numpy as np
#import pickle
#import time
from matplotlib import pyplot as plt
from operator import add


first_names = pd.read_csv("../../data/processed/gender_per_author.tsv", sep="\t")

def plot_gender_balance(first_names, title, filename, start_year=1953):
    male = []
    female = []
    inconclusive = []

    for year in range(start_year,2023):
        counts = first_names[first_names["publication_year"]==year]["gender"].value_counts()

        male.append(counts["male"])
        female.append(counts["female"])
        inconclusive.append(counts["inconclusive"])

    fig, ax = plt.subplots()
    
    plt.title(title)
    ax.bar(range(start_year,2023), male, label="male", color="blue")
    ax.bar(range(start_year,2023), female, label="female", color="red", bottom=male)
    ax.bar(range(start_year,2023), inconclusive, label="inconclusive", color="grey", 
           bottom=list(map(add, male, female)))
    ax.legend()

    plt.savefig(filename)

    
plot_gender_balance(first_names,
                    "Gender balance of taxonomists",
                    "../../reports/figures/gender_balance.png",
                    start_year=2013)


def plot_gender_balance_percentage(first_names, title, filename, start_year=1973):
    male = []
    female = []
    inconclusive = []

    for year in range(start_year,2023):
        counts = first_names[first_names["publication_year"]==year]["gender"].value_counts()
        male.append(counts["male"])
        female.append(counts["female"])
        inconclusive.append(counts["inconclusive"])
    
    total = list(map(add, male, female)) # in two steps because map can only add two lists at a time
    total = list(map(add, total, inconclusive))
    
    male_perc = np.divide(male, total)
    female_perc = np.divide(female, total)
    inc_perc = np.divide(inconclusive, total)
    
    fig, ax = plt.subplots()

    plt.title(title)
    ax.bar(range(start_year,2023), female_perc, label="female", color="blue")
    ax.bar(range(start_year,2023), male_perc, label="male", color="red", bottom=female_perc)
    ax.bar(range(start_year,2023), inc_perc, label="inconclusive", color="grey", bottom=female_perc+male_perc)
    ax.legend()

    plt.savefig(filename)

plot_gender_balance_percentage(first_names, 
                               "Gender balance of taxonomists",
                               "../../reports/figures/gender_percentages.png")
