import json
import plotly
import pandas as pd

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
nltk.download(['omw-1.4','punkt', 'wordnet', 'averaged_perceptron_tagger','stopwords'])
from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
import plotly.graph_objs as go
# from sklearn.externals import joblib
from sqlalchemy import create_engine

from sklearn.base import BaseEstimator, TransformerMixin
import joblib

def tokenize(text):
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)

    return clean_tokens
class StartingVerbExtractor(BaseEstimator, TransformerMixin):

    # Custom transformer to extract starting verb
    def starting_verb(self, text):
        sentence_list = nltk.sent_tokenize(text)
        for sentence in sentence_list:
            pos_tags = nltk.pos_tag(tokenize(sentence))
            first_word, first_tag = pos_tags[0]
            if first_tag in ['VB', 'VBP'] or first_word == 'RT':
                return True
        return False

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_tagged = pd.Series(X).apply(self.starting_verb)
        return pd.DataFrame(X_tagged)

class StartingNounExtractor(BaseEstimator, TransformerMixin):
    # Custom transformer to extract starting Noun
    def starting_noun(self, text):
        sentence_list = nltk.sent_tokenize(text)
        for sentence in sentence_list:
            pos_tags = nltk.pos_tag(tokenize(sentence))
            first_word, first_tag = pos_tags[0]
            if first_tag in ['NN', 'NNS', 'NNP', 'NNPS'] or first_word == 'RT':
                return True
        return False

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X_tagged = pd.Series(X).apply(self.starting_noun)
        return pd.DataFrame(X_tagged)

# load data
engine = create_engine('sqlite:///./data/DisasterResponse.db')
df = pd.read_sql_table('DisasterResponseTable', engine)

# load model
model = joblib.load("./models/classifier.pkl")

def return_figures():
    """Creates two plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the two plotly visualizations

    """
    
    graph_one = []
    category_names = df.iloc[:,4:].columns.values.tolist()
    value_1 = [df[df[category]==1][category].value_counts()[1] for category in category_names]
    value_0 = [df[df[category]==0][category].value_counts()[0] for category in category_names]
    graph_one.append(
        Bar(
        name = '1',
        x = category_names,
        y =  value_1,        
      )
    )
    graph_one.append(
        Bar(
        name = '0',
        x = category_names,
        y =  value_0,
       
      )
    )
    layout_one = dict(title = 'Distribution of Message Categories',
                xaxis = dict(title = "Category",),
                yaxis = dict(title = "Count"),
                )

    graph_two = [] 
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)

    graph_two.append(
      Bar(
        x = genre_names,
        y = genre_counts,
      )
    )

    layout_two = dict(title = 'Distribution of Message Genres',
                xaxis = dict(title = "Genre",),
                yaxis = dict(title = "Count"),
                )


    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    
    
    return figures

