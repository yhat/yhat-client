#!/usr/bin/env python
from docstructure import *
from cohesion import *
from readability import *
from nlputil import *
import random

docs = []
for i in range(10):
    fin = open('paper/'+str(i+1)+'.txt')
    dstr = fin.read()
    fin.close()
    docs.append(Document(dstr))

# coh[document](wc wc_shuffle dc dc_shuffle)
coh = []
for d in docs:
    wc = word_overlap_cohesion(d)
    dc = word_dist_cohesion(d)
    d_new = Document(d.text)
    random.shuffle(d_new.sents)
    wc_new = word_overlap_cohesion(d_new)
    dc_new = word_dist_cohesion(d_new)
    coh.append((wc, wc_new, dc, dc_new))

dis = ['Biology', 'Civil Engineering', 'Economics', 'Education', 'English', 'History', 'Industrial Engineering', 'Linguistics', 'Mechanical Engineering', 'Environment']

for i in range(len(coh)):
    disc = dis[i]
    x,y,z,t = coh[i]
    print '%s & %.4f & %.4f & %.4f & %.4f \\\\'%(disc, x, y, z, t)

