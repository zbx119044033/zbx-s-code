# -*- coding:utf-8 -*-

import gensim
import logging
from functional import seq
import jieba
import io
import re
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
with io.open('sentiment2.txt', 'r', encoding='utf-8') as fr:
    sentences = []
    for line in fr.readlines():
        lis = line.strip().split()
        sentence = seq(lis[1:]).map(lambda w: w.strip()).reduce(lambda w1, w2: w1 + ' ' + w2 + ' ').strip()
        sentences.append(sentence)
print "read finished"

with io.open('sentiment3.txt', 'w', encoding='utf-8') as fw:
    for line in sentences:
        fw.write(line + '\n')
print "write finished"


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = gensim.models.word2vec.Text8Corpus('sentiment3.txt')
model = gensim.models.Word2Vec(sentences, min_count=1, size=100, workers=1)
model.save('test_sim')  # save the model
"""
model = gensim.models.Word2Vec.load('test_sim')
print(model.similarity(u'不需要', u'不需'))
