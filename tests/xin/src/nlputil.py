import re
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.corpus import wordnet_ic

# refer to:
# [WordNet] http://nltk.googlecode.com/svn/trunk/doc/howto/wordnet.html

def remove_punctuation_from_words(words):
    # retain only those tokens that have at least a letter or number
    nonPunct = re.compile('.*[A-Za-z0-9].*')
    return [w for w in words if nonPunct.match(w.text)]

def remove_stopwords(words):
    return [w for w in words if not w.text.lower() in stopwords.words("english")]

# Note: plain word texts are returned instead of Word objects
_stemmer = nltk.PorterStemmer()
def stem_lower_words(words):
    return [_stemmer.stem(w.text.lower()) for w in words]

def noun_synsets(word):
    return wn.synsets(str(word), pos=wn.NOUN)

# return the max similarity between all possible sense combinations of two words
# simtype should be one of the following:
#   select_path_similarity()
#   OR
#   select_resnick_similarity()
def max_similarity(word1, word2, simtype):
    nsx = noun_synsets(word1)
    nsy = noun_synsets(word2)
    if len(nsx)==0 or len(nsy)==0:
        return 0
    else:
        return max(simtype(x, y) for x in nsx for y in nsy)

# returns a simtype function for use of max_similarity(), same below
# very slow
def select_path_similarity():
    return lambda x, y: x.path_similarity(y)

# extremely slow
def select_lch_similarity():
    return lambda x, y: x.lch_similarity(y)

_brown_ic = wordnet_ic.ic('ic-brown.dat')
# very slow
def select_resnick_similarity():
    return lambda x, y: x.res_similarity(y, _brown_ic)
