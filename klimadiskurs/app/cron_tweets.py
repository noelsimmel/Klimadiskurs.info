# Cron job script
# Queries the Twitter API for each term in the glossary
# Writes terms that have been tweeted to GitHub repo
# Used to determine which glossary entries to link in the app
# Scheduled to run every Sunday at 1:30 am UTC

from datetime import datetime
from github import Github
from time import sleep
from klimadiskurs import db
from klimadiskurs.config import GITHUB_TOKEN
from klimadiskurs.app.utils_twitter import connect_to_twitter

# script should run only once a week
# workaround since Heroku Scheduler can only schedule daily tasks
# 0 = Monday, 6 = Sunday
if datetime.today().weekday() != 6:
    print("Today is not Sunday. Trying again tomorrow.")
    exit()

def get_file(filename):
    """Gets a file from GitHub and decodes it.

    Args:
        fn (str): Path to the file.

    Returns:
        tuple(str): The GitHub file [0] and the decoded contents of the file [1].
    """

    return (repo.get_contents(filename), 
            repo.get_contents(filename).decoded_content.decode("UTF-8"))

def write_to_file(term):
    """
    Adds a term to tweeted_terms_temp.txt on GitHub and commits it.

    Args:
        term (str): The term.
    """

    tweets_file, content = get_file("tweeted_terms_temp.txt") 
    content += "\n" + term

    try:
        repo.update_file(tweets_file.path, "new term", content, tweets_file.sha)
        sleep(9)   # avoid GitHub API error 409 (occurs when too many requests)
    except Exception as e:
        print("GitHub API Error:", e)


print(f"Searching recent tweets for {len(db)} terms")
api = connect_to_twitter()
github = Github(GITHUB_TOKEN)
repo = github.get_repo("noelsimmel/klimadiskurs-files")

# if tweeted_terms_temp.txt is empty, search full database
# otherwise start from last tweeted term (used if this task timed out or was interrupted)
terms_list = list(db.keys())
_, content = get_file("tweeted_terms_temp.txt")
try:
    last_idx = terms_list.index(content.split()[-1])
    terms_list = terms_list[last_idx+1:]
except IndexError:
    last_idx = 0
    terms_list = list(db.keys())

# Twitter sadly doesn't allow * in API calls, so ignore gendered terms
# * raises a tweepy.errors.BadRequest 400 (wildcard character cannot appear in a term)
terms_list = [t for t in terms_list if "*" not in t]

# query API and write to GitHub file
for idx, term in enumerate(terms_list):
    if idx+last_idx in range(0, len(db), 100):
        print(f"Querying term {idx}/{len(db)}")
    tweets = []
    for variant in (term, "Klima-" + term[5:]):
        try:
            response = api.search_all_tweets(variant + " lang:de -is:retweet", 
                                             max_results=10, since_id=20)
            sleep(1)  # to avoid rate limiting
            tweets += [t for t in response.data if not t.text.startswith("RT") 
                       and variant.lower() in t.text.lower()]
            if tweets:
                write_to_file(term)
                break
        # if no tweets were found for a term
        except TypeError: continue

# after processing the whole db
# save the list to tweeted_terms.txt and empty the temp file
tweets_file, content = get_file("tweeted_terms_temp.txt")
backup_file, _ = get_file("tweeted_terms.txt")
repo.update_file(backup_file.path, "backup", content, backup_file.sha)
print("Copied all terms to final file")
repo.update_file(tweets_file.path, "emptied", "", tweets_file.sha)  # update with empty string
print("Emptied temp file")
