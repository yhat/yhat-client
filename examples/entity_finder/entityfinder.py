#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
entityfinder.py

Created by Yhat, Inc. on 2013-06-29.
Copyright (c) 2013.

This script deploys a named-entity extractor to Yhat for the purposes of text
classification.

Named entities include: names of persons, organizations, locations,
expressions of times, quantities, monetary values, percentages, etc.

The script builds a model using NLTK and Yhat. EntityFinder is a subclass
of yhat.BaseModel which implements `require` to ensure loading of NLTK, while
Yhat loads pandas and numpy by default.

EntityFinder implements self.transform which expects a dictionary as follows:

{'data':
    ["David Moore, a wealthy Manhattanite, comes rushing into the lobby of his apartment building, carrying his comatose wife Joan in his arms.",
    "A woman is bludgeoned to death with a paving stone in a subway station, and the police use data stored from her transit pass and her stolen credit cards to find the killer."]
}

Each sentence in the list will be parsed by self.transform.
Parts of speech are extracted using NLTK and the resulting list of
tokenized parts of speech sentences are passed to self.predict.

self.predict iterates over the chunked sentences each of which is made up of
an element tree. self.predict recursively traverses each tree until it finds
all nodes which are named entities:
    tree.node == 'NE'

The script builds test cases from text-based episode summaries of
Law and Order episodes submitted by users on TV.com.

    episodes_and_recaps.txt
"""

import nltk
import numpy as np
import pandas as pd
from yhat import Yhat, BaseModel

class EntityFinder(BaseModel):
    def require(self):
        import nltk

    def transform(self, raw):

        def parts_of_speech(corpus):
            sentences = nltk.sent_tokenize(corpus)
            tokenized = [nltk.word_tokenize(sentence) for sentence in sentences]
            pos_tags  = [nltk.pos_tag(sentence) for sentence in tokenized]
            return pos_tags

        rows = pd.Series(raw['data'],name='corpus')
        tagged_sentences = rows.apply(parts_of_speech)
        chunked = tagged_sentences.apply(
            lambda x: nltk.batch_ne_chunk(x, binary=True)
        )
        return chunked

    def predict(self, chunked):
        def find_entities(tree):
            entity_names = []
            if hasattr(tree, 'node') and tree.node:
                if tree.node == 'NE':
                    entity_names.append(' '.join([child[0]
                            for child in tree]))
                else:
                    for child in tree:
                        entity_names.extend(find_entities(child))
            return entity_names

        named_entities = []
        for sentence in chunked:
            for tree in sentence:
                for entity in find_entities(tree):
                    if entity not in named_entities:
                        named_entities.append(entity)

        return named_entities

yh = Yhat("YOUR USERNAME", "YOUR PASSWORD")
my_models = yh.show_models()

def latest_version(name, models=my_models):
    models = models['models']
    return max([model['version'] for model in models if model['name'] == name])

def make_test_cases(n_samples=5):
    df = pd.read_csv('./episodes_and_recaps.txt',sep='|')
    df = df[df.corpus.notnull()]
    corpuses = df.corpus.head(n_samples).tolist()
    return {'data': corpuses}

name = "EntityFinder"
clf = EntityFinder()
yh.upload(name, clf)

raw_data = make_test_cases()
v = latest_version(name)

print 'On my local machine...'
local_results = np.array(clf.predict(clf.transform(raw_data)))
print local_results
print '*' * 79

print 'On the server...'
server_results = np.array(yh.predict(name, version=v,data=raw_data))
print server_results
print '*' * 79

print 'Results are Exactly Equal'
print np.all(server_results == local_results)


