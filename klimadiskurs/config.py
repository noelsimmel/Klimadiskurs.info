# Config file
# Reads all config variables from the .env file
# On Heroku, there is no .env file, instead use the heroku config command: 
# https://devcenter.heroku.com/articles/config-vars

from dotenv import load_dotenv
from os import environ

load_dotenv()

# database
# how many items to show per "page" on the home page
# changing this may break the layout
ITEMS_PER_PAGE = 30
# if set to 1, users will be able to submit new entries through the submit form
# 1/0 instead of True/False for cross-compatibility with JavaScript
ENABLE_SUBMISSIONS = int(environ.get("ENABLE_SUBMISSIONS"))

# Twitter API access token
TWITTER_TOKEN = environ.get("TW_BEARER_TOKEN")

# GitHub API access token
GITHUB_TOKEN = environ.get("GH_ACCESS_TOKEN")

# Config class is only necessary for Flask app configuration
class Config:
    # Flask app key
    SECRET_KEY = environ.get("APP_SECRET_KEY")
    # whether to run in debug mode or not
    DEBUG_MODE = int(environ.get("DEBUG_MODE"))
