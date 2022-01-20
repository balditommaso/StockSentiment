import pandas as pd

def set_tweets_weight(df):
    df['Weight'] = 0

    max_follower = 200000
    min_follower = 1000
    like_pt = 1
    comment_pt = 1
    retweet_pt = 1

    for index, row in df.iterrows():
        if row['Number_Follower'] < min_follower:
            df.drop(index, inplace=True)

        start_value = (row['Number_Follower'] * min_follower) / max_follower
        row['Weight'] = start_value + like_pt*row['Number_Likes'] + comment_pt*row['Number_Comments'] + retweet_pt*row['Number_Retweets']

        if row['Number_Follower'] >= max_follower:
            row['Weight'] = 1000

    df.drop(columns=['Number_Follower', 'Number_Likes', 'Number_Comments', 'Number_Retweets'], inplace=True)
    return df


if __name__ == '__main__':
    fname = '../data/TEST_FILTER.json'
    with open(fname, mode='r') as file:
        df = pd.read_json(path_or_buf=file, orient='records', lines=True)
    print(df)
    after_df = set_tweets_weight(df)
    print('-------------------------------------')
    print(after_df)
