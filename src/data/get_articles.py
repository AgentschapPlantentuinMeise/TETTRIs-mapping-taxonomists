# get all European taxonomic articles from taxonomic journals
import pandas as pd
import glob
import os
# custom packages
import download
import prep_articles


journals = pd.read_csv("../../data/processed/journals.csv")

# clear directory
files = glob.glob("../../data/raw/articles/*")
#files.extend(glob.glob("../../data/interim/eu_keyword-filtered_articles/*"))
for f in files:
    os.remove(f)

# ask OpenAlex (nicely) for all articles from these journals from 2014-2023
# can only use journals that have OpenAlex IDs and that are not dissolved
oaids = list(set(journals[journals["dissolved"]!=True]["openAlexID"]))
email = input("Enter e-mail address for OpenAlex API: ")
articles = []
n = 0; m = 0

# deal with PLOS ONE now
plosone_articles = download.request_works("primary_location.source.id:S202381698", email, to_date="2023-12-31")

filtered_articles = prep_articles.filter_keywords(plosone_articles)
filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/articles"+str(m)+".pkl")
#eu_articles = prep_articles.filter_eu_articles(filtered_articles)
#eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
m += 1

# download recent articles from every taxonomic journal
for oaid in oaids:
    if oaid != oaid: # check if nan
        continue
    if oaid == "S202381698": # dealt with PLOS ONE separately
        continue # (returns ~240 000 articles)
    
    # search by confirmed OpenAlex ID (from OpenAlex itself or Wikidata) 
    journal_articles = download.request_works("primary_location.source.id:"+oaid, email, to_date="2023-12-31")
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
        filtered_articles = prep_articles.filter_keywords(articles_df)
        #eu_articles = prep_articles.filter_eu_articles(filtered_articles)
        
        filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/eu_articles"+str(m)+".pkl")
        #eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
        
        articles = []
        n = 0; m += 1

# same procedure for last articles
articles_df = pd.concat(articles, ignore_index=True)
#articles_df.to_csv("../../data/raw/articles/articles"+str(m)+".tsv", sep="\t")

filtered_articles = prep_articles.filter_keywords(articles_df)
filtered_articles.to_pickle("../../data/interim/keyword-filtered_articles/articles"+str(m)+".pkl")
#eu_articles = prep_articles.filter_eu_articles(filtered_articles)
#eu_articles.to_pickle("../../data/interim/eu_keyword-filtered_articles/eu_articles"+str(m)+".pkl")
m += 1

# putting it together
articles = prep_articles.merge_pkls("../../data/interim/keyword-filtered_articles/")
#eu_articles = prep_articles.merge_pkls("../../data/interim/eu_keyword-filtered_articles/")

# preprocess
articles = prep_articles.flatten_works(articles)
#eu_articles = prep_articles.flatten_works(eu_articles)

# save final version of all (European) keyword-filtered taxonomic articles together
articles.to_pickle("../../data/interim/filtered_articles.pkl")
articles.to_csv("../../data/interim/filtered_articles.tsv", sep="\t")

#eu_articles.to_pickle("../../data/interim/eu_filtered_articles.pkl")
#eu_articles.to_csv("../../data/interim/eu_filtered_articles.tsv", sep="\t")

print("Taxonomic articles filtered. Results in data/interim/filtered_articles.tsv.")
