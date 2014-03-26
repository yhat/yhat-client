import math
import nltk
import numpy
import itertools
import nlputil
from docstructure import *

# return a list of sentence pairs
# doc: either a Document or a Paragraph, any object that has sents attribute
# usage: for x,y = sentence_pair(..): ...
def sentence_pairs(doc, is_local=True):
    if is_local:
        return [(doc.sents[i], doc.sents[i+1]) 
            for i in range(0, len(doc.sents)-1)]
    else:
        return [(doc.sents[i], doc.sents[j])
            for i, j in itertools.combinations(range(len(doc.sents)), 2)]

# lables the given number of sentence pairs with highest score and lowest score
# i.e., at most 2*num sentences will be labeled good, and 2*num bad
# the result is directly written as a property of each Sentence object
# This function will override any previous labels on Sentence objects.
def label_sentence(doc, sent_pairs, score, num):
    pair_score = [(sent_pairs[i], score[i]) for i in range(len(sent_pairs))]
    pair_score = sorted(pair_score, key=lambda x:x[1])
    # reset all labels
    for x in doc.sents:
        x.howbad = 0
        x.howgood = 0
    # label bad sentences
    for i in range(0, min(num, len(sent_pairs))):
        (x, y), s = pair_score[i]
        if x.howbad==0:
            x.howbad = i+1
        if y.howbad==0:
            y.howbad = i+1
    # label good sentences
    for i in range(max(0, len(sent_pairs)-num), len(sent_pairs)):
        (x, y), s = pair_score[i]
        x.howgood = len(sent_pairs)-i
        y.howgood = len(sent_pairs)-i

# apply a sentence pairwise metric to any pair of sentences in a document
# similarity_metric could be jaccard_index, or cosine_similarity, or max_max_similarity
def apply_cohesion(doc, is_local, word_type, similarity_metric, num_label, label_sent):
    if len(doc.sents) < 2: return 0
    sent_pairs = sentence_pairs(doc, is_local)
    score = [similarity_metric(x, y, word_type) for x, y in sent_pairs]
    if label_sent:
        label_sentence(doc, sent_pairs, score, num_label)
    return numpy.mean(score)

# measuring word overlapping a pair of sentences
# words_type should be a function gotten from words_typed()
def jaccard_index(sent1, sent2, word_type):
    word_set = lambda x: set([y.text for y in word_type(x)])
    set1 = word_set(sent1)
    set2 = word_set(sent2)
    if len(set1)==0 and len(set2)==0:
        return 0.0
    else:
        return len(set1.intersection(set2)) / float(len(set1.union(set2)))


# measuring document cohesion based on word overlapping (jaccard index)
def word_overlap_cohesion(doc, is_local=True, word_type=lambda x: x.scwords, num_label=2, label_sent=True):
    return apply_cohesion(doc, is_local, word_type, jaccard_index, num_label, label_sent)

# return a frequency distribution dictionary of words
def word_frequency(words):
    return nltk.FreqDist([x.text for x in words])

# return the cosine between two vectors, stored as dictionary objects
def cosine_vectors(vector1, vector2):
    prod = 0.0
    v1_sq = 0.0
    v2_sq = 0.0
    for x in vector1:
        y = vector1[x]
        v1_sq += y * y
        if x in vector2:
            prod += y * vector2[x]
    for x in vector2:
        y = vector2[x]
        v2_sq += y * y
    if v1_sq == 0 or v2_sq == 0:
        return 0
    else:
        return prod / math.sqrt(v1_sq * v2_sq)

# measuring word frequency distribution similarity between a pair of sentences
def cosine_similarity(sent1, sent2, word_type):
    vector1 = word_frequency(word_type(sent1))
    vector2 = word_frequency(word_type(sent2))
    return cosine_vectors(vector1, vector2)

# meausring document cohesion
def word_dist_cohesion(doc, is_local=True, word_type=lambda x: x.scwords, num_label=2, label_sent=True):
    return apply_cohesion(doc, is_local, word_type, cosine_similarity, num_label, label_sent)

# measuring max_max_similarity between any sense combination between any word pair of a pair of sentences
# By default: word_type = lambda x: x.nouns
# Simtype should be nlputil.select_path_similarity() or alike, see nlputil.py for more options
_simtype = nlputil.select_resnick_similarity()
def max_max_similarity(sent1, sent2, word_type):
    words1 = word_type(sent1)
    words2 = word_type(sent2)
    if len(words1)==0 or len(words2)==0:
        return 0
    else:
        return max([nlputil.max_similarity(x, y, _simtype) 
            for x in words1 for y in words2])

# measuring WordNet-based cohesion using max_max_similarity
# caution: extremely slow
def wordnet_cohesion(doc, is_local=True, word_type=lambda x: x.nouns, num_label=2, label_sent=True):
    if not doc.pos_tagged:
        doc.pos_tag()
    return apply_cohesion(doc, is_local, word_type, max_max_similarity, num_label, label_sent)

# apply a given cohesion measure to each paragraph of a document
# and update the cohesion to each Paragraph object, and save the result
# as a list to the Document object
def paragraph_cohesion(doc, is_local=True, word_type=lambda x:x.scwords,
                       metric=word_dist_cohesion):
    for x in doc.pars:
        x.cohesion = metric(x, is_local, word_type, label_sent=False)
    doc.par_cohesion = [x.cohesion for x in doc.pars]
    return doc.par_cohesion
