from flask import current_app, flash, json, redirect, render_template, url_for
from github import Github
import os
import random
import re
import requests
from klimadiskurs import db
from klimadiskurs.app.forms import EntrySubmitForm
from klimadiskurs.config import ENABLE_SUBMISSIONS, ITEMS_PER_PAGE, GITHUB_TOKEN

github = Github(GITHUB_TOKEN)
try:
    repo = github.get_repo("noelsimmel/klimadiskurs-files")
except github.GithubException.BadCredentialsException:
    current_app.logger.error("Bad GitHub credentials. Maybe the personal access token has expired.")

def home_route(template, **kwargs):
    """Route to the home page.
    Handles new term submissions and random button.
    Separate function because this logic is used by / and /search routes. 


    Args:
        template (str): HTML template to render.
        glossary (dict): Glossary/entries to display.
        tweeted (list(str), optional): List of tweeted terms. Defaults to [].
        include_html (list(str), optional): List of other templates to include.
        Defaults to [].

    Renders:
        template
    """

    # submit form
    form = EntrySubmitForm()
    if form.validate_on_submit():
        # only accept submission if it's not spam
        if not form.url.data: 
            send_submission(form)
            return redirect(url_for("glossary.home"))

    # select random entry that has a definition for the "random" button
    try:
        random_entry = random.choice(list({k for k, v in db.items() if v["definition"]}))
    # if no entry has a definition, just use "Klimaleugner"
    except IndexError:
        random_entry = "Klimaleugner"

    return render_template(template, **kwargs, random_entry=random_entry, 
                           form=form, db_size=len(db), enable_submissions=ENABLE_SUBMISSIONS, 
                           items_per_page=ITEMS_PER_PAGE)

def get_files_in_directory(path, extension=""):
    """Returns a list of all files in a directory (with a given extension).

    Args:
        path (str): Path to the directory.
        extension (str, optional): Extension to select, including the dot.
        Defaults to "", i.e. all files.
    """

    return [f for f in os.listdir(path) if f.endswith(extension)]

def query_db(query):
    """Helper function. Queries the database by key.

    Args:
        query (str): Query.

    Returns:
        dict: Dict subset of search results.
    """

    return {k: v for k, v in db.items() if query.lower() in k.lower()}

def get_github_file(fn, repo_name="noelsimmel/klimadiskurs-files"):
    """Retrieves a file using the GitHub API.
    Content is base64 encoded. Use get_github_file_decoded() to get the decoded content as a string.

    Args:
        fn (str): Path to the file that should be retrieved.
        repo_name (str, optional): Name of the repository. 
        Defaults to "noelsimmel/klimadiskurs-files".

    Returns:
        github.ContentFile.ContentFile
        https://pygithub.readthedocs.io/en/latest/github_objects/ContentFile.html#github.ContentFile.ContentFile
    """

    repo = github.get_repo(repo_name)
    return repo.get_contents(fn)

def get_github_file_decoded(fn, repo_name="noelsimmel/klimadiskurs-files", encoding="UTF-8"):
    """Retrieves a file using the GitHub API and returns its content as a string.

    Args:
        fn (str): Path to the file that should be retrieved.
        repo_name (str, optional): Name of the repository.
        Defaults to "noelsimmel/klimadiskurs-files".
        encoding (str, optional): Encoding to decode to. Defaults to "UTF-8".

    Returns:
        str: Decoded file content.
    """

    repo = github.get_repo(repo_name)
    return repo.get_contents(fn).decoded_content.decode(encoding)

def get_dwds_link(term):
    """Query the DWDS API to see if term exists in the dictionary.

    Args:
        term (str): Query.

    Returns:
        str: URL to the DWDS entry for term if it exists, otherwise None.
    """

    try:
        dwds_url = f"https://www.dwds.de/api/wb/snippet/?q={term.capitalize()}"
        # sample response: 
        # [{"wortart":"Substantiv","url":"https://www.dwds.de/wb/Klimawandel",
        # "input":"Klimawandel","lemma":"Klimawandel"}]
        dwds_response = requests.get(dwds_url)
        dwds_content = json.loads(dwds_response.content.decode("utf-8"))
        if dwds_content:
            return dwds_content[0]["url"]
    # sometimes DWDS doesn't respond in time
    except TimeoutError:
        current_app.logger.error("TimeoutError: DWDS API didn't respond in time")
    # catch other exceptions that might be caused by users' unstable internet connection
    except Exception as e:
        current_app.logger.error(e)
    return

def send_submission(form):
    """Generates a new database entry from a submission and writes it to the file on GitHub.

    Args:
        form (EntrySubmitForm): Flask form.
    """

    # only do anything if submissions are enabled in the config/env vars
    if ENABLE_SUBMISSIONS:
        # generate Python dict
        new_entry = __generate_db_entry(form)

        # read submissions file from GitHub
        submissions_file = get_github_file("submissions.tsv")

        # decode content and append new entry
        # do it like this to avoid trailing tabs at the end of the line
        content = submissions_file.decoded_content.decode("UTF-8") + "\n" + new_entry["term"]
        for key in EntrySubmitForm.fieldnames[1:]:
            content += "\t" + str(new_entry[key])

        try:
            # this replaces the old file content, "submission" is the commit message
            repo.update_file(submissions_file.path, "submission", content, submissions_file.sha)
            current_app.logger.info(f"New submission received: \"{form.term.data}\"")
            flash("Wir haben Ihren Vorschlag erhalten und werden ihn überprüfen. Vielen Dank!", 
                  "success")
        except Exception as e:
            current_app.logger.error("GitHub API Error:", e)
            flash("""Leider haben wir gerade technische Probleme. 
                  Bitte versuchen Sie es später erneut.""", "error")
        
def __generate_db_entry(form):
    """Helper function for send_submissions(). 
    Generates a Python dict from form data.

    Args:
        form (EntrySubmitForm): Flask form.
    """
    
    # ALL dict values MUST be strings so they can be written to submission.tsv
    # lists items can be separated by spaces (for words) or delimiter symbol █ (for phrases)
    # e.g. association list [0, 1] => "0 1"
    # e.g. examples list ["example 1", "example 2"] => "example 1█example 2"
    entry = {"id": 0, "term": form.term.data.capitalize(), 
             "definition": form.definition.data.strip(), 
             "sources": "", "association": "", "examples": "", "related": ""}

    # alternate spellings
    term = form.term.data.capitalize()
    entry["spellings"] = term
    if "-" in term:
        entry["spellings"] += " " + term.replace("-", "")
    else:
        entry["spellings"] += " Klima-" + term[5:].capitalize()

    # groups who use that term
    # ass_con = contra = 0 = climate sceptics
    # ass_pro = 1 = climate activists or groups who believe in human-made climate change
    for idx, checkbox in enumerate([form.ass_con, form.ass_pro]):
        if checkbox.data:
            entry["association"] += str(idx) + " "

    # tokenize sources
    for source in form.sources.data.splitlines():
        # some regex logic in case user input is separated by commas, as it often is
        source = re.sub("[,;]", "", source)
        entry["sources"] += source.strip() + " "

    # tokenize examples
    for ex in form.examples.data.splitlines():
        entry["examples"] += ex.strip() + "█"   # easy to spot delimiter
    entry["examples"] = entry["examples"][:-1]  # remove last delimiter

    return entry
