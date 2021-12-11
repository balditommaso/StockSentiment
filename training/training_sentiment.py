import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import re
from langdetect import detect
from bs4 import BeautifulSoup

def removeSpecialChars(tweet):
    '''
    Removes special characters which are specifically found in tweets.
    '''
    # Converts HTML tags to the characters they represent
    soup = BeautifulSoup(tweet, "html.parser")
    tweet = soup.get_text()

    # Convert www.* or https?://* to empty strings
    tweet = re.sub(r'((www\.[^\s]+)|(https?://[^\s]+))', '', tweet)

    # Convert @username to empty strings
    tweet = re.sub(r'@[^\s]+', '', tweet)

    # Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

    # Trims the tweet
    tweet = tweet.strip('\'"')

    return tweet


def removeAllNonAlpha(tweet):
    '''
    Remove all characters which are not alphabets, numbers or whitespaces.
    '''
    tweet = re.sub('[^A-Za-z ]+', ' ', tweet)

    # Remove additional white spaces
    tweet = re.sub(r'[\s]+', ' ', tweet)

    return tweet

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
            ## drop also the lines that cause errors
            df.drop(index, inplace=True)
            print(f'Line {index} dropped')
    return df

def train():
    df = pd.read_json('tsla.json', lines=True)
    df = df['Text']
    df.to_csv('tsla.csv', index=False)
    """
    #    df = df.sample(frac=0.02)
    df['Text'] = df['Text'].str.lower()
    df['Text'] = df['Text'].apply(removeSpecialChars)
    df['Text'] = df['Text'].apply(removeAllNonAlpha)
    df = select_only_english(df)
    
    
    """

    training_set, test_set = train_test_split(df, test_size=0.2)

    print(len(training_set))

    # Pipeline Classifier
    clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', MultinomialNB()),
    ])

    # Training the Pipeline Classifier
    clf.fit(training_set.text, training_set.label)

    #Testing of the Pipeline
    docs_test = test_set['text']
    print(docs_test)
    predicted = clf.predict(docs_test)

    #Extracting statistics and metrics
    accuracy = accuracy_score(predicted, test_set['label'])
    print("Accuracy on test set: ", accuracy)
    print("Metrics per class on test set:")

    print("Confusion matrix:")
    metrics.confusion_matrix(test_set['label'], predicted)

    print(metrics.classification_report(test_set.label, predicted,
        target_names=["0","1", "2"]))

train()