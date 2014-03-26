#!/usr/bin/env python
import sys
from docstructure import *
from readability import *
from cohesion import *
from nlputil import *
import cStringIO

argv0, infile, metric, scale, good, bad = sys.argv
fin = open(infile)
dstr = fin.read()
fin.close()

fout = cStringIO.StringIO()
def hprint(s=""):
    fout.write(s+"<br/>")
def hprint2(s=""):
    fout.write(s+'\r')

# Start Computing and Output

fout.write("<label><h2>Results</h2></label>")

# load document
d = Document(dstr)


# readability metrics
length = len(d.pwords)
numsent = len(d.sents)
sl = average_word_per_sentence(d)
wl = average_syllable_per_word(d)
fre = flesch_reading_ease(d)
fkgl = flesch_kinciad_grade_level(d)
fgl = fog_grade_level(d)
fout.write("<label><h4>Readability Statistics</h4></label>")
hprint("Number of words: %d"%length)
hprint("Number of sentences: %d"%numsent)
hprint("Average words per sentence: %.2f"%sl)
hprint("Average syllables per word: %.2f"%wl)
hprint("Flesch Reading Ease: %.2f"%fre)
hprint("Flesch-Kinciad Grade Level: %.2f"%fkgl)
hprint("FOG Grade Level: %.2f"%fgl)

# cohesion metrics
wo = word_overlap_cohesion(d, is_local=True, label_sent=False)
wog = word_overlap_cohesion(d, is_local=False, label_sent=False)
vo = word_dist_cohesion(d, is_local=True, label_sent=False)
vog = word_dist_cohesion(d, is_local=False, label_sent=False)
#wn = wordnet_cohesion(d, is_local=True, label_sent=False)
fout.write("<label><h4>Cohesion Statistics</h4></label>")
hprint("Word Overlap Local: %.3f"%wo)
hprint("Word Overlap Global: %.3f"%wog)
hprint("Freq. Dist. Local: %.3f"%vo)
hprint("Freq. Dist. Global: %.3f"%vog)
#hprint("WordNet Local: %.3f"%wn)

# plot cohesion curve
# Refer to: http://www.dynamicdrive.com/dynamicindex11/linegraph.htm
met = None
if metric != '0':
    if metric == '1':
        met = word_overlap_cohesion
    elif metric == '2':
        met = word_dist_cohesion
    elif metric == '3':
        met = wordnet_cohesion
    if scale == '1':
        is_local = True
    elif scale =='2':
        is_local = False
    parcoh = paragraph_cohesion(d, metric=met, is_local=is_local)
    fout.write("<label><h4>Paragraphic Cohesion Plot</h4></label>")
    hprint()
    hprint2('<script type="text/javascript" src="wz_jsgraphics.js"></script>')
    hprint2('<script type="text/javascript" src="line.js">')
    hprint2('</script>')
    hprint2('<div id="lineCanvas" style="overflow: auto; position:relative;height:300px;width:400px;"></div>')
    hprint2('<script type="text/javascript">')
    hprint2('var g = new line_graph();')
    for i in range(len(parcoh)):
        hprint2("g.add('%d', %f);"%(i+1, parcoh[i]*100))
    hprint2('g.render("lineCanvas", "Paragraphs");')
    hprint2('</script>')

# display text annotation/highlight
met(d, is_local=is_local, num_label=max(int(good), int(bad)), label_sent=True)
fout.write("<hr>")
fout.write("<label><h2>Cohesion Highlighter</h2></label>")
if int(good)>0:
    fout.write('<span class="bold red">Red: Cohesive </span>')
if int(bad)>0:
    fout.write('<span class="yellow-background">Yellow: Not Cohesive</span>')

hprint2('<div style="width:600px;"><p align="left">')
d.print_html(fout, int(good), int(bad))
hprint2('</p></div>')
# End Computing and OUtput 

print fout.getvalue()
fout.close()
