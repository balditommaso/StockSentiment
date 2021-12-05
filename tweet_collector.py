# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
import snscrape.modules.twitter as sntwitter
import pandas as pd

# Creating list to append tweet data to
tweets_list = []

# Using TwitterSearchScraper to scrape data and append tweets to list
for i, tweet in enumerate(
        sntwitter.TwitterSearchScraper('TSLA tesla since:2021-11-05 until:2021-12-05').get_items()):

    #counter
    print(i)

   # if tweet.likeCount > tot
    tweets_list.append([tweet.id, tweet.url, tweet.user.username, tweet.content, tweet.date, tweet.retweetCount,
                        tweet.likeCount, tweet.replyCount])

# Creating a dataframe from the tweets list above
tweets_df = pd.DataFrame(tweets_list, columns=['Tweet_ID', 'URL', "Account_Name", 'Text', 'Datetime','Number_Retweets', 'Number_Likes', 'Number_Comments'])
print(tweets_df)

fname = 'prova.json'

with open(fname, 'w') as f:
    print("Saved Json: ", fname)
    tweets_df.to_json(fname, orient="records", lines=True)