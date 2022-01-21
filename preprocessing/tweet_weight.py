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


if __name__ == '__main__':
    fname = '../data/TEST_FILTER.json'
    with open(fname, mode='r') as file:
        df = pd.read_json(path_or_buf=file, orient='records', lines=True)
    print(df)
    after_df = set_tweets_weight(df)
    print('-------------------------------------')
    print(after_df)
