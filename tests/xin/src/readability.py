import numpy
import nlputil
from docstructure import *

def average_word_per_sentence(doc):
    return float(len(doc.pwords))/len(doc.sents)

def average_syllable_per_word(doc):
    nsyl = [x.numsyl() for x in doc.pwords]
    return numpy.mean(nsyl)

def percentage_of_monosyllable_word(doc):
    return float(sum([x.numsyl()==1 for x in doc.pwords])) / len(doc.pwords)

def flesch_reading_ease(doc):
    sl = average_word_per_sentence(doc)
    wl = average_syllable_per_word(doc) * 100
    return 206.835 - 0.846 * wl - 1.015 * sl
    
def flesch_kinciad_grade_level(doc):
    sl = average_word_per_sentence(doc)
    wl = average_syllable_per_word(doc)
    return -15.59 + 11.80 * wl + 0.39 * sl

def fog_grade_level(doc):
    sl = average_word_per_sentence(doc)
    pmw = percentage_of_monosyllable_word(doc)
    return 3.0680 + 0.877 * sl + 0.984 * pmw

# apply readability metric to each paragraph in a document
# save the readability to each Paragraph object and the Document object
# metric: a function
def paragraph_readability(doc, metric=flesch_kinciad_grade_level):
    for x in doc.pars:
        x.readability = metric(x)
    doc.par_readability = [x.readability for x in doc.pars]
    return doc.par_readability
