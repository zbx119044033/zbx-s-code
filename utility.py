#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter
import numpy as np
from gensim.models import word2vec
import sys
import os
from pymongo import MongoClient
from functional import seq
reload(sys)
sys.setdefaultencoding('utf-8')


try:
    client = MongoClient("mongodb://lionking:Tv6pAzDp@60.205.187.223:27017/Simba?authMechanism=SCRAM-SHA-1")
    db_mongo = client.Simba
    collection_out = db_mongo.faq
    collection_in = db_mongo.sentence_vector
except Exception, e:
    print e
    sys.exit()

corpus_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "models/corpus.model")
model = word2vec.Word2Vec.load(corpus_path)
flag_w = {'n': 1.2, 'nz': 1, 'vn': 0.9, 'uj': 0.5, 'v': 0.8, 'r': 0.5, 'm': 0.6, 'a': 1, 'c': 0.9, 'l': 1, 'd': 0.8,
          'y': 0.5, 'nr': 1.2, 'i': 1.2}

for item in collection_out.find():
    question = seq(nlp.cut(item['question'].strip())).filter(lambda t: t[1] != u'x').list()

    def process_segment(word_flag):
        word = word_flag[0]
        flag = word_flag[1]
        if unicode(word) in model:
            return model[unicode(word)] * flag_w[flag] if flag in flag_w else model[unicode(word)] * 1

    vector = seq(question).map(process_segment).list()
    sentence_vec = sum(vector).reshape(1, -1) / len(question)
    collection_in.insert_one({"vector": vector, "answer_id": item['_id']})

print 'job done !'
