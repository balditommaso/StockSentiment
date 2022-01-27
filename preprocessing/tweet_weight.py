import pandas as pd


def set_tweets_weight(df):

    max_follower = 200000
    min_follower = 1000

    df['Weight'] = ((df['Number_Follower'] * min_follower) / max_follower)  # edo exp?
    for index, row in df.iterrows():
        if row['Number_Follower'] < min_follower:
            df.drop(index, inplace=True)

    df.sort_values(['Number_Follower'], inplace=True, ascending=False)
    return df
