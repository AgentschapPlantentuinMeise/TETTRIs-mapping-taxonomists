import pandas as pd
import numpy as np
import pickle
#import prep_taxonomy
from tqdm import tqdm  # Import tqdm for the progress bar


backbone = pd.read_csv("../../data/external/backbone/Taxon.tsv", sep="\t", on_bad_lines='skip', low_memory=False)
print("backbone loaded")
backbone = backbone[backbone["taxonRank"]=="species"]
# drop species with no canonical name
backbone = backbone.dropna(subset="canonicalName").set_index("canonicalName")
print("species dropped with no canonical name")
# and no full taxonomic lineage to the family
#backbone = backbone.dropna(subset=['kingdom', 'phylum', 'class', 'order', 'family'])
backbone = backbone[['taxonomicStatus', 'taxonID', 'acceptedNameUsageID',
                     'kingdom', 'phylum', 'class', 'order', 'family', 'genus']]
print("backbone updated")

backbone["numberOfAuthors"] = [0,]*len(backbone.index)


# get disambiguated, European authors of taxonomic articles
authors = pd.read_pickle("../../data/processed/authors_disambiguated_truncated.pkl")
print("authors loaded")

# link the author's expertise to the taxonomic backbone
available_species = set(backbone.index)
print("author's expertise linked to the taxonomic backbone")

# Progress bar for the loop that links author expertise
for subjects in tqdm(authors["species_subject"], desc="Processing species subjects"):
    if len(subjects) != 0: 
        for species in subjects:
            if species in available_species:
                backbone.loc[species, "numberOfAuthors"] += 1
print("counting finished")

# Progress bar for propagating synonyms
for row in tqdm(backbone.itertuples(), total=len(backbone), desc="Propagating synonyms"):
    if row.taxonomicStatus == "synonym":
        backbone.loc[backbone["taxonID"] == row.acceptedNameUsageID, "numberOfAuthors"] += row.numberOfAuthors
        backbone.drop(index=row.Index)
print("synonyms propagated")

backbone.to_pickle("../../data/processed/backbone_with_author_counts.pkl")
print("backbone_with_author_counts.pkl produced")
backbone.to_csv("../../data/processed/backbone_with_author_counts.tsv", sep="\t")
print("backbone_with_author_counts.tsv produced")
