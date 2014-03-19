import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))


# load in our data and split it into a training and test set
df = pd.read_csv("/Users/glamp/repos/yhat/test-scripts/models/data/tweets_with_html.csv").head(100)
df['total_favs_and_rts'] = df.favorite_count + df.retweet_count
df['liked_content'] = np.where(df.total_favs_and_rts > 1, 1, 0)

df['istrain'] = np.random.uniform(size=len(df)) <= 0.8
train = df[df.istrain]
test = df[-df.istrain]

vec = TfidfVectorizer(max_features=500, smooth_idf=True)
train_twitter_tfidf = vec.fit_transform(train.text)

# create and train a classifier
nbayes = MultinomialNB(fit_prior=False)
nbayes.fit(train_twitter_tfidf, train.liked_content.tolist())

# prep the test data, then create a confusion matrix to examine the results
test_twitter_tfidf = vec.transform(test.text)
preds = nbayes.predict(test_twitter_tfidf)
print pd.crosstab(test.liked_content, preds)

from yhat import Yhat, YhatModel, preprocess


class TwitterRanker(YhatModel):

    @preprocess(in_type=dict, out_type=dict)
    def execute(self, data):
        tweet = data['tweet_content']
        data = vec.transform([tweet])
        pred = nbayes.predict(data)
        prob = nbayes.predict_proba(data)
        prob = {
            "ham": round(prob[0][0], 4),
            "spam": 1 - round(prob[0][0], 4)
        }
        return {"pred": pred[0], "prob": prob}


