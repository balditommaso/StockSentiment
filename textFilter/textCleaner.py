import pandas as pd
from langdetect import detect
import re


def lowercase_dataset(df):
    for index, row in df.iterrows():
        row['Text'] = row['Text'].lower()


def select_only_keyword(df, keyword, ticker):
    print("Removing text without keyword or ticker ...")

    for index, row in df.iterrows():
        find_keyword = row['Text'].find(keyword)
        find_ticker = row['Text'].find(ticker)
        if find_keyword == -1 and find_ticker == -1:
            df.drop(index, inplace=True)
            print(f'Line {index} dropped')
    return df


def select_only_english(df):
    """
    Method that drops all the rows containing non-english tweets
    :param pd.DataFrame:
    :return:
    """
    print("Removing non-english tweets ...")

    for index, row in df.iterrows():
        if detect(row['Text']) != 'en':
            df.drop(index, inplace=True)
            print(f'Line {index} dropped')
    return df


def remove_puntuaction(text):
    return re.sub(r'[^\w\s]', '', text)


def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def remove_digits(text):
    return ''.join(i for i in text if not i.isdigit())


def select_only_ASCII(text):
    return text.encode('ascii', 'ignore')


if __name__ == "__main__":
    # import tweets
    df = pd.read_json("../data/tweets_AMZN_2021-12-06_2021-12-09.json", lines=True)
    # keep lowercase
    df['Text'] = df['Text'].str.lower()
    # remove noisy tweets
    df = select_only_keyword(df, 'amazon', 'AMZN')
    df = select_only_english(df)
    # remove punctuation
    ####### REMOVE URL and USERNAMES
    df['Text'] = df['Text'].apply(remove_puntuaction)
    df['Text'] = df['Text'].apply(remove_emoji)
    df['Text'] = df['Text'].str.replace('\n', ' ')
    df['Text'] = df['Text'].apply(remove_digits)
    df['Text'] = df['Text'].apply(select_only_ASCII)
    print(df['Text'])

    # create JSON file (test)
    fname = "../data/tweets_AMZN_filter_test.json"
    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        df.to_json(fname, orient="records", lines=True)
