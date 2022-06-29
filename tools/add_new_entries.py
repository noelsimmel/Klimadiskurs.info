# This script adds submissions from the web app to the glossary JSON file.
# First, download submissions:
#   Either from GitHub (copy raw content and save as submissions.tsv):
#     https://github.com/noelsimmel/klimadiskurs-files/blob/main/submissions.tsv
#   Or http://klimadiskurs.info/download/submissions
# Edit the file to keep only the submissions you want (e.g. using Excel)
# Make sure to open it with UTF-8 encoding
# Then place the TSV in tools/ directory and run this script

import csv
import json
import os

fieldnames = ["term", "id", "definition", "sources", "association", 
              "examples", "spellings", "related"]

def add_new_entries(tsv_path, json_path, overwrite):
    """
    Creates new glossary entries from a curated TSV file and merges them with the existing glossary.

    Overwrites json_path with the new glossary. The old glossary is stored in glossary_OLD.json for 
    comparison (git diff recommended). The TSV is emptied, but the old file is stored in 
    submissions_OLD.tsv. 

    Args:
        tsv_path (str): Path to submissions.tsv (downloaded from Heroku).
        json_path (str): Path to glossary.json.
        overwrite (bool): Whether existing glossary information (i.e. example sentences) should be \
            overwritten by information from the TSV. If False, only missing information is filled \
            in.
    """

    # read both files
    submissions = __read_tsv(tsv_path)
    with open(json_path, encoding="utf-8", errors="replace") as f:
        live_db = json.load(f)

    # construct dict with new entries
    new_db, adds, mods = __construct_new_dict(submissions, live_db, overwrite)
    # merge dicts
    new_db = live_db | new_db

    # rename old files so they won't get deleted
    try:
        os.rename(json_path, os.path.splitext(json_path)[0] + "_OLD.json")
        os.rename(tsv_path, os.path.splitext(tsv_path)[0] + "_OLD.tsv")
    except FileExistsError as e:
        fn, ext = os.path.splitext(str(e).split()[-3])
        culprit = fn + "_OLD" + ext
        print(f"Error: File {culprit} already exists, please remove it.")
        exit()

    # write new db to file
    with open(json_path, mode="w", encoding="utf-8", errors="replace") as f:
        f.write(json.dumps(new_db, indent=2, ensure_ascii=False))

    # empty submissions file, only leave header
    with open(tsv_path, mode="w", encoding="utf-8", errors="replace") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        writer.writeheader()

    print(f"Updated {json_path}")
    print(f"Added {adds} new entries, modified {mods} existing entries")

def __read_tsv(tsv_path):
    """Reads the submissions file and converts it to the glossary dictionary fomat.
    Note: The ID field is filled in in __construct_new_dict().

    Args:
        tsv_path (str): see add_new_entries

    Returns:
        dict(str(dict())): Glossary.
    """

    submissions = dict()

    with open(tsv_path, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f, fieldnames=fieldnames, delimiter="\t")
        for row in reader:
            term = row["term"]
            if term == "term": continue  # skip header
            if not term: continue   # skip empty lines
            if term in submissions:
                print(f"Warning: Several entries for {term} in submissions file.", 
                      "Only using the last one")
            values = {"term": term, "related": []}
            values["term"] = term
            # all dict values are currently strings and must be converted to lists
            values["definition"] = row["definition"].strip()
            values["sources"] = __split_string(row["sources"])
            values["spellings"] = __split_string(row["spellings"])
            values["examples"] = __split_string(row["examples"], "█")
            values["association"] = [int(i) for i in __split_string(row["association"])]
            submissions[term] = values
    
    return submissions

def __split_string(s, delimiter=None):
    """
    Splits a string using a delimiter and built-in split() function. 

    Catches AttributeError when dictionary value is None.

    Args:
        s (str): The string.
        delimiter (str, optional): Delimiter. Defaults to None = whitespace => split().

    Returns:
        list(str): List of string units.
    """

    try:
        return [i.strip() for i in s.split(delimiter) if i]
    except AttributeError:
        return []

def __construct_new_dict(submissions, live_db, overwrite):
    """
    Constructs a dictionary of new entries from submissions and the current glossary.

    Terms that are not yet in the glossary are added with new IDs. Entries that already are in the 
    glossary are updated with new information from submissions (e.g. definitions).

    Args:
        submissions (dict): Submissions dict from __read_tsv().
        live_db (dict): Glossary JSON that is currently live on the app.
        overwrite (bool): Whether to overwrite all information with new info from submissions. If \
            False, only missing information is filled in. Normally only concerns example sentences \
            that may have been submitted through the app.

    Returns:
        dict: Dictionary with new entries.
        int: Number of new entries.
        int: Number of modified entries.
    """

    new_db = dict()
    last_id = len(live_db)
    adds, mods = 0, 0

    for term, entry in submissions.items():
        original_term = term
        term = term.replace("-", "").capitalize()   # adhere to glossary spelling rules
        # previously unseen terms/items/entries are added as-is
        if term not in live_db: 
            new_db[term] = entry
            new_db[term]["id"] = last_id + 1
            last_id += 1
            adds += 1
        # update existing entries
        else:
            new_db[term] = live_db[term]
            if overwrite:
                # update with key, value if value is informative (truthy)
                new_db[term].update((k, v) for (k, v) in submissions[original_term].items() if v)
            else:
                # update with key, value iff value is informative and not yet filled
                new_db[term].update((k, v) for (k, v) in submissions[original_term].items() if v 
                                    and not new_db[term][k])
            mods += 1
    
    return new_db, adds, mods


tsv_path = "submissions.tsv"
json_path = "../klimadiskurs/static/data/glossary.json"
overwrite = False   # recommended
add_new_entries(tsv_path, json_path, overwrite)
