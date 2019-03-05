# -*- coding: utf-8 -*-

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import KMeans
from sklearn import metrics
from pymongo import MongoClient
import sys
import pickle
import matplotlib.pyplot as plt
reload(sys)
sys.setdefaultencoding('utf-8')


def serialize():
    try:
        client = MongoClient("mongodb://xxx")
        db_mongo = client.Simba
        collection = db_mongo.sentence_vector
    except Exception, e:
        print e
        sys.exit()

    vectors = []
    aid = []
    for item in collection.find({}):
        vectors.append(np.array(item['vector']))
        aid.append(item['answer_id'])

    with open('vectors.pkl', 'wb') as fw:
        pickle.dump(np.array(vectors), fw)
    with open('data.pkl', 'wb') as fw:
        pickle.dump(aid, fw)
    print 'dump completed !'


def deserialize():
    with open('vectors.pkl') as fr:
        x = pickle.load(fr)
    return x


def search(x):
    n = []
    met = []
    ssd = []
    limit = np.arange(100, 410, 30)
    for i in limit:
        # print '%f is starting ...' % i
        # db = DBSCAN(eps=i, min_samples=10, metric='euclidean', algorithm='auto',  p=None, n_jobs=-1).fit(x)
        # labels = db.labels_
        # n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # Number of clusters, ignoring noise if present.
        kmeans = KMeans(n_clusters=i, init='k-means++', random_state=0).fit(x)
        sd = kmeans.inertia_
        labels = kmeans.labels_
        # n.append(n_clusters_)
        metric = metrics.silhouette_score(x, labels, sample_size=20000)
        met.append(metric)
        ssd.append(sd)
        print 'Number %d is completed' % i
    """
    plt.figure()
    plt.plot(limit, met, color='b', linewidth=1)
    plt.xlabel("n_clusters")
    plt.ylabel("SSD")
    plt.title("Grid search CV for parameter n_clusters in K-means")
    plt.axis("tight")
    plt.show()
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(limit, ssd, color='b', linewidth=1)
    ax1.set_ylabel('SSD')
    ax1.set_title("Grid search CV for parameter n_clusters in K-means")
    ax2 = ax1.twinx()
    ax2.plot(limit, met, color='r', linewidth=1)
    ax2.set_ylabel('Silhouette Coefficient')
    ax2.set_xlabel('n_clusters')
    plt.show()


def dbscan(x):
    db = DBSCAN(eps=1, min_samples=10, metric='cosine', algorithm='brute', leaf_size=30,  p=None, n_jobs=-1).fit(x)
    labels = db.labels_
    indices = db.core_sample_indices_
    n_clusters_ = len(set(labels))
    print 'Estimated number of clusters: %d' % n_clusters_
    print "Silhouette Coefficient: %0.3f" % metrics.silhouette_score(x, labels)


def batch_kmeans(x):
    kmeans = MiniBatchKMeans(n_clusters=240, init='k-means++', batch_size=100).fit(x)
    sd = kmeans.inertia_
    labels = kmeans.labels_
    metric = metrics.silhouette_score(x, labels, sample_size=10000)
    print 'the sum of square distances of samples to their nearest neighbor is : %f' % sd
    print 'Silhouette Coefficient: %f' % metric


def kmeans(x):
    # kmeans = KMeans(n_clusters=240, init='k-means++').fit(x)
    kmeans = KMeans(n_clusters=240, init='k-means++', random_state=0).fit(x)
    sd = kmeans.inertia_
    labels = kmeans.labels_
    metric = metrics.silhouette_score(x, labels, sample_size=20000)
    print 'the sum of square distances of samples to their nearest neighbor is : %f' % sd
    print 'Silhouette Coefficient: %f' % metric


if __name__ == '__main__':
    # serialize()
    search(deserialize())
    # dbscan(deserialize())
    # kmeans(deserialize())
    # batch_kmeans(deserialize())
