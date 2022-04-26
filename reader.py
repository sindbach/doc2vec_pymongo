#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pymongo
import logging
import re

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords

import nltk
nltk.download('wordnet')

import nltk
nltk.download('omw-1.4')

from nltk.stem import WordNetLemmatizer


logging.basicConfig(format='%(levelname)s : %(message)s', level=logging.INFO)
logging.root.level = logging.INFO
_logger = logging.getLogger(__name__)

class Reader(object):
    ''' Source reader object feeds other objects to iterate through a source. '''
    def __init__(self):
        ''' init '''
        exclude_stops = set(('.', '(', ')'))
        self.stop = set(stopwords.words('english')) - exclude_stops
        self.wn_lemmatizer = WordNetLemmatizer()

    def prepare_words(self, text):
        ''' Prepare text 
        '''
        # lower cased all text
        texts = text.lower()
        # tokenize
        texts = re.split(r'(?![\.|\$])[^\w\d]', texts)
        texts = [w.strip('.') for w in texts]
        # remove words that are too short
        texts = [w for w in texts if not len(w)<3]
        # remove words that are not alphanumeric and does not contain at least one character
        texts = [w for w in texts if w.isalnum()]
        # remove numbers only
        texts = [w for w in texts if not w.isdigit()]
        # remove stopped words
        texts = [w for w in texts if not w in self.stop]
        # remove duplicates 
        seen = set()
        seen_add = seen.add 
        texts = [w for w in texts if not (w in seen or seen_add(w)) ]
        # lemmatize
        texts = [self.wn_lemmatizer.lemmatize(w) for w in texts]        
        return texts

    def iterate(self):
        ''' virtual method '''
        pass


class MongoReader(Reader):
    def __init__(self, dbName=None, collName=None, 
                 mongoURI="mongodb://localhost:27017", limit=None):
        ''' init
            :param mongoURI: mongoDB URI. default: localhost:27017
            :param dbName: MongoDB database name.
            :param collName: MongoDB Collection name. 
            :param limit: query limit
        '''
        Reader.__init__(self)
        self.conn = None
        self.mongoURI = mongoURI
        self.dbName = dbName
        self.collName = collName
        self.limit = limit
        self.fields = ['Title', 'Plot', 'Actors', 'Genre']
        self.key_field = 'Genre'
        self.return_fields = ['Title', 'Plot', 'Actors']

    def get_value(self, value):
        ''' convinient method to retrive value.
        '''
        if not value:
            return value
        if isinstance(value, list):
            return ' '.join([v.encode('utf-8', 'replace').decode('utf-8', 'replace') for v in value])
        else:
            return value.encode('utf-8', 'replace').decode('utf-8', 'replace')

    def iterate(self):
        ''' Iterate through the source reader '''
        if not self.conn: 
            try:
                self.conn = pymongo.MongoClient(self.mongoURI)[self.dbName][self.collName]
            except Exception as ex:
                raise Exception("ERROR establishing connection: %s" % ex)

        if self.limit: 
            projection = {}
            for key in self.fields:
                projection[key] = 1
            cursor = self.conn.aggregate([{"$sample":{"size":self.limit}}, 
                                          {"$project":projection}])
        else:
            cursor = self.conn.find({}, self.fields)

        for doc in cursor:
            content = ""
            for f in self.return_fields:
                content +=" %s" % (self.get_value(doc.get(f)))
            texts = self.prepare_words(content)
            tags = doc.get(self.key_field).split(',')
            tags = [t.strip() for t in tags]
            doc = { "texts": texts, "tags": tags, "title": doc.get('Title'), "plot": doc.get('Plot')}
            yield doc

if __name__ == "__main__":
    pass