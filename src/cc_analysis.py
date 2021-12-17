from cc_credentials import get_s3_bucket
from collections import defaultdict
import os
import re

maximum_word_length = 40

def list_files_recursive(result, path):
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir(follow_symlinks=False):
                list_files_recursive(result, f'{path}/{entry.name}')
            elif entry.is_file(follow_symlinks=False):
                result.append(f'{path}/{entry.name}')

def create_analysis(con, project_id, tempdir, extension):
    cur = con.cursor()
    s3_bucket = get_s3_bucket()
    files = []

    prev_ids = []
    for row in cur.execute("SELECT id FROM analysis WHERE project_id = ?", (project_id,)):
        prev_id, = row
        prev_ids.append(prev_id)

    print(f"Listing files in {tempdir}")
    list_files_recursive(files, tempdir)
    counts = defaultdict(int)
    filecount = 0
    wordcount = 0
    errorcount = 0
    for filename in files:
        try:
            if extension == None or filename.endswith(f'.{extension}'):
                with open(filename) as f:
                    for word in re.split("(?<=[a-z])(?=[A-Z])|[^a-zA-Z]+", f.read()):   # split on camelCase and non-alphabetic characters
                        if len(word) >= 2 and len(word) <= maximum_word_length:
                            counts[(word.lower(), filecount)] += 1
                            wordcount += 1
                    filecount += 1

        except Exception as e:
            errorcount += 1   # expected if we encounter a binary file
    print(f"Read {filecount} files, {errorcount} errors, {wordcount} words, {len(counts)} distinct words")
    cur.execute("INSERT INTO analysis(project_id) VALUES (?)", (project_id,))
    analysis_id = cur.lastrowid
    cur.executemany("INSERT INTO wordcount(analysis_id, word, file_number, count) VALUES (?,?,?,?)", ((analysis_id, word, file_number, count) for ((word,file_number),count) in counts.items()))
    con.commit()

    cur.executemany("DELETE FROM wordcount WHERE analysis_id = ?", ((prev_id,) for prev_id in prev_ids))
    cur.executemany("DELETE FROM analysis WHERE id = ?", ((prev_id,) for prev_id in prev_ids))
    con.commit()
    print(f"{len(prev_ids)} previous analyses discarded.")

