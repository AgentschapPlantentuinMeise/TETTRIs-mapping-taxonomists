import pandas as pd
import matplotlib.pyplot as plt

# Load datasets
articles = pd.read_pickle("../../data/processed/taxonomic_articles_with_subjects.pkl")
backbone = pd.read_csv("../../data/external/backbone/Taxon.tsv", sep="\t", on_bad_lines='skip', low_memory=False)

# Reduce the size of backbone for easier searching
backbone = backbone[backbone["taxonomicStatus"] != "doubtful"]
backbone = backbone[["canonicalName", "family"]]
# Remove taxa with no known species name or family
backbone = backbone.dropna().drop_duplicates(ignore_index=True).reset_index(drop=True)

## Link Articles to Taxonomic Backbone
articles["families"] = [list() for _ in range(len(articles.index))]

# Create a dictionary for quick family lookups
seen_species = {}

for species in backbone.itertuples():
    if species.canonicalName not in seen_species:
        seen_species[species.canonicalName] = species.family

# For each article, find families based on species
for i, article in articles.iterrows():
    for species in article["species_subject"]:
        if species in seen_species:
            family_name = seen_species[species]
            if family_name not in article["families"]:
                articles.at[i, "families"].append(family_name)

# Count occurrences of each family across all articles
family_counts = {}

for fam_list in articles["families"]:
    for family in fam_list:
        if family in family_counts:
            family_counts[family] += 1
        else:
            family_counts[family] = 1  # Start from 1

# Create Histogram with Formatting Adjustments
plt.clf()  # Clear the current figure
fig, ax = plt.subplots()

ax.hist(family_counts.values(), bins=50, range=(0, 50))
ax.set_xlabel("Articles", fontsize=20)
ax.set_ylabel("Families (%)", fontsize=20)
ax.tick_params(axis='y', labelsize=14)
ax.tick_params(axis='x', labelsize=14)

# If you have a legend to add:
#ax.legend(["Family Distribution"], loc="lower left", fontsize=16)

#plt.title("Histogram of Articles per Family", fontsize=20)
plt.tight_layout()  # Ensure everything fits well
plt.savefig("../../reports/figures/histogram_families.png")
plt.show()

# Print the Top 10 Families
top_10_families = sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:10]
print("Top 10 Families by Number of Articles:")
for family, count in top_10_families:
    print(f"{family}: {count} articles")
