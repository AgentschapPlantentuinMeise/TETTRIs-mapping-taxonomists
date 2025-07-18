# get all European taxonomic articles from taxonomic journals
import pandas as pd
import glob
import os
# custom packages
import download
import prep_articles
import json
from datetime import datetime
from pathlib import Path
import sys
import time

def ts(msg):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}")
    
ts("Entered get_articles.py")



print("=== get_articles.py started ===")

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# === Path setup ===
this_dir = Path(__file__).resolve().parent
root_dir = this_dir.parents[1]  # Adjust if needed

config_path = root_dir / "config" / "config.json"

ts(f"Resolved config path: {config_path}")

journals_path = root_dir / "data" / "processed" / "journals.csv"
articles_dir = root_dir / "data" / "raw" / "articles"
interim_dir = root_dir / "data" / "interim" / "keyword-filtered_articles"
raw_dir = root_dir / "data" / "raw" / "articles"

interim_dir.mkdir(parents=True, exist_ok=True)

# === Load configuration ===
if not config_path.exists():
    raise FileNotFoundError(f"Config file not found at {config_path}")

ts("Loading config...")

with open(config_path, "r", encoding="utf-8") as config_file:
    config = json.load(config_file)
    
ts("Config loaded")
    
# Extract dates
from_date = config.get("from_date", "2014-01-01")  # Default to 2014-01-01 if not provided
to_date = config.get("to_date", "2023-12-31")      # Default to 2023-12-31 if not provided

if not validate_date(from_date) or not validate_date(to_date):
    raise ValueError("Invalid date format in configuration. Use YYYY-MM-DD.")

print("From ="+from_date+" To ="+to_date)
      
journals = pd.read_csv(journals_path)
if journals is None:
    raise ValueError("No journals were loaded — check input files or download step.")

# clear directory
articles_dir.mkdir(parents=True, exist_ok=True)
files = glob.glob(str(articles_dir / "*"))
#files.extend(glob.glob("../../data/interim/eu_keyword-filtered_articles/*"))
for f in files:
    os.remove(f)

# ask OpenAlex (nicely) for all articles from these journals from 2014-2023
# can only use journals that have OpenAlex IDs and that are not dissolved
oaids = list(set(journals[journals["dissolved"]!=True]["openAlexID"]))
#email = input("Enter e-mail address for OpenAlex API: ")
email = config.get("email")

if not email:
    raise ValueError("Email address for OpenAlex API is missing in config.json")
print("using email: "+email)

articles = []
n = 0; m = 0

ts("About to request PLOS ONE articles")
print("Requesting PLOS ONE articles from OpenAlex...")

# deal with PLOS ONE now
#plosone_articles = download.request_works("primary_location.source.id:S202381698", email, to_date="2023-12-31")

plosone_articles = download.request_works(
    "primary_location.source.id:S202381698",
    email,
    to_date="2023-12-31"
)
print(f"Retrieved {len(plosone_articles)} PLOS ONE articles")
print(f"[DEBUG] Raw PLOS ONE articles returned: {len(plosone_articles)}")

filtered_articles = prep_articles.filter_keywords(plosone_articles, config=config)

print(f"[DEBUG] Articles after keyword filtering: {len(filtered_articles)}")

if filtered_articles is None or filtered_articles.empty:
    raise ValueError("No PLOS ONE articles were loaded — possibly none matched after filtering.")

for i in range(10):
    print(f"Still working... {i}")
    time.sleep(5)
    
print(f"[DEBUG] Articles returned: {len(filtered_articles)}")

filtered_articles = prep_articles.filter_by_domain(filtered_articles, domain_id="https://openalex.org/domains/1")

if filtered_articles.empty:
    print("[WARNING] Filtered PLOS ONE articles are empty — nothing to save!")
else:
    save_path = interim_dir / f"articles{m}.pkl"
    interim_dir.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Saving {len(filtered_articles)} filtered articles to {save_path}")
    filtered_articles.to_pickle(save_path)
    
#filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/articles"+str(m)+".pkl")
print(f"[DEBUG] Saving {len(filtered_articles)} articles to: {interim_dir / f'articles{m}.pkl'}")
filtered_articles.to_pickle(interim_dir / f"articles{m}.pkl")
#eu_articles = prep_articles.filter_eu_articles(filtered_articles)
#eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
m += 1

# download recent articles from every taxonomic journal
for oaid in oaids:
    #print(f"Processing journal: {oaid}")
    #for i in range(10):
    #    print(f"Still working... {i}")
    #    time.sleep(5)
    if oaid != oaid: # check if nan
        continue
    if oaid == "S202381698": # dealt with PLOS ONE separately
        continue # (returns ~240 000 articles)
    
    # search by confirmed OpenAlex ID (from OpenAlex itself or Wikidata) 
    journal_articles = download.request_works("primary_location.source.id:"+oaid, email, 
                                              from_date=from_date, to_date=to_date)
    n += len(journal_articles)
    articles.append(journal_articles)
    
    # split the dataframe every 10 000 articles
    if n >= 10000:
        print("Another "+str(n)+" articles found")
        # save raw data
        articles_df = pd.concat(articles, ignore_index=True)
        #articles_df.to_pickle("../../data/raw/articles/articles"+str(m)+".pkl")
        #articles_df.to_csv("../../data/raw/articles/articles"+str(m)+".tsv", sep="\t")
        
        # save (European) keyword-filtered articles
        filtered_articles = prep_articles.filter_keywords(articles_df, config=config)
        filtered_articles = prep_articles.filter_by_domain(filtered_articles, domain_id="https://openalex.org/domains/1")
                
        #filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/eu_articles"+str(m)+".pkl")
        print(f"[DEBUG] Saving {len(filtered_articles)} articles to: {interim_dir / f'articles{m}.pkl'}")
        filtered_articles.to_pickle(interim_dir / f"eu_articles{m}.pkl")
        #filtered_articles.to_csv("../../data/interim/keyword-filtered_articles/eu_articles"+str(m)+".tsv", sep="\t")
        #eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
        
        articles = []
        n = 0; m += 1

# same procedure for last articles
articles_df = pd.concat(articles, ignore_index=True)
#articles_df.to_csv("../../data/raw/articles/articles"+str(m)+".tsv", sep="\t")

filtered_articles = prep_articles.filter_keywords(articles_df, config=config)

filtered_articles = prep_articles.filter_by_domain(filtered_articles, domain_id="https://openalex.org/domains/1")

#filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/articles"+str(m)+".pkl")
print(f"[DEBUG] Saving {len(filtered_articles)} articles to: {interim_dir / f'articles{m}.pkl'}")
filtered_articles.to_pickle(interim_dir / f"articles{m}.pkl")
#eu_articles = prep_articles.filter_eu_articles(filtered_articles)
#eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
m += 1

# putting it together
#articles = prep_articles.merge_pkls("../../data/interim/keyword-filtered_articles/")
articles = prep_articles.merge_pkls(str(interim_dir.resolve()) + "/")
#eu_articles = prep_articles.merge_pkls("../../data/interim/eu_keyword-filtered_articles/")

# preprocess
articles = prep_articles.flatten_works(articles)
#eu_articles = prep_articles.flatten_works(eu_articles)

# save final version of all (European) keyword-filtered taxonomic articles together
#articles.to_pickle("../../data/interim/filtered_articles.pkl")
#articles.to_csv("../../data/interim/filtered_articles.tsv", sep="\t")
articles.to_pickle(interim_dir / "filtered_articles.pkl")
articles.to_csv(interim_dir / "filtered_articles.tsv", sep="\t")

#eu_articles.to_pickle("../../data/interim/eu_filtered_articles.pkl")
#eu_articles.to_csv("../../data/interim/eu_filtered_articles.tsv", sep="\t")

print("Taxonomic articles filtered. Results in data/interim/filtered_articles.tsv.")
