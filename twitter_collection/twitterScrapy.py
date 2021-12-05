import requests
import pandas as pd


def connect_to_twitter():
    """
    Connect to thw Twitter API
    :return: (dictionary) header to ask request at the API
    """
    Twitter_Bearer_Token = 'AAAAAAAAAAAAAAAAAAAAAHAEWQEAAAAAFihOgI%2FZ6JFeQi58PUigamVLABc%3D1hMBYqoivDjrSD0l3AgkW' \
                           'YH3iRMw34gfP1ReEV8pj3GSpYLd86'
    return {"Authorization": "Bearer {}".format(Twitter_Bearer_Token)}


def make_request(headers, keywords):
    """
    make request to the api and build a DataFrame which will be save
    as JSON in a file

    :param headers: to auth with the api
    :param keywords: list of keywords to filter the tweets
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    with open("tweets.json", mode='w', encoding='utf-8') as tweets_json:
        for key in keywords:
            params = "query=" + key + " lang:en is:quote is:verified" \
                 "&tweet.fields=created_at,text&max_results=100"
            response = requests.request("GET", url, params=params, headers=headers).json()
            df = make_df(response)
            df.to_json(tweets_json, orient='records', lines=True)


def make_df(response):
    return pd.DataFrame(response['data'])


if __name__ == "__main__":
    TARGET_TAGS = ['amazon', 'tesla', 'google', 'apple', 'microsoft']
    # TARGET_TAGS = ['AMZN', 'TSLA', 'GOOG', 'GOOGL', 'AAPL', 'MSFT']
    headers = connect_to_twitter()
    make_request(headers, TARGET_TAGS)
