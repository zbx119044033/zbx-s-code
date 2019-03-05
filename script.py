#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter
import logging
import numpy as np
from gensim.models import word2vec
import types
import pymongo
import jieba.posseg as pseg
import re
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()


with open('stopwords.txt','r') as f:
    stopwords = f.read().split('\n')
jieba.load_userdict('entitydict.txt')

'''
连接mongo获取数据
'''
def mongo():
    client = pymongo.MongoClient('mongodb://xxx')
    db = client.get_database('Simba')
    collection = db.get_collection('faq')
    pattern = re.compile(r'\n|\\&quot')
    q_a = []
    for item in collection.find():
        eachQA = []
        question = re.sub(pattern,'',item['question'])
        eachQA.append(question)
        answer = re.sub(pattern,'',item['answer'][0])
        # eachQA.append(question)
        eachQA.append(answer)
        q_a.append(eachQA)
    print 'ok'
    for i in range(len(q_a)):
        print q_a[i][0]
        print q_a[i][1]
    with open('q&a_6W.txt','a') as f:
        for i in range(len(q_a)):
            f.write(q_a[i][0].encode('utf-8'))
            f.write('\n')
            f.write(q_a[i][1].encode('utf-8'))
            f.write('\n')
    print 'finish'

'''
训练word2vec模型
'''
# 主程序
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
sentences = word2vec.Text8Corpus( r"F:\similar\all_words_7_24.txt")  # 加载语料
model = word2vec.Word2Vec(sentences, size=200,min_count=3,min_alpha=0.025)  # 训练skip-gram模型; 默认window=5
# 保存模型，以便重用
model.save(r"F:\similar\datebao_no_eng_7_24.model")

'''
加载word2vec模型及测试
'''
def test_word2vec():
    model = word2vec.Word2Vec.load('F:\similar\datebao_no_eng.model')
    y2 = model.most_similar(u"叫", topn=100)  # 20个最相关的
    print u"和good最相关的词有：\n"
    for item in y2:
        print item[0], item[1]
    print "--------\n"
    y1 = model.similarity(u"黄曲霉素",u"爱情")
    print u"woman和man的相似度为：", y1
    print "--------\n"
    print model[u'黄曲霉素']

'''
获得q_a
'''
with open('q&a.txt','r') as f:
    q_a_1 = f.read().split('\n')
q = []
a = []
for i in range(len(q_a_1)):
    if i%2 == 0:
        q.append(q_a_1[i])
    else:
        a.append(q_a_1[i])
q_a = []
for i in range(len(q)):
    q_a.append([q[i],a[i]])


'''
分词加生成各种文件
'''
with open('stopwords.txt','r') as f:
    stopwords = f.read().split('\n')
jieba.load_userdict('entitydict.txt')

all_words = []
q_all_words = []
a_all_words = []
count = 1
with open('q&a.txt','r') as f:
    lines = f.read().split('\n')
    for line in lines:
        print line
        seg_list = pseg.cut(line.strip())
        list1 = []
        if count % 2 != 0:
            for word,flag in seg_list:
                if word.encode('utf-8') not in stopwords and word != ' ':
                    all_words.append(word.encode('utf-8'))
                    list1.append(word.encode('utf-8')+'_'+flag)
            q_all_words.append(list1)
        if count % 2 ==0:
            for word,flag in seg_list:
                if word.encode('utf-8') not in stopwords and word != ' ':
                    all_words.append(word.encode('utf-8'))
                    list1.append(word.encode('utf-8')+'_'+flag)
            a_all_words.append(list1)
        count += 1

print count,len(q_all_words),len(a_all_words)
print a_all_words[0]
print q_all_words[0]


with open('sep_questions_7_24.txt','a') as f:
    for line in q_all_words:
        f.write(' '.join(line))
        f.write('\n')

with open('sep_answers.txt','a') as f:
    for line in a_all_words:
        f.write(' '.join(line))
        f.write('\n')
print 'finish'

with open('questions.txt','a') as f:
    for i in range(len(q_a)):
        f.write(q_a[i][0])
        f.write('\n')

with open('answers.txt','a') as f:
    for i in range(len(q_a)):
        f.write(q_a[i][1])
        f.write('\n')

f = open('q&a.txt','r')
w = open('all_words_7_24.txt','a')
partten = re.compile(r'\w*',re.L)

while True:
    line = f.readline()
    if line == '':
        break
    line = re.sub(partten,'',line)
    seg_list = jieba.lcut(line.strip(), cut_all=False)
    list1 = []
    for word in seg_list:
        if word.encode('utf-8') not in stopwords and word != '':
            list1.append(word.encode('utf-8'))
    w.write(' '.join(list1))
    w.write('\n')
w.close()
f.close()
print 'finish'
