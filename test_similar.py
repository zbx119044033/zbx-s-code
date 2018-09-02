#!/usr/bin/python
# -*- coding:utf-8 -*-

from operator import itemgetter
import numpy as np
from gensim.models import word2vec
import jieba.posseg as pseg
import jieba
import sys
import os
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
reload(sys)
sys.setdefaultencoding('utf-8')
jieba.load_userdict('entitydict.txt')


with open('stopwords.txt', 'r') as f:
    stopwords = f.read().split('\n')
model = word2vec.Word2Vec.load('E:/Pycharm/mywork/dialog/corpus.model')
# flag_w = {'x': 1.0, 'n': 1.2, 'nz': 1, 'vn': 0.9, 'uj': 0.5, 'v': 0.8, 'r': 0.5, 'm': 0.6, 'a': 1, 'c': 0.9, 'l': 1,
#           'd': 0.8, 'y': 0.5, 'nr': 1.2, 'i': 1.2}
flag_w = {'x': 1, 'n': 1.2, 'nz': 1, 'vn': 0.9, 'uj': 0.5, 'v': 0.8, 'r': 0.5, 'm': 0.6, 'a': 1, 'c': 0.9, 'l': 1,
          'd': 0.8, 'y': 0.1, 'nr': 1, 'i': 1.2, 'zg': 0.1}


class SimilarRobot(object):

    def __init__(self):
        self.all_sep_questions, self.all_sep_questions_arr = self.get_all_sep_questions_arr()
        self.q_a = self.get_q_a()

    # 预处理，将库中所有问题向量化，获得all_sep_questions_arr
    def get_all_sep_questions_arr(self):
        all_sep_questions = []
        with open('sep_questions_7_24.txt', 'r') as fr:
            list2 = fr.read().strip().split('\n')
        for line in list2:
            line = line.split()
            all_sep_questions.append(line)      # 矩阵，每句一行，每行为分词后的列表
        all_sep_questions_arr = []
        for each_question in all_sep_questions:
            line_arr = np.zeros((1, 200), dtype='float32')
            count = 0.0
            flag_sum = 0.0
            for word_f in each_question:
                word_f = word_f.split('_')
                word = word_f[0]
                flag = word_f[1]
                if unicode(word) in model:
                    count += 1
                    if flag in flag_w:
                        line_arr += model[unicode(word)] * flag_w[flag]
                        flag_sum += flag_w[flag]
                    else:
                        line_arr += model[unicode(word)]*1
                        flag_sum += 1
            all_sep_questions_arr.append(line_arr/len(each_question))       # 矩阵，每行一句，为加权求和平均后的向量
            # all_sep_questions_arr.append(line_arr / flag_sum)
            # all_sep_questions_arr.append(line_arr/count)
        return all_sep_questions, all_sep_questions_arr

    # 获得q_a,问题与答案集合，二维向量，[i][0]为第i个QA对的问题，[i][1]为答案
    def get_q_a(self):
        with open('q&a.txt', 'r') as fr:
            q_a_1 = fr.read().split('\n')
        q = []
        a = []
        for i in range(len(q_a_1)):
            if i % 2 == 0:
                q.append(q_a_1[i])
            else:
                a.append(q_a_1[i])
        q_a = []
        for i in range(len(q)):
            q_a.append([q[i], a[i]])        # 矩阵，每行为问答对，列表，两项：问、答
        return q_a

    # 辅助函数计算余弦距离
    def vector_cosine(self, v1, v2):
        # return (v1.dot(v2.T)) / (np.math.exp(-15) + np.sqrt(v1.dot(v1.T)) * np.sqrt(v2.dot(v2.T)))
        return cosine_similarity(v1, v2)
        # return euclidean_distances(v1, v2)

    # 方法二：语义jaccard（时间复杂度高）
    def test(self, text, threshold):
        seg_list = jieba.lcut(text.strip(), cut_all=False)
        seg_words = []
        for word in seg_list:
            if word.encode('utf-8') not in stopwords and word != '':
                seg_words.append(word)
        score_dict = {}
        for i in range(len(self.all_sep_questions)):
            each_score_lst = []
            for input_word in seg_words:
                similar_lst = []
                if unicode(input_word) in model:
                    for word in self.all_sep_questions[i]:
                        word = word.split('_')[0]
                        if unicode(word) in model:
                            similar_lst.append(model.similarity(unicode(word), unicode(input_word)))
                        else:
                            similar_lst.append(0)
                else:
                    for word in self.all_sep_questions[i]:
                        similar_lst.append(0)
                each_score_lst.append(similar_lst)

            arr1 = np.array(each_score_lst)
            # print arr1
            # print '-----------'
            similar_score = 0
            count = 0.0
            while np.max(arr1) > threshold:
                similar_score += np.max(arr1)
                count += 1
                re = np.where(arr1 == np.max(arr1))
                row = re[0][0]
                column = re[1][0]
                arr1[row, :] = 0
                arr1[:, column] = 0
            not_similar_arr = np.transpose(np.nonzero(arr1))
            m = len(not_similar_arr)
            if m != 0:
                not_similar_score = 0.0
                for j in range(m):
                    not_similar_score += (1 - arr1[not_similar_arr[j][0], not_similar_arr[j][1]])
                    # print not_similar_score
                score_dict[str(i)] = similar_score/(similar_score + not_similar_score)
            elif m == 0 and count != 0:
                score_dict[str(i)] = similar_score/count
            else:
                score_dict[str(i)] = 0
            # print i
        sorted_score = sorted(score_dict.iteritems(), key=itemgetter(1), reverse=True)
        print 'the input question is %s' % text
        if sorted_score[0][1] > 0.8:
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
            print '------------------------------------------------------'
            return self.q_a[int(sorted_score[0][0])][0]
        else:
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[1][0])][0], sorted_score[1][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[2][0])][0], sorted_score[2][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[3][0])][0], sorted_score[3][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[4][0])][0], sorted_score[4][1])
            print '------------------------------------------------------'
            return [self.q_a[int(sorted_score[0][0])][0], self.q_a[int(sorted_score[1][0])][0],
                    self.q_a[int(sorted_score[2][0])][0], self.q_a[int(sorted_score[3][0])][0],
                    self.q_a[int(sorted_score[4][0])][0]]

    # 方法一：向量乘权重相加
    def vector_sum_similar(self, text):
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
            if unicode(word) in model:
                count += 1
                if flag in flag_w:
                    text_vector += (model[unicode(word)] * flag_w[flag])
                    flag_sum += flag_w[flag]
                else:
                    text_vector += (model[unicode(word)] * 1)
                    flag_sum += 1
        text_vector = text_vector/len(seg_words)
        # text_vector = text_vector/count
        # text_vector = text_vector / flag_sum
        # print text_vector
        cos_similar = {}
        for i in range(len(self.all_sep_questions_arr)):
            cos_similar[str(i)] = self.vector_cosine(text_vector, self.all_sep_questions_arr[i])
            # cos_similar[str(i)] = text_vector.dot(all_sep_questions_arr[i].T)/np.sqrt(text_vector.dot(text_vector.T)) / np.sqrt(all_sep_questions_arr[i].dot(all_sep_questions_arr[i].T))
        sorted_score = sorted(cos_similar.iteritems(), key=itemgetter(1), reverse=True)
        # sorted_score = sorted(cos_similar.iteritems(), key=itemgetter(1))

        print 'the input question is %s' % text
        if sorted_score[0][1] > 1.951:
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
            print '------------------------------------------------------'
            # return self.q_a[int(sorted_score[0][0])][0]
        else:
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[0][0])][0], sorted_score[0][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[1][0])][0], sorted_score[1][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[2][0])][0], sorted_score[2][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[3][0])][0], sorted_score[3][1])
            print 'the question is:%s the similarity is: %f' % (self.q_a[int(sorted_score[4][0])][0], sorted_score[4][1])
            print '------------------------------------------------------'
            # return [self.q_a[int(sorted_score[0][0])][0],self.q_a[int(sorted_score[1][0])][0],self.q_a[int(sorted_score[2][0])][0],self.q_a[int(sorted_score[3][0])][0],self.q_a[int(sorted_score[4][0])][0]]
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[5][0])][0],sorted_score[5][1])
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[6][0])][0],sorted_score[6][1])
        #     print 'the question is:%s the similarity is: %f' % (q_a[int(sorted_score[7][0])][0],sorted_score[7][1])
        return sorted_score

    '''
    输入
    text：指定查询的句子
    num：要返回的匹配个数
    输出
    similar_questions
    similar_answers
    similar_score
    '''
    def get_similar_questions(self, num, text):
        similar_questions = []
        similar_answers = []
        similar_score = []
        sorted_score = self.vector_sum_similar(text)
        if num > 1:
            for i in range(num):
                similar_questions.append(self.q_a[int(sorted_score[i][0])][0])
                similar_answers.append(self.q_a[int(sorted_score[i][0])][1])
                similar_score.append('%f' % sorted_score[i][1])
            # print similar_questions[1],similar_answers[1],similar_score[1]
            return similar_questions, similar_answers, similar_score
        elif num == 1:
            return self.q_a[int(sorted_score[0][0])][0], self.q_a[int(sorted_score[0][0])][1], '%f' % sorted_score[0][1]
        else:
            print "num can't be smaller than 1"
            return

    def precise_recall(self, test_path):
        with open(test_path, 'r') as fr:
            test_text = fr.read().split('\n')
        input_sentence = [line.split('\t', 1)[0].strip() for line in test_text]
        wished_questions = [line.split('\t')[1:] for line in test_text]
        recall = 0
        precise = 0
        top_1_recall = 0
        top_5_flag = 0
        top_1_flag = 0
        for i in range(len(input_sentence)):
            count = 0
            similar_questions_1, similar_answers_1, similar_score_1 = self.get_similar_questions(1, input_sentence[i])
            similar_questions_5, similar_answers_5, similar_score_5 = self.get_similar_questions(5, input_sentence[i])
            # similar_questions = self.vector_sum_similar(input_sentence[i])
            if isinstance(similar_questions_1, str):
                if similar_questions_1 in wished_questions[i]:
                    top_1_flag += 1
                    top_1_recall += 1 / float(len(wished_questions[i]))
            if isinstance(similar_questions_5, list):
                for each_question in similar_questions_5:
                    if each_question in wished_questions[i]:
                        count += 1
                recall += (count/float(len(wished_questions[i])))
                # precise += (count/float(len(similar_questions)))
            if count != 0:
                top_5_flag += 1
        recall = recall/float(len(test_text))
        # precise = precise/float(len(test_text))
        top_1_precise = top_1_flag/float(len(input_sentence))
        top_5_precise = top_5_flag/float(len(input_sentence))
        print 'top1 recall is %f' % top_1_recall
        print 'top1 precise is %f' % top_1_precise
        print 'top5 recall is %f' % recall
        print 'top5 precise is %f' % top_5_precise
        # print 'precise is %f' % precise

    def precise_recall2(self, test_path):
        # input_sentence = []
        # wished_questions = []
        with open(test_path, 'r') as fr:
            test_text = fr.read().split('\n')
        input_sentence = [line.split('\t', 1)[0].strip() for line in test_text]
        wished_questions = [line.split('\t')[1:] for line in test_text]
        '''
        wishes = []
        for ls in wished_questions:
            for i in range(len(ls)):
                wishes.append(ls[i])
        print len(input_sentence), len(wishes)
        '''
        top_3_precise = 0
        top_1_flag = 0
        top_1_recall = 0
        top_3_recall = 0
        for i in range(len(input_sentence)):
            count = 0
            similar_questions_1, similar_answers_1, similar_score_1 = self.get_similar_questions(1, input_sentence[i])
            similar_questions_3, similar_answers_3, similar_score_3 = self.get_similar_questions(3, input_sentence[i])
            # similar_questions = self.vector_sum_similar(input_sentence[i])
            if isinstance(similar_questions_1, str):
                if similar_questions_1 in wished_questions[i]:
                    top_1_flag += 1
                    top_1_recall += 1 / float(len(wished_questions[i]))
            if isinstance(similar_questions_3, list):
                for each_question in similar_questions_3:
                    if each_question in wished_questions[i]:
                        count += 1
                top_3_precise += count / 3.0
                top_3_recall += count / float(len(wished_questions[i]))

        top_1_recall = top_1_recall / float(len(input_sentence))
        top_1_precise = top_1_flag/float(len(input_sentence))
        top_3_recall = top_3_recall/float(len(input_sentence))
        top_3_precise = top_3_precise / float(len(input_sentence))
        print 'top1 recall is %f' % top_1_recall
        print 'top1 precise is %f' % top_1_precise
        print 'top3 recall is %f' % top_3_recall
        print 'top3 precise is %f' % top_3_precise


if __name__ == '__main__':
    chatbot = SimilarRobot()
    # text = '什么是海损'
    # sorted_score = chatbot.vector_sum_similar(text)
    # chatbot.get_similar_questions(5,text)
    chatbot.precise_recall2('test_questions.txt')
    # all_sep_questions, all_sep_questions_arr = chatbot.get_all_sep_questions_arr()
    # chatbot.vector_cosine(all_sep_questions_arr[0],all_sep_questions_arr[0])
    # len(all_sep_questions)
    # Precise_Recall(r'F:\simi
    # lar\test_questions.txt')
    #
    # input_sentence,wished_questions = Precise_Recall(r'test_questions.txt')
    # if '医疗保险可以退保吗' in wished_questions[1]:
    #     print 'p'
    #
    # test_list = [[0,0],[0,1],[0,4]]
    # test_list = 'asdfa  dfa  d sdf 我是'
    # if type(test_list) is types.StringType:
    #     print 'o'
    # arr1 = np.array(test_list)
    # re = np.where(arr1 == np.max(arr1))
    # row = re[0][0]
    # column = re[1][0]
    # arr1[row,:] = 0
    # arr1[:,column] = 0
    # arr1[0,0]
    # arr1[1,0]
    # np.count_nonzero(arr1)
    # a = np.transpose(np.nonzero(arr1))
    # for i in range(len(a)):
    #     print arr1[a[i][0], a[i][1]]

    # np.count_nonzero(arr1)

    # dict1 = {'1':265,'2':112,'3':323}
    # sorted_score = sorted(dict1.iteritems(),key=lambda d:d[1],reverse=True)

    # a = (model[u'什么'] + model[u'是'] + model[u'意外险'] )/3
    # b = (model[u'意外险']+ model[u'是'] + model[u'什么'])/3
    # print vector_cosine(a,b)
    #
    # with open('questions.txt','a')as f:
    #     for i in range(len(q_a)):
    #         f.write(q_a[i][0])
    #         f.write('\n')
    #
    # seg_list = pseg.cut('如何给公司员工买意外险')
    # for word,flag in seg_list:
    #     print word,flag
    # seg_list = pseg.cut('什么是海损')
    # for word,flag in seg_list:
    #     print word,flag
    #
    # y1 = model.similarity(u"叫",u"是")
    # print u"woman和man的相似度为：", y1
    # print "--------\n"

# with open('test_questions.txt', 'r') as f:
#     test_text = f.read().split('\n')
# input_sentence = [line.split('\t', 1)[0].strip() for line in test_text]
# wished_questions = [line.split('\t')[1:] for line in test_text]
# print len(wished_questions[1])
