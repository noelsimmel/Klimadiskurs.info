# Investigate the corpus
# 1. Find most frequent "Klima-" words in all corpus texts
# 2. Find words in the word list that are most frequent in the corpus
# 3. Find words in the word list that were tweeted at least 100 times
# 4. Find out which words in the list contain hyphens

from collections import Counter
from dotenv import load_dotenv
from os import environ
from time import sleep
import string
import tweepy

def find_most_frequent_all(text_paths=("raw_data/texts_pro.txt", "raw_data/texts_contra.txt"), 
                           n=30):
    """Prints the most frequent words that start with "klima" from all texts in the corpus.

    Args:
        texts_paths (tuple(str), optional): Paths to master text files for each association group.
        n (int, optional): The n most frequent types will be printed. Defaults to 30.
    """

    print("Reading texts...")
    full_text = ""
    for path in text_paths:
        with open(path, encoding="utf-8", errors="replace") as f:
            full_text += f.read() 

    print("Finding climate words...")
    # remove all punctuation
    full_text = full_text.translate(str.maketrans('', '', string.punctuation+"‚„“”‛’‘"))
    # find all tokens that start with "klima"
    climate_words = [w for w in full_text.lower().split() if w.startswith("klima")]
    print(f"Found {len(climate_words)} words with prefix \"klima\"")

    print("Counting...")
    word_counts = Counter(climate_words)    # count frequency for each type

    print("30 most common words:", word_counts.most_common(n))

def find_most_frequent_wordlist(text_paths=("raw_data/texts_pro.txt", "raw_data/texts_contra.txt"), 
                                n=30):
    """Prints the most frequent words from path_wordlist from all texts in the corpus.

    Args:
        texts_paths (tuple(str), optional): Paths to master text files for each association group.
        n (int, optional): The n most frequent types will be printed. Defaults to 30.
    """

    print("Reading texts...")
    full_text = ""
    for path in text_paths:
        with open(path, encoding="utf-8", errors="replace") as f:
            full_text += f.read() 
    # remove all punctuation
    full_text = full_text.translate(str.maketrans('', '', string.punctuation+"‚„“”‛’‘"))

    print("Counting words...")
    wordset = __read_file(path_wordlist)
    counter_list = [w for w in full_text.lower().split() if w in wordset]
    word_counts = Counter(counter_list)    # count frequency for each type

    print("30 most common words:", word_counts.most_common(n))

def find_most_tweeted(n=300):
    """Prints terms from the corpus that were tweeted at least n times.

    Args:
        n (int, optional): Minimum frequency. Defaults to 300, current API limit is 500.
    """

    # read word list from file
    wordset = __read_file(path_wordlist)

    # connect to Twitter
    print("Connecting to Twitter API...")
    load_dotenv("../klimadiskurs/.env")
    api = tweepy.Client(bearer_token=environ.get("TW_BEARER_TOKEN"), wait_on_rate_limit=True)

    print(f"Printing words with at least {n} tweets...")
    for idx, word in enumerate(wordset):
        if idx in range(0, len(wordset), 100):
            print(f"  Querying word #{idx}")
        # if only recent tweets (within the last week) are desired, change to search_recent_tweets()
        tweets = api.search_all_tweets(word, max_results=n, since_id=20)
        sleep(1)
        if tweets.data and len(tweets.data) == n:
            print(word)

def investigate_spelling():
    """Counts how many words in path_wordlist are spelled with a hyphen.
    """

    wordset = __read_file(path_wordlist)
    hyphenated = [w for w in wordset if "-" in w]
    print(f"{len(hyphenated)} words contain a hyphen \"-\"")
    both_versions = [w for w in wordset if "-" in w and w.replace("-", "") in wordset]
    print(f"{len(both_versions)} appear with and without a hyphen")

def __read_file(path_wordlist):
    wordset = set()
    with open(path_wordlist, encoding="utf-8", errors="replace") as f:
        for line in f:
            wordset.add(line.lower().strip())
    print(f"{len(wordset)} words in corpus")
    return wordset


path_wordlist = "raw_data/wordlist.txt"

find_most_frequent_all()
find_most_frequent_wordlist()
find_most_tweeted()
investigate_spelling()
