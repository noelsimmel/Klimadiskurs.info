# This script converts the raw data from Goecke's Climate Change Glossary into a JSON database.
# It reads the list of climate compounds "raw_data/wordlist.txt" 
# and finds example sentences from the master files of the pro and contra groups.
# These master files must be created once by create_master_text_files.py and moved to /raw_data.
# The final JSON structure is specified in the JSON schema "glossary.schema.json".

import re
import json
from os import path
from time import time

def create_json(json_path,
                wordlist_path="raw_data/wordlist.txt",
                groups_texts_paths=["raw_data/texts_contra.txt", "raw_data/texts_pro.txt"],
                verbose=True):
    """
    Creates the glossary database in JSON format. 

    Args:
        json_path (str): The path to the final JSON file. This should not yet exist.
        wordlist_path (str): Path to a plain text list of all terms in the glossary.
        groups_texts_paths (list(str)): List of paths to full text files for each association \
            group. These master files can be created using create_master_text_file.py
        verbose (bool): Whether to output more detailed status information. Defaults to True.
    """

    t0 = time()

    # avoid accidentally overwriting files
    if path.isfile(json_path):
        print(f"The file {json_path} already exists. Please remove it.")
        exit()

    # read the list of terms
    terms_list = []
    with open(wordlist_path, encoding="utf-8", errors="replace") as f:
        for line in f:
            terms_list.append(line.strip())

    # read and tokenize master text file for each group
    groups_texts = []  # list of lists of sentences for each group
    for fn in groups_texts_paths:
        groups_texts.append(__tokenize_file(fn))

    print("Creating glossary entries...")
    # create the actual glossary
    glossary = __create_glossary_content(terms_list, groups_texts, verbose)

    # write it to json
    with open(json_path, mode="w+", encoding="utf-8", errors="replace") as f:
        f.write(json.dumps(glossary, indent=2, ensure_ascii=False))

    print(f"Done in {(time()-t0)/60} minutes")

def __tokenize_file(path, min_sentence_length=4):
    """
    Reads text from a file and tokenizes it.
    
    Removes sentences that are shorter than a minimum number of words. This is 
    to ensure more meaningful example sentences in the finished glossary.

    Args:
        path (str): Path to a text file.
        min_sentence_length (int, optional): Minimum number of words per sentence. Defaults to 4.

    Returns:
        list(str): List of sentences.
    """

    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    # split text into sentences
    # don't split on : as it is often used as part of headlines
    sentences = re.split(r"[\.|!|?|…] |…\.|\n", text)
    sentences = [s for s in sentences if "klima" in s.lower()
                 and len(s.split()) >= min_sentence_length
                 and len(s.split()) < 70    # discard very long sentences (usually enumerations)
                 and not s.startswith("*** FILE")]  # only sentences with klima words
    return sentences

def __create_glossary_content(terms_list, groups_texts, verbose):
    """
    The actual glossary creation.

    Iterates over the list of terms, creates glossary entries with ID, association groups and 
    examples and adds them to a dictionary.

    Args:
        terms_list (list(str)): List of terms for the glossary.
        groups_texts (list(list(str))): Contains lists of sentences from each group.
        verbose: Whether to print terms that were excluded from the glossary due to lack of examples

    Returns:
        dict: Contains glossary entries.
        Ex: {"Klimalüge": {"term": "Klimalüge", "id": 45, etc.}, ...}
    """

    counter = 1  # counts valid entries = entry IDs
    glossary = dict()
    for term in terms_list:
        idx = counter
        # indicate progress
        if idx in range(0, len(terms_list), 100): print(f"Creating entry #{idx}...")
        # actual entry creation
        entry = __create_single_entry(term, idx, groups_texts, verbose=verbose)
        # ignore terms without any examples, i.e. with example "sentences" of less than 4 words
        if not entry: continue
        glossary[entry["term"]] = entry
        counter += 1
    return glossary
 
def __create_single_entry(term, idx, groups_texts, verbose=False):
    """
    Creates a glossary entry for a single term. 

    Creates a dict with keys "term", "id", "association", "examples". 
    Finds up to 2 example sentences for each association/group.

    Args:
        term (str): The glossary term, i.e. "klimawandel".
        id (int): Each entry has a unique consecutive ID, starting from 1.
        groups_texts (list(list(str))): Contains lists of sentences from each group.

    Returns:
        dict(str): One glossary entry. 
        Ex: {"term": "Klimalüge", "id": 45, "association": [1], "examples": ["..."], ...}
    """
    
    # definition, sources and related have to be filled in manually
    entry = {"term": term, "id": idx, "definition": "", "sources": [], "related": []}

    # compounds are often spelled with hyphens
    entry["spellings"] = [term, "Klima-" + term[5:].capitalize()]

    # "association" is a list of ids (indices) for groups that use that term,
    # i.e. climate sceptics (id 0) or climate activists (id 1)
    # get up to 2 example sentences for each group
    entry["examples"], entry["association"] = __get_examples(term, groups_texts, 
                                                             entry["spellings"], verbose=verbose)
    # ignore terms without any examples, i.e. with example "sentences" of less than 4 words
    if not entry["examples"]: 
        if verbose: print(f"Couldn't find examples for {term}")
        return dict()
    return entry

def __get_examples(term, all_groups_texts, spellings, max_examples_per_group=2, verbose=False):
    """
    Finds example sentences for a term from the corpus texts.

    Extracts up to <max_examples_per_group> sentences that contain <term> from <all_group_texts>
    per group. If no exact matches are found, the search is expanded to words that contain <term>. 

    Args:
        term (str): The term, e.g. "Klimalüge".
        all_groups_texts (list(list(str))): Contains lists of sentences from each group.
        spellings (list(str)): List of alternative spellings of term.
        max_examples_per_group (int, optional): Max number of example sentences per group. \
            Defaults to 2.
        verbose (bool, optional): Whether to print information about terms that didn't have an \
            exact match in the texts (where expanded search was carried out). Defaults to False.

    Returns:
        list(str): Example sentences for <term>.
        list(int): List of ids for the groups that <term> is used by.
    """

    examples = []
    ass = []
    # iterate over all group master files
    for group_id, group_texts in enumerate(all_groups_texts):
        group_examples = set()
        # iterate over all sentences in one master file
        for sentence in group_texts:
            # this regex matches the term exactly while escaping special characters such as *
            # using negative lookahead assertion to match "Klima-CO2" but not "Klima-CO2-Signal"
            for variant in spellings:
                if re.search(r"\b"+re.escape(variant)+r"\b(?!-)", sentence, flags=re.I):
                    group_examples.add(sentence)
                    break
            if len(group_examples) == max_examples_per_group: 
                break
        # if this doesn't yield any matches for a group,
        # expand search to sentences that simply include the word
        # e.g. "Klimalüge" would get an example sentence containing "Klimalügen"
        if not group_examples:
            for sentence in group_texts:
                if term in sentence:
                    group_examples.add(sentence)
                    if verbose:
                        print(f"No examples for '{term}' for group {group_id}, used fuzzy search")
                    if len(group_examples) == max_examples_per_group: break
        if group_examples: ass.append(group_id)
        examples += list(group_examples)
    return examples, ass


glossary_path = "glossary.json"
cleaned_wordlist_path = "raw_data/wordlist.txt"

create_json(glossary_path, cleaned_wordlist_path)
