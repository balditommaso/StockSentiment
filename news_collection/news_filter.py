import os, json
import pandas as pd
from langdetect import detect


def lang_review(df):
    """
    Method that drops all the rows containing non-english news
    :param pd.DataFrame:
    :return:
    """
    print("Removing non-english news ...")

    for index, row in df.iterrows():
        news_text = row[2] + " " + row[4]
        if detect(news_text) != 'en':
            df.drop(index, inplace=True)

    return df


if __name__ == "__main__":
    path_to_json = '../data/'
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    # For each ticker
    for file in json_files:
        print("Loading: ", file)
        df = pd.read_json(path_to_json + file, lines=True)

        df.drop_duplicates(subset=['headline'], keep='first')

        df = lang_review(df)

        fname = path_to_json + "processed" + file

        with open(fname, 'w') as f:
            print("Saved Json: ", fname)
            df.to_json(fname, orient="records", lines=True)
