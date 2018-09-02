#!/usr/bin/python
# -*- coding:utf-8 -*-

from multiprocessing import Pool
import os
from operator import itemgetter
import numpy as np
from gensim.models import word2vec
import jieba.posseg as pseg
import types
import jieba
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.getdefaultencoding()


cos_similar = {}
model = word2vec.Word2Vec.load('F:\similar\datebao_no_eng.model')
flag_w = {'x': 1.6, 'n': 1.2, 'nz': 1, 'vn': 1, 'uj': 0.5, 'v': 0.91, 'r': 0.5, 'm': 1, 'a': 1, 'c': 1, 'l': 1,
          'd': 0.8, 'y': 0.5}


# 获得all_sep_questions_arr
def get_all_sep_questions_arr():
    # flag_w = {'x':1.6,'n':1.5,'nz':1.6,'vn':1.6,'uj':0.01,'v':1.6,'r':0.4,'m':0.4,'a':0.5,'c':0.5,'l':0.6}
    # flag_w = {'x':2.5,'n':2.5,'nz':1.6,'vn':2.5,'uj':0.01,'v':2,'r':1,'m':1,'a':1,'c':1,'l':1}
    all_sep_questions = []
    with open('sep_questions.txt', 'r') as f:
        list2 = f.read().split('\n')
    for line in list2:
        line = line.split(' ')
        all_sep_questions.append(line)
    all_sep_questions_arr = []
    for each_question in all_sep_questions:
        line_arr = np.zeros((1, 200), dtype='float32')
        count = 0.0
        flag_sum = 0.0
        for word_f in each_question:
            word_f = word_f.split('_')
            word = word_f[0]
            flag = word_f[1]
            if u'%s' % word in model:
                count += 1
                if flag_w.has_key(flag):
                    line_arr += (model[u'%s' % word] * flag_w[flag])
                    flag_sum += flag_w[flag]
                else:
                    line_arr += (model[u'%s' % word] * 1)
                    flag_sum += 1
        all_sep_questions_arr.append(line_arr / len(each_question))
        # all_sep_questions_arr.append(line_arr / flag_sum)
        # all_sep_questions_arr.append(line_arr/count)
    return all_sep_questions, all_sep_questions_arr


# 获得q_a
def get_q_a():
    with open('q&a.txt', 'r') as f:
        q_a_1 = f.read().split('\n')
    q = []
    a = []
    for i in range(len(q_a_1)):
        if i % 2 == 0:
            q.append(q_a_1[i])
        else:
            a.append(q_a_1[i])
    q_a = []
    for i in range(len(q)):
        q_a.append([q[i], a[i]])
    return q_a


# 辅助函数计算余弦距离
def vector_cosine(num, v1, v2):
    # print 'Run task %s (%s)...' % (num, os.getpid())
    return (num,1 + v1.dot(v2.T) / (1 + np.sqrt(v1.dot(v1.T)) * np.sqrt(v2.dot(v2.T))))

'''
测试
'''
# def test(self, text, threshold):
#     seg_list = jieba.lcut(text.strip(), cut_all=False)
#     seg_words = []
#     for word in seg_list:
#         if word.encode('utf-8') not in stopwords and word != '':
#             seg_words.append(word)
#     score_dict = {}
#     for i in range(len(self.all_sep_questions)):
#         each_score_lst = []
#         for input_word in seg_words:
#             similar_lst = []
#             if u'%s' % input_word in model:
#                 for word in self.all_sep_questions[i]:
#                     word = word.split('_')[0]
#                     if u'%s' % word in model:
#                         similar_lst.append(model.similarity(u'%s' % word, u'%s' % input_word))
#                     else:
#                         similar_lst.append(0)
#             else:
#                 for word in self.all_sep_questions[i]:
#                     similar_lst.append(0)
#             each_score_lst.append(similar_lst)
#
#         arr1 = np.array(each_score_lst)
#         # print arr1
#         # print '-----------'
#         similar_score = 0
#         count = 0.0
#         while np.max(arr1) > threshold:
#             similar_score += np.max(arr1)
#             count += 1
#             re = np.where(arr1 == np.max(arr1))
#             row = re[0][0]
#             column = re[1][0]
#             arr1[row, :] = 0
#             arr1[:, column] = 0
#         not_similar_arr = np.transpose(np.nonzero(arr1))
#         m = len(not_similar_arr)
#         if m != 0:
#             not_similar_score = 0.0
#             for j in range(m):
#                 not_similar_score += (1 - arr1[not_similar_arr[j][0], not_similar_arr[j][1]])
#                 # print not_similar_score
#             score_dict[str(i)] = similar_score / (similar_score + not_similar_score)
#         elif m == 0 and count != 0:
#             score_dict[str(i)] = similar_score / count
#         else:
#             score_dict[str(i)] = 0
#             # print i
#     sorted_score = sorted(score_dict.iteritems(), key=itemgetter(1), reverse=True)
#     print 'the input question is %s' % text
#     if sorted_score[0][1] > 0.8:
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
#         print '------------------------------------------------------'
#         return self.q_a[int(sorted_score[0][0])][0]
#     else:
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[1][0])][0], sorted_score[1][1])
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[2][0])][0], sorted_score[2][1])
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[3][0])][0], sorted_score[3][1])
#         print 'the question is:%s the similarity is: %f' % (
#         self.q_a[int(sorted_score[4][0])][0], sorted_score[4][1])
#         print '------------------------------------------------------'
#         return [self.q_a[int(sorted_score[0][0])][0], self.q_a[int(sorted_score[1][0])][0],
#                 self.q_a[int(sorted_score[2][0])][0], self.q_a[int(sorted_score[3][0])][0],
#                 self.q_a[int(sorted_score[4][0])][0]]


# 获得输入文本向量
def get_text_vector(text):
    with open('stopwords.txt', 'r') as f:
        stopwords = f.read().split('\n')
    jieba.load_userdict('entitydict.txt')
    cos_similar = {}
    text_vector = np.zeros((1, 200), dtype='float32')
    seg_list = pseg.cut(text.strip())
    seg_words = []
    for word, flag in seg_list:
        if word.encode('utf-8') not in stopwords and word != '':
            seg_words.append(word + '_' + flag)
    count = 0.0
    flag_sum = 0.0
    for word_f in seg_words:
        word = word_f.split('_')[0]
        flag = word_f.split('_')[1]
        if u'%s' % word in model:
            count += 1
            if flag_w.has_key(flag):
                text_vector += (model[u'%s' % word] * flag_w[flag])
                flag_sum += flag_w[flag]
            else:
                text_vector += (model[u'%s' % word] * 1)
                flag_sum += 1
    text_vector = text_vector / len(seg_words)
    return text_vector

'''
简单向量相加
'''
def vector_sum_similar(tuple1):
    num = tuple1[0]
    similar_score = tuple1[1]
    # text_vector = text_vector/count
    # text_vector = text_vector / flag_sum
    # print text_vector
    cos_similar[str(num)] =similar_score

'''
结果输出
'''
def output_answer(q_a):
    sorted_score = sorted(cos_similar.iteritems(), key=itemgetter(1), reverse=True)
    if sorted_score[0][1] > 1.951:
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
        print '------------------------------------------------------'
        return q_a[int(sorted_score[0][0])][0]
    else:
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[1][0])][0], sorted_score[1][1])
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[2][0])][0], sorted_score[2][1])
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[3][0])][0], sorted_score[3][1])
        print 'the question is:%s the similarity is: %f' % (
        q_a[int(sorted_score[4][0])][0], sorted_score[4][1])
        print '------------------------------------------------------'
        return [q_a[int(sorted_score[0][0])][0], q_a[int(sorted_score[1][0])][0],
                q_a[int(sorted_score[2][0])][0],q_a[int(sorted_score[3][0])][0],
                q_a[int(sorted_score[4][0])][0]]
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[5][0])][0],sorted_score[5][1])
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[6][0])][0],sorted_score[6][1])
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[7][0])][0],sorted_score[7][1])
        # return cos_similar


def precise_recall(self, test_path):
    with open(test_path, 'r') as f:
        test_text = f.read().split('\n')
    input_sentence = [line.split('\t', 1)[0].strip() for line in test_text]
    wished_questions = [line.split('\t')[1:] for line in test_text]
    recall = 0
    precise = 0
    for i in range(len(input_sentence)):
        count = 0
        similar_questions = self.vector_sum_similar(flag_w, model, input_sentence[i])
        # similar_questions = self.test(sentence,0.7)
        if type(similar_questions) is types.ListType:
            for each_question in similar_questions:
                if each_question in wished_questions[i]:
                    count += 1
            recall += (count / float(len(wished_questions[i])))
            precise += (count / float(len(similar_questions)))
        if type(similar_questions) is types.StringType:
            if similar_questions in wished_questions:
                recall += 1 / float(len(wished_questions[i]))
                precise += 1
    recall = recall / float(len(test_text))
    precise = precise / float(len(test_text))
    print 'recall is %f' % recall
    print 'precise is %f' % precise


if __name__ == '__main__':
    print 'Parent process %s.' % os.getpid()
    text = '什么是海损'
    print 'The input question is %s'%text
    all_sep_questions,all_sep_questions_arr = get_all_sep_questions_arr()
    text_vector = get_text_vector(text)
    p = Pool()
    for i in range(len(all_sep_questions_arr)):
        p.apply_async(vector_cosine,args=(i,text_vector,all_sep_questions_arr[i],),callback=vector_sum_similar)
    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'
    output_answer(get_q_a())
