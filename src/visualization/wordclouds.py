from wordcloud import WordCloud, STOPWORDS
import pickle
import pandas as pd
import matplotlib.pyplot as plt


# exclude additional words from wordclouds
stopwords = STOPWORDS
stopwords.update(["one", "two", "three", "four", "five", "et"]
                 +list("abcdefghijklmnopqrstuvwxyz1234567890.,;"))

def wordcloud_abstracts(df, name):
    abstract_words = df["abstract_inverted_index"]
    abstract_words = list(filter(None, abstract_words))
    
    frequencies = {}
    
    for pub in abstract_words:
        for word, indices in pub.items():
            word = word.strip(".")
            # add new word to frequencies
            if word in frequencies:
                frequencies[word] += len(indices)
            # add new words that are not stopwords
            elif word.lower() not in stopwords: 
                frequencies[word] = len(indices)
    
    # make wordcloud of abstract word frequencies
    wordcloud = WordCloud(stopwords=stopwords, background_color="white",
                          width=2000, height=1000).fit_words(frequencies)
    
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    # save wordcloud for this concept
    plt.savefig("../../reports/figures/wordcloud_"+name+".png", format="png", dpi=600, bbox_inches='tight')
    plt.show()

articles = pd.read_pickle("../../data/processed/taxonomic_articles_with_subjects.pkl")
wordcloud_abstracts(articles, "european_taxonomic_articles")
