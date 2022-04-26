#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import argparse
import logging
import json 

from gensim.models import Doc2Vec

from reader import MongoReader

logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO
_logger = logging.getLogger(__name__)

class Doc2VecAnalyser(object):
    def __init__(self, model, reader, topn=3):
        ''' init 
            :param model: Doc2Vec model
            :param reader: source reader object
            :param topn: specify number of most similar tags. default: 3
        '''
        self.doc2vec_model = Doc2Vec.load(model)
        self.reader = reader

    def analyse(self):
        ''' analyse '''
        for doc in self.reader.iterate():
            # doc[0] is the texts, while doc[1] is the tags.
            _logger.info("Title: %s" % doc.get('title'))
            _logger.info("Plots: %s" % doc.get('plot'))
            _logger.info("Actual Genres: %s" % doc.get('tags'))
            pred_vec = self.doc2vec_model.infer_vector(doc.get('texts'))
            pred_tags = self.doc2vec_model.docvecs.most_similar([pred_vec], topn=3)
            _logger.info("Most similar:  %s" % pred_tags)
            _logger.info("  \n\n ")
        return 


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Given a model file classify a collection.")
    parser.add_argument('--model', help="Specify input model file. default: doc2vec.model", default="./doc2vec.model")
    parser.add_argument('--db', help="Specify MongoDB db name. default:topics", default="topics")
    parser.add_argument('--coll', help="Specify MongoDB collection name", default="test")
    parser.add_argument('--mongoURI', help="Specify MongoDB URI for different server/ports", default="mongodb://localhost:27017")
    parser.add_argument('--limit', help="Specify a number of documents to classify. default:10", type=int, default=10)
    parser.add_argument('--topn', help="Specify a number of most similar tags. default:3", type=int, default=3)
    args = parser.parse_args()

    if not args.model:
        parser.print_help()
        sys.exit(0)

    reader = MongoReader(mongoURI=args.mongoURI, dbName=args.db, collName=args.coll, limit=args.limit)
    analyser = Doc2VecAnalyser(model=args.model, reader=reader)
    analyser.analyse()
