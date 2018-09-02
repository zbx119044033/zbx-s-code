#!/usr/bin/python
# -*- coding:utf-8 -*-

import numpy as np
from gensim.models import word2vec
from functional import seq
import jieba
from jieba import posseg
from sklearn.metrics.pairwise import cosine_similarity
jieba.load_userdict('entitydict.txt')

model = word2vec.Word2Vec.load('corpus.model')
flag_w = {'n': 1.6, 'nz': 1.8, 'vn': 0.9, 'uj': 0.5, 'v': 0.8, 'r': 0.5, 'm': 0.6, 'a': 1, 'c': 0.9, 'l': 1, 'd': 0.8,
          'y': 0.1, 'nr': 1, 'i': 1.2, 'zg': 0.1}


def cut(text):
    mixWords = []
    for word, flag in jieba.posseg.cut(text):
        print word, flag
        mixWords.append((word, flag))
    return mixWords


def w2v(text):
    question = seq(cut(text.strip())).filter(lambda t: t[1] != u'x').list()

    def process_segment(word_flag):
        word = word_flag[0]
        flag = word_flag[1]
        if unicode(word) in model:
            return model[unicode(word)] * flag_w[flag] if flag in flag_w else model[unicode(word)] * 1
        else:
            return np.zeros(200,)

    vector = seq(question).map(process_segment).list()
    sentence_vec = sum(vector).reshape(1, -1) / len(question)
    return sentence_vec


def culculate(text1, text2):
    v1 = w2v(text1)
    v2 = w2v(text2)
    return cosine_similarity(v1, v2)[0][0]


if __name__ == '__main__':
    t1 = u'我想知道重疾险怎么买呢？'
    t2 = u'如何买重疾险？'
    print culculate(t1, t2)
