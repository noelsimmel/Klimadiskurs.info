# Contains all Twitter related functions

import tweepy
import re
from time import sleep
from klimadiskurs.config import TWITTER_TOKEN

class Tweet():
    """Custom Tweet class. Makes working with tweets easier."""

    def __init__(self, data, users):
        """Constructor. Only keeps valuable information from the API response:
        Tweet ID, text, user handle (@username), date.
        Links are removed from tweet text.

        Args:
            data (list): Tweet data from API response.
            users (list): User data from API response.
        """
        
        self.id = str(data.id)
        self.text = data.text
        self.handle = [user.username for user in users if user.id == data.author_id][0]
        self.date = data.created_at.strftime("%d.%m.%y")

        self.text = re.sub(r"http\S+", "", self.text)   # remove links
        self.text = re.sub(r"www\S+", "", self.text)   # remove links

    def __str__(self):
        """Tweet string representation, example: \"@username: This is the tweet text.\""""

        return f"@{self.handle}: {self.text}"

    def __repr__(self):
        """Tweet string representation (used in list of Tweet objects), example:
        [\"@username: This is tweet 1\", \"@otheruser: Blablabla\", ...]"""

        return self.__str__()

    def __contains__(self, query):
        """Checks if tweet text contains a query and returns a boolean.
        Example for query="Klimaleugner":
        Returns True iff \"klimaleugner\" OR \"klima-leugner\" 
        or \"klima leugner\" is in tweet text, case insensitive.
        """

        text = self.text.lower()
        contains = query.lower() in text \
            or "klima-" + query[5:] in text \
            or "klima " + query[5:] in text
        return contains

    def startswith(self, query):
        """Checks if tweet text starts with a query and returns a boolean.
        Case insensitive."""

        return self.text.lower().startswith(query.lower())


def connect_to_twitter():
    """Connects to Twitter API using tweepy.Client.

    Returns:
        tweepy.Client: The API.
        (None: If errors occurred.)
    """

    api = tweepy.Client(bearer_token=TWITTER_TOKEN, wait_on_rate_limit=True)
    # verify connection
    try:
        api.get_tweet(20)
        return api
    except tweepy.errors.Unauthorized:
        print("ERROR: Could not verify Twitter credentials")
    except Exception as e:
        print(e)
    return None

def query_tweets(query, api, count=10):
    """Queries the full Twitter archive using search_all_tweets(). 
    Results are cleaned using filter_tweets().

    Needs Twitter API v2 Academic Research access: 
    https://developer.twitter.com/en/docs/projects/overview#product-track
    With Essential or Elevated access, use search_recent_tweets() instead.

    Args:
        query (str): The query (term).
        api (tweepy.Client): Twitter API object.
        count (int, optional): Maximum number of tweets to return. Defaults to 10.

    Returns:
        list(Tweet): List of Tweet objects.
        (list(): Empty list if some error occurred.)
    """

    print(f"Querying Twitter API for {query}")

    # if API connection failed (error is logged by connect_to_twitter)
    if not api: return []

    # retrieve twice the number of tweets at first and filter them down to 10 below
    try:
        response = api.search_all_tweets(query+" OR "+"klima-"+query[5:]+" lang:de -is:retweet", 
                                         max_results=count*2, 
                                         since_id=20, tweet_fields=["created_at", "author_id"],
                                         expansions="author_id")
        # avoid rate limiting
        # requesting >1 /def/ entries per second leads to a tweepy error (rate limit)
        # this can be solved by clicking more slowly or reloading the page
        sleep(1)
    # in case of errors, return an empty list --> don't show any tweets
    except Exception as e:
        print(e)
        return []
    
    return filter_tweets(response, query)[:count]

def filter_tweets(response, query):
    """Take a Twitter API response and filters it to exclude retweets and mentions.

    Args:
        response (requests.Response): API response (i.e. result of search_all_tweets()).
        query (str): The query.

    Returns:
        list(Tweet): List of tweets that passed the filter.
    """

    if not response.data: return []

    # set to avoid duplicate tweets
    tweets = []
    for i in range(len(response.data)):
        tweets.append(Tweet(response.data[i], response.includes["users"]))

    # filter out manual retweets to avoid duplicates 
    # filter out tweets where the term only appears in the username 
    # note that __contains__ and startswith are redefined for Tweet objects
    tweets_cleaned = [t for t in tweets if not t.startswith("RT") 
                      and query in t and "@"+query not in t]

    return tweets_cleaned
