# Download the original Climate Change Glossary: https://github.com/ajgoecke/climate_change_glossary
# This scipt combines all the .txt files in text_files/pro and text_files_contra
# into one .txt master file, respectively
# This is necessary for preprocess_wordlists.py and create_json.py

import os

def create_master_text_file(source_path, target_filename):
    """
    Merges all .txt files in path into a single file in target_filename.

    Used to merge all files for each group into a master file, which is used to find example 
    sentences for the glossary entries.

    Format:

    *** FILE {number of file} *** {path to file} \n
    {file text} \n\n

    Args:
        source_path (str): Path to the main directory.
        target_filename (str): Filename of the resulting master text file.
    """

    c = 1   # counts number of files
    # recursively walk all subdirectories of source_path
    for root, _, files in os.walk(source_path):
        for fn in files:
            if fn.endswith(".txt"):
                path_to_file = os.path.join(root, fn)
                with open(target_filename, mode="a", encoding="utf-8") as target:
                    target.write(f"*** FILE {c} *** {path_to_file} \n")
                    with open(path_to_file, encoding="utf-8", errors="replace") as source:
                        for line in source:
                            target.write(line)
                    target.write("\n\n")
                c += 1


# example call using CCG github repo:
create_master_text_file("../../climate_change_glossary/text_files/pro", 
                        "raw_data/texts_pro.txt")
create_master_text_file("../../climate_change_glossary/text_files/contra", 
                        "raw_data/texts_contra.txt")
