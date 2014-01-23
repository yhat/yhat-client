import pandas as pd
import numpy as np
import sys

df = pd.read_csv("data/beer_reviews.csv")
df.head()


beer_1, beer_2 = "Dale's Pale Ale", "Fat Tire Amber Ale"

beer_1_reviewers = df[df.beer_name==beer_1].review_profilename.unique()
beer_2_reviewers = df[df.beer_name==beer_2].review_profilename.unique()
common_reviewers = set(beer_1_reviewers).intersection(beer_2_reviewers)
print "Users in the sameset: %d" % len(common_reviewers)
list(common_reviewers)[:10]

def get_beer_reviews(beer, common_users):
    mask = (df.review_profilename.isin(common_users)) & (df.beer_name==beer)
    reviews = df[mask].sort('review_profilename')
    reviews = reviews[reviews.review_profilename.duplicated()==False]
    return reviews

beer_1_reviews = get_beer_reviews(beer_1, common_reviewers)
beer_2_reviews = get_beer_reviews(beer_2, common_reviewers)

cols = ['beer_name', 'review_profilename', 'review_overall', 'review_aroma', 
        'review_palate', 'review_taste']
beer_2_reviews[cols].head()


# choose your own way to calculate distance
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.metrics.pairwise import manhattan_distances
from scipy.stats.stats import pearsonr


ALL_FEATURES = ['review_overall', 'review_aroma', 'review_palate', 'review_taste']
def calculate_similarity(beer1, beer2):
    # find common reviewers
    beer_1_reviewers = df[df.beer_name==beer1].review_profilename.unique()
    beer_2_reviewers = df[df.beer_name==beer2].review_profilename.unique()
    common_reviewers = set(beer_1_reviewers).intersection(beer_2_reviewers)

    # get reviews
    beer_1_reviews = get_beer_reviews(beer1, common_reviewers)
    beer_2_reviews = get_beer_reviews(beer2, common_reviewers)
    dists = []
    for f in ALL_FEATURES:
        dists.append(euclidean_distances(beer_1_reviews[f], beer_2_reviews[f])[0][0])
    
    return dists

calculate_similarity(beer_1, beer_2)

# get a list of all the beers we have
beers = df.beer_name.unique().tolist()

simple_distances = []
for beer1 in beers:
    print "\ttraining", beer1
    for beer2 in beers:
        if beer1 != beer2:
            row = [beer1, beer2] + calculate_similarity(beer1, beer2)
            simple_distances.append(row)

cols = ["beer1", "beer2", "overall_dist", "aroma_dist", "palate_dist", "taste_dist"]
simple_distances = pd.DataFrame(simple_distances, columns=cols)
simple_distances.tail()


def calc_distance(dists, beer1, beer2, weights):
    mask = (dists.beer1==beer1) & (dists.beer2==beer2)
    row = dists[mask]
    row = row[['overall_dist', 'aroma_dist', 'palate_dist', 'taste_dist']]
    dist = weights * row
    return dist.sum(axis=1).tolist()[0]

def normalize_dists(dists):
    newdists = []
    dist_min = min(row[2] for row in dists)
    dist_max = max(row[2] for row in dists)
    for (b1, b2, dist) in dists:
        dist = (dist - dist_min) / (dist_max - dist_min)
        dist = 100 * (1 - round(dist, 2))
        newdists.append((b1, b2, dist))

    return newdists

weights = [2, 1, 1, 1]


from yhat import Yhat, BaseModel

class BeerRec(BaseModel):
    
    def transform(self, raw_data):
        beer = raw_data['beer']
        weights = raw_data.get("weights", [1, 1, 1, 1])
        # normalize the weights so they sum to 1.0
        weights = [float(w) / sum(weights) for w in weights]
        print "making recs for: " + beer
        return (beer, weights)
        
    def predict(self, data):
        beer, weights = data
        results = []
        for beer_cmp in self.beers:
            if beer!=beer_cmp:
                dist = calc_distance(self.simple_distances, beer, beer_cmp, weights)
                results.append((beer, beer_cmp, dist))
        dists = sorted(results, key=lambda x: x[2])
        # return dists
        return normalize_dists(dists)

yh = Yhat({USERNAME}, {APIKEY})
myBeerModel = BeerRec(simple_distances=simple_distances, beers=beers, 
                udfs=[calc_distance, normalize_dists])

if raw_input("Deploy? (y/N)")=="y":
    print yh.deploy("BeerRec", myBeerModel)

print yh.predict("BeerRec", None, {"beer": "Coors Light"})




