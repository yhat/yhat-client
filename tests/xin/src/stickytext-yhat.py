#!/usr/bin/env python
# This is a duplicate of the original stickytext.py, wrapped as a yhat model.
from yhat import Yhat, YhatModel , preprocess
import sys
from docstructure import *
from readability import *
from cohesion import *
from nlputil import *
import cStringIO

class StickyTextYhat (YhatModel):
  REQUIREMENTS="PyHyphen==2.0.4"
  
  def hprint(self, s=""):
    self.fout.write(s+"<br/>")
  def hprint2(self, s=""):
    self.fout.write(s+'\r')

  @preprocess(in_type=dict, out_type=dict)
  def execute(self, data):
    dstr = data['mytext']
    metric = data['metric']
    scale = data['scale']
    good = data['good']
    bad = data['bad']

    self.fout = cStringIO.StringIO()

    # Start Computing and Output
    self.fout.write("<label><h2>Results</h2></label>")

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
    self.fout.write("<label><h4>Readability Statistics</h4></label>")
    self.hprint("Number of words: %d"%length)
    self.hprint("Number of sentences: %d"%numsent)
    self.hprint("Average words per sentence: %.2f"%sl)
    self.hprint("Average syllables per word: %.2f"%wl)
    self.hprint("Flesch Reading Ease: %.2f"%fre)
    self.hprint("Flesch-Kinciad Grade Level: %.2f"%fkgl)
    self.hprint("FOG Grade Level: %.2f"%fgl)

    # cohesion metrics
    wo = word_overlap_cohesion(d, is_local=True, label_sent=False)
    wog = word_overlap_cohesion(d, is_local=False, label_sent=False)
    vo = word_dist_cohesion(d, is_local=True, label_sent=False)
    vog = word_dist_cohesion(d, is_local=False, label_sent=False)
    #wn = wordnet_cohesion(d, is_local=True, label_sent=False)
    self.fout.write("<label><h4>Cohesion Statistics</h4></label>")
    self.hprint("Word Overlap Local: %.3f"%wo)
    self.hprint("Word Overlap Global: %.3f"%wog)
    self.hprint("Freq. Dist. Local: %.3f"%vo)
    self.hprint("Freq. Dist. Global: %.3f"%vog)
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
        self.fout.write("<label><h4>Paragraphic Cohesion Plot</h4></label>")
        self.hprint()
        self.hprint2('<script type="text/javascript" src="wz_jsgraphics.js"></script>')
        self.hprint2('<script type="text/javascript" src="line.js">')
        self.hprint2('</script>')
        self.hprint2('<div id="lineCanvas" style="overflow: auto; position:relative;height:300px;width:400px;"></div>')
        self.hprint2('<script type="text/javascript">')
        self.hprint2('var g = new line_graph();')
        for i in range(len(parcoh)):
            self.hprint2("g.add('%d', %f);"%(i+1, parcoh[i]*100))
        self.hprint2('g.render("lineCanvas", "Paragraphs");')
        self.hprint2('</script>')

    # display text annotation/highlight
    met(d, is_local=is_local, num_label=max(int(good), int(bad)), label_sent=True)
    self.fout.write("<hr>")
    self.fout.write("<label><h2>Cohesion Highlighter</h2></label>")
    if int(good)>0:
        self.fout.write('<span class="bold red">Red: Cohesive </span>')
    if int(bad)>0:
        self.fout.write('<span class="yellow-background">Yellow: Not Cohesive</span>')

    self.hprint2('<div style="width:600px;"><p align="left">')
    d.print_html(self.fout, int(good), int(bad))
    self.hprint2('</p></div>')
    # End Computing and OUtput 

    output = self.fout.getvalue()
    self.fout.close()
    return { "html_output": output }

yh = Yhat("rongxin1989@gmail.com", "ff7bb725be9e4a32af286f464b316a23", "http://umsi.yhathq.com/")
print yh.deploy("StickyText", StickyTextYhat, globals())
