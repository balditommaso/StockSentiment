import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

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
            if detect(row['text']) != 'en':
                df.drop(index, inplace=True)
                print(f'Line {index} dropped')
        except:
            ## drop also the lines that cause errors
            df.drop(index, inplace=True)
            print(f'Line {index} dropped')
    return df


def train():
    df = pd.read_csv('news_with_sentiment.csv')

    #Code for data preprocessing
    #    df = df.sample(frac=0.02) to use when the dataset is too large
    #    df = df['text']
    df['text'] = df['text'].str.lower()
    df['text'] = df['text'].apply(removeSpecialChars)
    df['text'] = df['text'].apply(removeAllNonAlpha)
    #df = select_only_english(df)

    #df.to_csv('training_set_to_label.csv', index=False)


    training_set, test_set = train_test_split(df, test_size=0.2, random_state=11)


    # Pipeline Classifier
    clf = Pipeline([
        ('vect', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', XGBClassifier()),   # XGBClassifier è il migliore in acc ma basso positive recall
                                    # Random Forest Classifier, Logistic Regression e SVC sono buoni (0.75 acc)
                                    # MultinomialNB e BernoulliNB meno buoni (0.67 acc)
    ])

    # Training the Pipeline Classifier
    clf.fit(training_set.text, training_set.target)

    #Testing of the Pipeline
    predicted = clf.predict(test_set['text'])

    #Extracting statistics and metrics
    accuracy = accuracy_score(predicted, test_set['target'])
    print("Accuracy on test set: ", accuracy)
    print("Metrics per class on test set:")

    print("Confusion matrix:")
    metrics.confusion_matrix(test_set['target'], predicted)

    print(metrics.classification_report(test_set['target'], predicted,
        target_names=["positive", "neutral", "negative"]))

    # Save the classifier
    #joblib.dump(clf, 'sentiment_classifier.pkl')


train()