#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import sys
import argparse
import logging
import json 
import os
from random import shuffle
from gensim.models.doc2vec import TaggedDocument
from gensim.models import Doc2Vec
from sklearn.model_selection import train_test_split
from reader import MongoReader
import numpy as np 

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO
_logger = logging.getLogger(__name__)

class BuildDoc2VecModel(object):
    ''' Build Doc2Vec model file. 
    '''
    def __init__(self, fileoutput, dm=0, size=150, negative=5, hs=0, min_count=2, 
                 workers=3, numpasses=10, numiter=10):
        ''' init
            :param fileoutput: output model file
            :param dm: defines the algorithm. 0 = PV-DBOW, 1 = PV-DM . default=0
            :param size: the dimensionality of the feature vectors. default=100.
            :param negative: if > 0, negative sampling will be used, the int for negative 
                             specifies how many “noise words” should be drawn
            :param hs: if 0 (default), hierarchical sampling will not be used
            :param min_count: ignore all words with total frequency lower than this
            :param worker: threads to train the model
            :param numpasees: number of passes
            :param numiter: number of iteration 
        '''
        self.fileoutput = fileoutput
        self.dm=dm
        self.size = size
        self.negative = negative
        self.hs = hs
        self.min_count = min_count
        self.workers = workers
        self.numpasses = numpasses
        self.numiter = numiter

        self.d2v_model = None
        self.test_sents = None

    def build(self, reader):
        ''' Build model
            :param reader: source Reader object
        '''
        # Build TaggedDocument objects from the documents. 
        sentences = [TaggedDocument(words=doc.get('texts'), tags=doc.get('tags')) for doc in reader.iterate()] 
        
        # Split model into 90/10 training and test
        train_sents, self.test_sents = train_test_split(sentences, test_size=0.1, random_state=42) 

        model= Doc2Vec(dm=self.dm, 
                       vector_size=self.size,
                       negative=self.negative, 
                       hs=self.hs, 
                       min_count=self.min_count, 
                       workers=self.workers,
                       epochs=self.numiter)

        model.build_vocab(sentences)

        alpha = 0.025
        min_alpha = 0.001
        alpha_delta = (alpha - min_alpha) / self.numpasses

        for i in range(self.numpasses):
            shuffle(sentences)
            model.alpha = alpha
            model.min_alpha = alpha
            model.train(sentences, total_examples=model.corpus_count, epochs=self.numiter)
            alpha -= alpha_delta

        model.save(self.fileoutput)
        self.d2v_model = model
        return 

    def score_similiarity(self):
        ''' Test similarity using Jaccard
        '''
        score = 0.0 
        for test_sent in self.test_sents: 
            pred_vec = self.d2v_model.infer_vector(test_sent.words)
            pred_tags = self.d2v_model.docvecs.most_similar([pred_vec], topn=len(test_sent.tags))
            _logger.info("text: %s\n" % test_sent.words)
            _logger.info("Predicted tags: %s\n" % pred_tags)
            _logger.info("Actual tags: %s\n" % test_sent.tags)
            sim = jaccard_similarity(test_sent.tags, [x[0] for x in pred_tags])
            score += sim

        _logger.info("Jaccard similarity score: %s" % float(float(score)/len(self.test_sents)))

def jaccard_similarity(labels, preds):
    lset = set(labels)
    pset = set(preds)
    return len(lset.intersection(pset)) / len(lset.union(pset))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doc2Vec model builder.")
    parser.add_argument('--model', help="Specify output model file. default: doc2vec.model", default="./doc2vec.model")
    parser.add_argument('--db', help="Specify MongoDB db name.", default="topics")
    parser.add_argument('--coll', help="Specify MongoDB collection name.", default="movies")
    parser.add_argument('--mongoURI', help="Specify MongoDB URI for different server/ports. default=localhost:27017", default="mongodb://localhost:27017")
    parser.add_argument('--limit', help="Specify the limit of records to read from source. default: None", type=int, default=None)

    parser.add_argument('--featsize', help="Specify number of feature vectors. default 150", type=int, default=150)
    parser.add_argument('--negative', help="Specify how many noise words should be drawn for negative sampling.", type=int, default=5)
    parser.add_argument('--hsampling', help="Specify flag for hierarchy sampling. 0/1", type=int, default=0)
    parser.add_argument('--mincount', help="Specify the minimum words frequency to be accounted", type=int, default=2)
    parser.add_argument('--workers', help="Specify the number of workers for training models", type=int, default=1)
    parser.add_argument('--numpasses', help="Specify number of passes/iteration", type=int, default=20)

    args = parser.parse_args()
    if not (args.db or args.coll):
        parser.print_help()
        sys.exit(1)

    builder = BuildDoc2VecModel(fileoutput=args.model)
    reader = MongoReader(mongoURI=args.mongoURI, dbName=args.db, collName=args.coll, limit=args.limit)
    builder.build(reader)
    builder.score_similiarity()
