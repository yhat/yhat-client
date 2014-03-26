#!/usr/bin/env python
from docstructure import *
from readability import *
from cohesion import *
from nlputil import *

s = "Today I am going to drink some beer. The beer comes from Chicago.\n\nMy wife, Lily, likes the bear. She says she would often love watching me drinking. What a lovely wife. I sometimes think the word lovely is kind of very lovely. It makes me sometimes want to cry. Crying in the open air. Air pollution is bad.\n\nI would so much want this to end as soon as possible. My life. This is so counterintuitive. I call it counterintuitivitabilism."

d = Document(s)

"""
print "[WHOLE DOCUMENT]"
print d
print "[PAR 0]"
print d.pars[0]
print "[PAR 1]"
print d.pars[1]
print "[SENT 1 PAR 1]"
print d.pars[1].sents[1]
print "[PWORD 1 PAR 1]"
print d.pars[1].pwords[1]
print "[WORD 2 SENT 1 PAR 1]"
print d.pars[1].sents[1].words[2]
print "[WORD 0 SENT 1 PAR 1]"
print d.pars[1].sents[1].words[0]
print "[NUMSYL WORD 0 SENT 1 PAR1]"
print d.pars[1].sents[1].words[0].numsyl()
"""

# Test number of syllables
#for i in d.words:
#    print str(i)+' '+str(i.numsyl())

print "\n[DOC LENGTH]"
print len(d.pwords)
print average_word_per_sentence(d)
print average_syllable_per_word(d)


print "\n[FLESCH READING EASE]"
print flesch_reading_ease(d)

print "\n[FLESCH-KINCIAD GRADE-LEVEL]"
print flesch_kinciad_grade_level(d)

print "\n[FOG GRADE-LEVEL]"
print fog_grade_level(d)

print "\n[EXAMPLE STEMMED WORDS]"
print ' '.join([str(x) for x in d.sents[5].scwords])


print "\n[JACCARD INDEX]"
print jaccard_index(d.sents[0], d.sents[1], lambda x:x.scwords)
print jaccard_index(d.sents[0], d.sents[1], lambda x:x.cwords)
print jaccard_index(d.sents[0], d.sents[1], lambda x:x.pwords)


print "\n[WORD OVERLAP COHESION]"
print word_overlap_cohesion(d, True, lambda x:x.cwords)
print word_overlap_cohesion(d, True, lambda x:x.scwords)
print word_overlap_cohesion(d, False, lambda x:x.cwords)
print word_overlap_cohesion(d, False, lambda x:x.pwords)

print "\n[WORD FREQ DIST COHESION]"
print word_dist_cohesion(d, True, lambda x:x.scwords)
print word_dist_cohesion(d, False, lambda x:x.scwords)

#print "\n[TEST POS-TAG]"
# d.pos_tag()
# print ' '.join([str(x) for x in d.pars[0].nouns])

#print "\n[WORDNET-BASED SIMILARITY]"
#print max_similarity('dog', 'umbrella', select_resnick_similarity())
#print wordnet_cohesion(d)

#print "\n[SENTENCE PAIR ON PARAGRAPH]"
#print sentence_pairs(d)
#print sentence_pairs(d.pars[0])

#print "\n[COHESION OF A PARAGRAPH]"
#print word_overlap_cohesion(d.pars[1])
#print word_dist_cohesion(d.pars[1])
#print wordnet_cohesion(d.pars[0])
#print d.pars[1]

print "\n[PARAGRAPH-WISE COHESION]"
paragraph_cohesion(d, metric=word_dist_cohesion)
#paragraph_cohesion(d, metric=wordnet_cohesion, word_type=lambda x: x.nouns)
print ' '.join([str(x) for x in d.par_cohesion])

#print "\n[PARAGRAPH-WISE READABILITY]"
#par_re = paragraph_readability(d)
#print ' '.join([str(x) for x in d.par_readability])

print "\n[SENTENCE GOOD/BAD LABELS]"
print '\n'.join(['[GOOD=%d] %s'%(x.howgood, x.text) for x in d.sents if x.howgood>0])
print '\n'.join(['[BAD=%d] %s'%(x.howbad, x.text) for x in d.sents if x.howbad>0])

print "\n[EVERY SENTENCE]"
for s in d.sents:
    print s.text
