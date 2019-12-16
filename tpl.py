import re
import os
import csv
import json
import gzip
import shutil
from langdetect import detect
from validate_utf8 import find_utf8_errors
from langdetect.lang_detect_exception import *


def check_language(lang, s):
    if detect(s) == lang:
        return True
    else:
        return False


def replace_token(token, s):
    if token == '#':
        s = re.sub(r'#[^ ]*', '$HASHTAG', s)
    elif token == '@':
        s = re.sub(r'@[^ ]*', '$MENTION', s)
    elif token == 'url':
        s = re.sub(r'htt[^ ]*', '$URL', s)
        s = re.sub(r'[^ ]*.ly[^ ]*', '$URL', s)
    return s


def transform_gz_csv(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        files = filenames

    for f in files:
        with gzip.open(path + '/' + f, 'rb') as f_in:
            with open(f[0:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        with open(f[0:-3], 'rb') as f_out:
            for line in f_out.readlines():
                if find_utf8_errors(line):
                    continue
                json_line = json.loads(line.decode("utf-8"))
                with open(org + '.csv', 'a') as csv_file:
                    fieldnames = ['organisation', 'tweet']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    try:
                        if(check_language(lang, json_line['full_text'])):
                            writer.writerow({'organisation': org,
                                         'tweet': json_line['full_text'].replace('\n', '  ')})
                    except LangDetectExpception:
                        continue

        os.remove('./' + f[0:-3])


def remove_duplicates(file, destination):
    with open(file, 'r') as in_file, open(destination, 'w') as out_file:
        writer = csv.writer(out_file)
        seen = set()
        try:
            for line in csv.reader(in_file):
                if line[1] in seen:
                    continue

                seen.add(line[1])
                writer.writerow(line)
        except Exception as ex:
            print(ex)


def remove_RT(file, destination):
    with open(file, 'r') as in_file, open(destination, 'w') as out_file:
        writer = csv.writer(out_file)
        regexp = re.compile(r'RT @')
        try:
            for line in csv.reader(in_file):
                if regexp.search(line[1]):
                    continue
                writer.writerow(line)
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    BASE_PATH = '/Users/gusy/DOCTORADO/'
    DATASET_PATH = BASE_PATH + 'Data/Tweets/cleaned/'
    DESTINATION_PATH = BASE_PATH + 'Data/Tweets/processed/ablation/nothing/'
    orgs = ['boeing', 'deloitte', 'microsoft', 'verizon']
    for org in orgs:
        # remove_RT(DATASET_PATH + org + '_noDuplicates.csv',
        #                   DESTINATION_PATH + org + '_cleaned.csv')
        with open(DATASET_PATH + org + '_cleaned.csv', 'r') as inp, open(DESTINATION_PATH + org + '_nothing.csv', 'w') as out:
            writer = csv.writer(out)
            for row in csv.reader(inp):
                row[1] = replace_token('#', row[1])
                row[1] = replace_token('url', row[1])
                row[1] = replace_token('@', row[1])
                writer.writerow(row)
