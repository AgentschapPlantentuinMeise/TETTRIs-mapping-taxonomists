import numpy as np
import pandas as pd
import matplotlib.pyplot as plt # version 3.5.2
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, to_rgb
import fiona
import geopandas as gpd
import pickle
from itertools import groupby
from mpl_toolkits.axes_grid1 import make_axes_locatable


def freq_countries(df):
    # get list of countries with authors
    countries = list(df["inst_country_code"])
    # remove None values + alphabetical
    countries = sorted([i for i in countries if i is not None])
    
    # count how many of each group (country)
    freqs = [len(list(group)) for key, group in groupby(countries)]
    
    # link counts to country codes
    freqs_dict = {}
    for i, country in enumerate(sorted(set(countries))):
        freqs_dict[country] = freqs[i]

    return freqs_dict



newcmp = LinearSegmentedColormap.from_list("TETTRIs", [to_rgb('#78d3ac'), to_rgb('#05041d')], N=10)



# get worldmap 
def plot_country_freqs(freqs, map_path, europe=False, dpi=1200, relative=False):
    worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    worldmap = worldmap.to_crs("ESRI:54009") # Mollweide projection

    # convert 3-letter codes to 2-letter codes used for frequencies
    country_codes = pd.read_csv("../../data/external/country_codes.tsv", sep="\t")
    
    worldmap = worldmap.rename(columns={"iso_a3":"Alpha-3 code"})
    # fixing country codes in worldmap
    worldmap.at[43,"Alpha-3 code"] = "FRA"
    worldmap.at[21,"Alpha-3 code"] = "NOR"
    worldmap.at[174,"Alpha-3 code"] = "XKX"
    
    worldmap = pd.merge(worldmap, country_codes[["Alpha-2 code", "Alpha-3 code"]], 
                        on="Alpha-3 code", how="left")

    # add frequencies to worldmap
    worldmap["freq"] = worldmap["Alpha-2 code"].map(freqs)
    worldmap["freq"].fillna(0, inplace=True)
    worldmap.replace(0, np.nan, inplace=True)
    
    if relative:
        worldmap = worldmap.rename(columns={"freq":"absolute_freq"})
        # map percentage of country's population that are taxonomists
        worldmap["freq"] = worldmap["absolute_freq"]/worldmap["pop_est"]*100
            
    # plot frequencies
    if not europe:
        fig, ax = plt.subplots(1,1)

        ax.set_xticks([])
        ax.set_yticks([])
        
        divider = make_axes_locatable(ax) # make legend same size as plot
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        worldmap.plot(column='freq', ax=ax, legend=True,
                      missing_kwds={"color":"lightgrey"},
                      cax=cax,
                      cmap = newcmp)
        plt.savefig(map_path+".jpg", dpi=dpi)
    
    if europe:
        fig, ax = plt.subplots(1, 1)
        
        divider = make_axes_locatable(ax) # make legend same size as plot
        cax = divider.append_axes("right", size="5%", pad=0.1)
        
        # limit scope of map to europe
        minx, miny, maxx, maxy = [-1500000, 4000000, 4300000, 8500000]
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        ax.set_xticks([])
        ax.set_yticks([])

        plt.xticks([])
        plt.yticks([])
        
        if not relative:
            worldmap.plot(column='freq', ax=ax, legend=True,
                          missing_kwds={"color":"lightgrey"},
                          legend_kwds={"label":"number of taxonomists"},
                          cax=cax,
                          cmap = newcmp)
        else:
            worldmap.plot(column='freq', ax=ax, legend=True,
                          missing_kwds={"color":"lightgrey"}, 
                          legend_kwds={"label":"percentage of population"},
                          cax=cax,
                          cmap = newcmp)

        plt.tight_layout()  # Adjust padding
        plt.savefig(map_path+"_europe.jpg", dpi=dpi, bbox_inches="tight")


authors = pd.read_pickle("../../data/interim/single_authors_of_taxonomic_articles.pkl")

countries_freq = freq_countries(authors)
plot_country_freqs(countries_freq, "../../reports/figures/map_authors")

eu_authors = pd.read_pickle("../../data/interim/country_taxonomic_authors_no_duplicates.pkl")
countries_freq = freq_countries(eu_authors)
plot_country_freqs(countries_freq, "../../reports/figures/map_authors_europe", europe=True)
plot_country_freqs(countries_freq, "../../reports/figures/map_authors_europe_relative", europe=True,
                   relative=True) 

eujot_freq = freq_countries(eu_authors[eu_authors["source_issn_l"]=="2118-9773"])
plot_country_freqs(eujot_freq, "../../reports/figures/map_eujot", europe=True)
plot_country_freqs(eujot_freq, "../../reports/figures/map_eujot_relative", europe=True, relative=True)

print("Authors' institutions plotted onto world maps. Results in reports/figures.")
