import pandas as pd
import costants as cs
from langdetect import detect
import re


def select_only_keyword(df, keyword, ticker):
    """
    Remove rows where the text do not contain the keyword
    :param df:
    :param keyword:
    :param ticker:
    :return:
    """
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
        try:
            if detect(row['Text']) != 'en':
                df.drop(index, inplace=True)
                print(f'Line {index} dropped')
        except:
            df.drop(index, inplace=True)
            print(f'Line {index} dropped')
    return df


def remove_special_char(text):
    """
    Apply to the text all the RegEx to clean the tweet text
    :param text:
    :return:
    """
    # remove digits
    text = ''.join(i for i in text if not i.isdigit())
    # remove emoji
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # remove \n
    text = text.replace('\n', ' ')
    # remove non-ASCII character
    text = re.sub('([^\x00-\x7F])+', '', text)
    return text


def select_keyword(ticker):
    """
    Search the keyword to filter the list of tweets
    :param ticker:
    :return:
    """
    for target in cs.target_company:
        if target['ticker'] == ticker:
            return target['name']
    print('ERROR: Company not available')
    exit(1)


def save_file(ticker, df):
    """
    Save a DataFrame inside a JSON file call with ticker
    :param ticker:
    :param df:
    :return:
    """
    fname = '../data/filteredTweets_' + ticker + '_test.json'
    with open(fname, 'w') as f:
        print("Saved JSON: ", fname)
        df.to_json(fname, orient="records", lines=True)

def filter_tweets(path):
    """
    filter all the JSON files given by path and save a new files with the
    results
    :param path:
    :return:
    """
    # select ticker
    path_list = path.split('_')
    ticker = path_list[1]
    # selected keyword
    keyword = select_keyword(ticker)
    # import tweets
    df = pd.read_json(path, lines=True)
    # remove not useful columns
    df.drop(columns=['Tweet_ID', 'URL', 'Account_Name'], axis=1, inplace=True)
    # use readable datetime format
    df['Datetime'] = df['Datetime'].dt.strftime('%m-%d-%y')
    # keep lowercase
    df['Text'] = df['Text'].str.lower()
    # remove noisy tweets
    df = select_only_keyword(df, keyword, ticker)
    df = select_only_english(df)
    # remove special char
    df['Text'] = df['Text'].apply(remove_special_char)
    # save results on file
    save_file(ticker, df)


# TEST
if __name__ == "__main__":
    filter_tweets("../data/tweets_AMZN_2021-12-06_2021-12-09.json")


