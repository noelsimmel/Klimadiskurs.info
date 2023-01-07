# The heart of the app
# Contains all routes/view functions

from flask import current_app, Blueprint, request, send_from_directory
from flask.templating import render_template
from collections import namedtuple
from klimadiskurs import db, platforms_db
from klimadiskurs.config import ENABLE_SUBMISSIONS
from klimadiskurs.app.utils import home_route, query_db, \
    get_files_in_directory, get_github_file_decoded, get_dwds_link
from klimadiskurs.app.utils_twitter import connect_to_twitter, query_tweets

# the following lines are executed only on server (re)start:
# 1. initialize blueprint (see __init__.py)
glossary = Blueprint("glossary", __name__, template_folder="templates", 
                     static_folder="static")

# 2. connect to Twitter API
twitter_api = connect_to_twitter()

# 3. get list of tweeted terms from GitHub
# this means the glossary view will only be updated on Heroku dyno cycling (1x/day)!
tweeted = [t.strip() for t in get_github_file_decoded("tweeted_terms.txt").split()]

@glossary.route("/", methods=["GET", "POST"])
def home():
    """Home route (/). Logic is contained in home_route() in utils.py.
    
    Renders: goecke-home.html
    """

    # display full database sorted by newest entries
    glossary = sorted(db, key=lambda k: db[k]["id"], reverse=True)
    return home_route("goecke/goecke-home.html", glossary, tweeted)

@glossary.route("/search/<query>", methods=["GET", "POST"])
@glossary.route("/search/<query>/", methods=["GET", "POST"])
def search(query):
    """Search route (/search/<query>).
    Same as home route, but the glossary content is replaced with an alphabetical list of search 
    results. This view is returned when the user presses the "1" button on a normal search results
    page. The normal search is performed by JavaScript/AJAX, not Flask (see search.js).

    Args:
        query (str): The search query.

    Renders: searchresult.html
    """

    # if search field is empty, search.js puts "None" as placeholder
    # in that case return all entries sorted alphabetically (takes a few seconds)
    if query == "None":
        return home_route("goecke/goecke-searchresult.html", sorted(db), tweeted)

    results = query_db(query)
    # sort results alphabetically
    results = sorted(results, key=lambda k: results[k]["term"])
    return home_route("goecke/goecke-searchresult.html", results, tweeted)

@glossary.route("/api")
def api():
    """Internal API used by search.js to query the database.
    Does not return a view, just the search results.

    Returns:
        dict: The search results dictionary (filtered database).
    """

    # get user query from form field
    # https://stackoverflow.com/questions/41475945/ajax-request-to-perform-search-in-flask
    user_query = request.args.get("query")
    current_app.logger.info(f"API call: {user_query}")

    # same logic as /search
    if user_query == "None": return db
    return query_db(user_query)

@glossary.route("/def/<term>")
@glossary.route("/def/<term>/")
def define(term):
    """Glossary definition route (/def/<term>). 
    Gets glossary info from the database, DWDS, and twitter and plugs it into the view.

    Args:
        term (str): Term in the glossary.

    Renders: goecke-definitions.html
    """

    # check if term is in database. if not, show error page
    if term.lower() not in db and term.capitalize() not in db:
        # route to error page if term is not in database
        message = f"Der Begriff \"{term.capitalize()}\" ist noch nicht in unserer Datenbank."
        if ENABLE_SUBMISSIONS:
            message += " Sie können ihn auf der Startseite hinzufügen."
        return render_template("errorpage.html", message=message)

    # query Twitter API for tweets
    tweets = query_tweets(term, twitter_api)

    # query DWDS API to see if the term is in the dictionary
    dwds = get_dwds_link(term)

    try:
        entry = db[term.capitalize()]
    except KeyError:
        entry = db[term.lower()]

    # defined terms is a list of terms with definitions
    # if these appear in this term's definition, they are hyperlinked
    defined_terms = [term for term in db.keys() if db[term]["definition"]]
    return render_template("goecke/goecke-definitions.html", term=term.capitalize(), entry=entry,
                           dwds=dwds, defined=defined_terms, tweets=tweets)

@glossary.route("/about")
@glossary.route("/about/")
def about():
    """About route (/about). 
    Calculates glossary statistics.

    Renders: about.html
    """

    Statistics = namedtuple("Statistics", "no_entries no_definitions no_tweeted \
                                           pct_pro pct_contra pct_both")

    n = len(db)

    stats = Statistics(n,   # total entries in db
                       sum(1 for v in db.values() if v["definition"]),  # with definition
                       len(tweeted),    # with recent tweets
                       # percentage of entries per group
                       int(sum(100 for v in db.values() if 1 in v["association"])/n),
                       int(sum(100 for v in db.values() if 0 in v["association"])/n),
                       # percentage of shared terms between both groups
                       int(sum(100 for v in db.values() if v["association"] == [0, 1])/n)
                       )

    return render_template("about.html", stats=stats)

@glossary.route("/download")
@glossary.route("/download/")
def download():
    """Download route (/download).
    
    Renders: download.html (static page)
    """
    
    return render_template("download.html")

@glossary.route("/download/wordlist")
def download_wordlist():
    """Wordlist download route (/download/wordlist).
    Returns wordlist.txt from tools/raw_data.
    """
    
    return send_from_directory("../tools/raw_data", "wordlist.txt")

@glossary.route("/download/json")
def download_json():
    """Database download route (/download/json).
    Returns glossary.json from static/data.
    """
    
    return send_from_directory("static/data", "glossary.json")

@glossary.route("/download/submissions")
def download_submissions():
    """
    Submissions download route (/download/submissions).
    Downloads the submissions.tsv file from GitHub and sends it to the user. 
    This "secret" route is not displayed on the website and only for internal use.
    """

    submissions = get_github_file_decoded("submissions.tsv")
    # creates the file in static/data folder where it is deleted once per day when the dyno cycles
    # see Heroku ephemeral disk: https://devcenter.heroku.com/articles/active-storage-on-heroku 
    with open("klimadiskurs/static/data/submissions.tsv", mode="w", encoding="utf-8") as f:
        f.write(submissions)
    return send_from_directory("static/data", "submissions.tsv")

@glossary.route("/wahlprogramme")
def wahlprogramme():
    """
    Route for party platforms research by Juliane Hanel (/wahlprogramme).
    """

    glossary = sorted(platforms_db)
    graphs = get_files_in_directory("klimadiskurs/templates/platforms/graphs", ".html")

    return home_route("platforms/platforms-home.html", glossary, include_html=graphs)
