

import os
import argparse
import time
import random
import collections
import re
import gensim
import smart_open
import json
import multiprocessing
import numpy as np


def clean_func(func):
    func = func.lower().replace('\n', '')

    if '@0x' in func:
        return func[:func.index('@0x') + 3]

    return func


def preprocess(stack_trace):
    return [clean_func(f) for f in stack_trace.split(' | ')]

def should_skip(stack_trace):
    return 'xul.dll@' in stack_trace or 'XUL@' in stack_trace or 'libxul.so@' in stack_trace

def get_stack_traces_for_signature(fnames, signature):
    traces = set()

    for fname in fnames:
        with smart_open.smart_open(fname, encoding='iso-8859-1') as f:
            for line in f:
                data = json.loads(line)
                if data['signature'] == signature:
                    traces.add(data['proto_signature'])

    return list(traces)


#start = time()

import json

input_proto_signature = input("Enter proto_signature of stack trace-: ")

w2v_corpus = []  # Documents to train word2vec on (all stack traces)
wmd_corpus = []  # Documents to run queries against (stack trace corresponding to proto_signature entered bu user).
documents = []  # wmd_corpus, with no pre-processing (so we can see the original documents).
with smart_open.smart_open('firefox-crashes-2016-11-03.json') as data_file:
    for line in data_file:
        json_line = json.loads(line)
        
        # Pre-process document.
        text = json_line['text']  # Extract text from JSON object.
        text = preprocess(text)
        
        # Add to corpus for training Word2Vec.
        w2v_corpus.append(text)
        
        

#print 'Cell took %.2f seconds to run.' %(time() - start)

# Train Word2Vec on all the stack traces.
model = Word2Vec(w2v_corpus, workers=3, size=100)

# Initialize WmdSimilarity
from gensim.similarities import WmdSimilarity
num_best = 10
instance = WmdSimilarity(wmd_corpus, model, num_best=10)


sent = get_stack_traces_for_signature('firefox-crashes-2016-11-03.json',input_proto_signature)
query = preprocess(sent)

sims = instance[query] 

# Print the query and the retrieved documents, together with their similarities.
print 'Query:'
print sent
for i in range(num_best):
    print
    print 'sim = %.4f' % sims[i][1]
    print documents[sims[i][0]]








