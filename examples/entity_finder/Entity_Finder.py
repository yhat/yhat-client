# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import numpy as np
import pandas as pd
import nltk

# <markdowncell>

# <h2>Named-entity recognition</h2>
# <p>In <a href="http://en.wikipedia.org/wiki/Natural_language_processing" title="natural language processing - wikipedia" target="_blank">natural language processing</a>, <a href="http://en.wikipedia.org/wiki/Named-entity_recognition" title="named entity recognition - wikipedia" target="_blank">entity recognition</a> problems are those in which the principal task is to identify irreducible elements within text like people, places, locations, products, companies, measurements (e.g. dollars, miles, percentages, etc.) and more.</p>

# <markdowncell>

# <h2>The Dataset</h2>
# <p>As an example, we'll look at text corpuses from <a href="http://www.tv.com" title="tv.com" target="_blank">tv.com</a> The dataset consists of user-submitted recaps of Law and Order episodes..</p>

# <codecell>

df = pd.read_csv('./episodes_and_recaps.txt', sep='|')

# <codecell>

print 'nrow: %d' % len(df)
print 'ncol: %d' % len(df.columns)
df

# <codecell>

print 'Number of episodes in the Law and Order franchise'
df.groupby(['show']).size()

# <markdowncell>

# <p>Because these are submitted by users, not every episode will have a recap / corpus.</p>

# <codecell>

text = df[df.corpus.notnull()].corpus.values[9]
print text[:500]

# <markdowncell>

# <h2>Extracting names of characters from the text</h2>
# <p>Suppose we wanted to know which neighborhoods were most often the scene of the crime in Law and Order or SVU. We could read through all the episode recaps submitted by users and look for neighborhoods mentioned. But there are 456 episodes spanning 20 seasons in the original Law and Order and 319+ episodes spanning 15 seasons. That's a lot of episode recaps to read through.</p>
# 
# <h2>Using NLTK and Python</h2>
# <p>For this example, we'll write a script to extract the named entities from these episode recaps programatically.</p>

# <markdowncell>

# <p>Our general strategy will be to transform our unstructured text data into structured data. To accomplish this, we'll be using several utilities found in Python's <a href="" title="nltk - natural language toolkit for python" target="_blank">NLTK</a> (Natural Language Toolkit) library, a package with lots of great functions and routines for tokenizing and learning text.</p>

# <markdowncell>

# <h4>Tokenize text into sentences</h4>
# <p>First things first. We need to break the corpus into individual sentences. This can be done using NLTK's <code>sent_tokenize</code> function (<a href="http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tokenize-module.html#sent_tokenize" title="nltk sent_tokenize function" target="_blank">read more here</a>).</p>

# <codecell>

help(nltk.sent_tokenize)

# <markdowncell>

# <p>The <code>sent_tokenize</code> function is pretty cool. Notice that NLTK knows that the period in "Mr. Daltry" isn't the end of a sentence? It'll also handle sentences that start w/ lowercase letters.</p>

# <codecell>

sentences = nltk.sent_tokenize(text)
print "\nFirst 2 sentences\n"
print sentences[0:2]

# <markdowncell>

# <p>As a rule, NLTK does a really good job of tokenization without a lot of fine tuning. If <em>you do</em> have some specific text that demands special behavior around tokenization, there are a lot of great options for adjusting and overriding the default behavior too.</p>

# <markdowncell>

# <h4>Tokenize sentences into words</h4>
# <p>Next, we need to tokenize each sentence into its individual words.</p>

# <codecell>

tokenized = [nltk.word_tokenize(sentence) for sentence in sentences]
print "First 20 words of the first sentence\n"
print tokenized[0][:20]

# <markdowncell>

# <h4>Label Parts of Speech</h4>
# <p>Finally, we need to label each word with its part of speech. This will enable us to discern nouns (and proper nouns) from everything else later on.</p>
# <p>A lot can--and has--been said about <a href="http://en.wikipedia.org/wiki/Part-of-speech_tagging" title="part of speech tagging - wikipedia" target="_blank">Part-of-speech tagging</a>. Since many of the details are outside the scope of this blog post, I'll go through some of the basics of POS tagging using NLTK and leave some cool references at the end for anybody interested to read more.</p>

# <markdowncell>

# <h4>NLTK's <code>pos_tag</code> function</h4>

# <markdowncell>

# <p>NLTK's <code>pos_tag</code> is NLTK's primary off-the-shelf tagger for parts of speech. It relies on the <a href="http://www.cis.upenn.edu/~treebank/" title="Penn Treebank annotates the linguistic structure of natural language text." target="_blank">Penn Treebank tagset</a> and encodes a list of tokens as tuples with shape <code>(tag, token)</code>.</p>

# <codecell>

help(nltk.pos_tag)

# <markdowncell>

# <p>If you don't have the Penn Treebank tagset installed, you can get it using NLTK's built-in downloader tool like so:</p>

# <codecell>

# import nltk
# nltk.download()

# <markdowncell>

# <p>Take the following sentence for example:</p>

# <codecell>

a = "Alan Shearer is the first player to score over a hundred Premier League goals."
a_sentences = nltk.sent_tokenize(a)
a_words     = [nltk.word_tokenize(sentence) for sentence in a_sentences]
a_pos       = [nltk.pos_tag(sentence) for sentence in a_words]
a_pos

# <markdowncell>

# <p>Take a look at the use of the word "over" in the above sentence. The <code>'IN'</code> tag in the tuple <code>('over', 'IN')</code> indicates that it's being used as a preposition in the phrase "over a hundred."</p>
# <p>Conversely, </p>

# <codecell>

b = "Hank Mardukas was over-served at the bar last night."
b_sentences = nltk.sent_tokenize(b)
b_words     = [nltk.word_tokenize(sentence) for sentence in b_sentences]
b_pos       = [nltk.pos_tag(sentence) for sentence in b_words]
b_pos

# <markdowncell>

# <p>This time, "over-served" is tagged as <code>'JJ'</code> (adjective). NLTK knows that "over" is part of the attributive adjective phrase describing Hank and the potentially embarassing state he found himself in at the bar last night.</p>
# 
# <p>We can apply this routine to our Law and Order episode recaps like so:</p>

# <codecell>

pos_tags  = [nltk.pos_tag(sentence) for sentence in tokenized]
print "First 10 (word, parts of speech) in the first sentence\n"
print pos_tags[0][:10]

# <markdowncell>

# <h2>Extracting the Entities</h2>
# <p>NLTK gives us some really powerful methods for isolating entities in text. One of the simplest and most powerful tools at our disposal is the <code>batch_ne_chunk</code> function which takes a list of tagged tokens and returns a list of named entity chunks.</p>
# 
# <p>You can chunk sentences by passing sentences that have been tagged with parts-of-speech to <code>batch_ne_chunk</code>.</p>

# <codecell>

named_entity_chunks =  nltk.batch_ne_chunk(pos_tags)
print sentences[0]
print named_entity_chunks[0][:9]

# <codecell>

print 'List of tagged tokens'
print [nltk.pos_tag(sentence) for sentence in tokenized][:1][0][:6]
print 
print 'List of entity chunks'
print nltk.batch_ne_chunk(pos_tags)[:1][0][:6]
print

# <markdowncell>

# <p>This is what we're after:</p>
# <pre><code>Tree('PERSON', [('Angela', 'NNP'), ('Jarrell', 'NNP')])</code></pre>
# <p>NLTK recognizes "Angela" and "Jarrell" as names, though it fails to identify them as <em>one name</em> ("Angela Jarrell"). If you wanted to treat <code>First</code> and <code>Last</code> names as a single name, there are ways to tune your classifier. Depending on the behavior you're shooting for, there could be a few ways to do it, so look to the NLTK docs for specifics.</p>

# <markdowncell>

# <h2>Pause for a second</h2>
# <p>So far we:</p>
# <ul>
#     <li>Took corpus of text and split it up into sentences using <code>sent_tokenize</code></li>
#     <li>Split up each tokenized sentence into word tokens using <code>word_tokenize</code></li>
#     <li>Tagged each part of speech using <code>pos_tag</code></li>
#     <li>Converted the tagged parts of speech tokens into entity chunks using <code>batch_ne_chunk</code></li>
# </ul>
# 
# <p>Let's wrap this routine into reusable functions.</p>

# <markdowncell>

# <h4>Helper to read `corpus` column without the other columns</h4>
# <p>Pretty simple. This'll let us read the top n non-null corpuses quickly.</p>

# <codecell>

# helper function to read in text corpuses only
def read_texts(f='./episodes_and_recaps.txt', n_samples=5):
    "returns non-null text corpuses for the top n rows"
    df = pd.read_csv(f,sep='|')
    df = df[df.corpus.notnull()]
    corpuses = df.corpus.head(n_samples).tolist()
    return corpuses

# <markdowncell>

# <h4>Take in raw text. Output tagged entity chunks.</h4>
# <p>Just copied and pasted the lines we already wrote into one function. This will puts a corpus thru the 4 operations we did above text => sentences => words => parts of speech => entity chunks. </p>

# <codecell>

def parts_of_speech(corpus):
    "returns named entity chunks in a given text"
    sentences = nltk.sent_tokenize(corpus)
    tokenized = [nltk.word_tokenize(sentence) for sentence in sentences]
    pos_tags  = [nltk.pos_tag(sentence) for sentence in tokenized]
    return nltk.batch_ne_chunk(pos_tags, binary=True)

# <markdowncell>

# <h4>Find all the unique named entities.</h4>
# <p>This one will extract named entities from the entity chunks.</p>

# <codecell>

def find_entities(chunks):
    "given list of tagged parts of speech, returns unique named entities"

    def traverse(tree):
        "recursively traverses an nltk.tree.Tree to find named entities"
        entity_names = []
    
        if hasattr(tree, 'node') and tree.node:
            if tree.node == 'NE':
                entity_names.append(' '.join([child[0] for child in tree]))
            else:
                for child in tree:
                    entity_names.extend(traverse(child))
    
        return entity_names
    
    named_entities = []
    
    for chunk in chunks:
        entities = sorted(list(set([word for tree in chunk
                            for word in traverse(tree)])))
        for e in entities:
            if e not in named_entities:
                named_entities.append(e)
    return named_entities

# <markdowncell>

# <h4>Test it out</h4>

# <codecell>

text = read_texts(n_samples=1)[0][:500]
print text

# <codecell>

entity_chunks  = parts_of_speech(text)
find_entities(entity_chunks)

# <markdowncell>

# <h2>This is cool. Now what?</h2>
# <p>Applications for text-based entity extraction are far ranging, from exploring product conversations on Facebook to uncovering terrorist plots in emails, to analyzing free-response answers in customer surveys. Once you've built and tuned a model for your particular use-case, you can use it to power your app or use it within your CRM via Yhat.</p>

# <markdowncell>

# <h4>Wrap the code you already wrote in a class</h4>
# <p>Define a subclass of <code>yhat.BaseModel</code>. Implement <code>require</code>, <code>transform</code>, and <code>predict</code> as usual. Here we require NLTK but not numpy or pandas since Yhat will load those for us by default.</p>

# <codecell>

from yhat import Yhat, BaseModel

# <codecell>

class NamedEntityFindr(BaseModel):
    def require(self):
        import nltk

    def transform(self, raw):
        "uses the parts_of_speech function we wrote earlier"
        rows = pd.Series(raw['data'])
        rows = rows.apply(parts_of_speech)
        return rows

    def predict(self, chunked):
        "uses the find_entities function we wrote earlier"
        res = chunked.apply(find_entities).values
        return {'entities': res.tolist()[0]} # returns a nice dictionary

# <markdowncell>

# <h4>Create an instance of that class</h4>
# <p>One super helpful feature of Yhat is that you can use any helper/utility functions you've written within your class. If you've referenced any functions from other parts of your script like the two we wrote, <code>parts_of_speech</code> and <code>find_entities</code>, you can pass those to your classifier when you create it by using the <code>udfs</code> argument. UDF is short for user defined function. This lets you explicitly tell Yhat which functions you want to use in production.</p>

# <codecell>

clf = NamedEntityFindr(
    udfs=[find_entities, parts_of_speech]
)

# <markdowncell>

# <h4>Test it out locally</h4>

# <codecell>

data = {'data': [text]}
print data

# <markdowncell>

# <p>On your local machine, you need to transform your data using the transform function you wrote before you can call predict. In production, Yhat will do the transformation for you.</p>

# <codecell>

print 'Results on my local machine'
transformed = clf.transform(data)
results = clf.predict(transformed)
print results

# <markdowncell>

# <p>Deploy to Yhat</p>

# <codecell>

yh = Yhat("YOUR USERNAME", "YOUR API KEY")

# <codecell>

print yh.upload("NamedEntityFindr", clf)

# <codecell>

[model for model in yh.show_models()['models'] if model['name'] == "NamedEntityFindr"]

# <codecell>

results_from_server = yh.raw_predict("NamedEntityFindr", 1, data)
results_from_server

# <codecell>

print 'sanity check.'
print 'results all match => %s' \
    % np.all(np.array(results['entities']) == np.array(results_from_server['prediction']['entities']))

# <markdowncell>

# <h2>Final Thoughts</h2>
# <ul>
#     <li><a href="http://nltk.googlecode.com/svn/trunk/doc/book/ch05.html" title="Categorizing and Tagging Words - NLTK docs" target="_blank">Categorizing and Tagging Words with NLTK</a> (NLTK docs)</li>
#     <li><a href="http://pixelmonkey.org/pub/nlp-training/" title="Just Enough NLP with Python" target="_blank">Just Enough NLP with Python</a> (slides)</li>
#     <li><a href="http://cdn.preterhuman.net/texts/science_and_technology/artificial_intelligence/Foundations%20of%20Statistical%20Natural%20Language%20Processing%20-%20Christopher%20D.%20Manning.pdf" title="Foundations of Statistical Natural Language Processing by Christopher Manning &amp; Hinrich Schiitze" target="_blank">Foundations of Statistical Natural Language Processing</a> by Christopher Manning &amp; Hinrich Schiitze (PDF)</li>
#     <li><a href="http://www.slideshare.net/japerk/nltk-in-20-minutes" title="NLTK in 20 minutes" target="_blank">http://www.slideshare.net/japerk/nltk-in-20-minutes</a> (Slideshare)</li>
#     <li><a href="http://jpr.sagepub.com/content/50/3/319.full.pdf" title="Shifting sands : Explaining and predicting phase shifts by dissident organizations" target="_blank">Shifting sands : Explaining and predicting phase shifts by dissident organizations</a> (PDF)</li>
#     <li><a href="http://www.cs.uic.edu/~liub/FBS/SentimentAnalysis-and-OpinionMining.pdf" title="sentiment analysis and opinion mining" target="_blank">the Sentiment Analysis book</a></li>
#     <li><a href="http://www.cs.uic.edu/~liub/FBS/CustomerReviewData.zip" title="customer review data zipfile" target="_blank">Customer Review Dataset</a> (Covers 5 products, .zip file)</li>
#     <li><a href="http://www-nlp.stanford.edu/software/" title="The Stanford Natural Language Processing Group" target="_blank">The Stanford Natural Language Processing Group</a></li>
# </ul>

# <codecell>


