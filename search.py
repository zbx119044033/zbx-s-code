# -*- coding:utf-8 -*-
# this module is used to test simple search algorithm

import jieba.posseg
from pymongo import MongoClient
import sys
import time
from functional import seq
jieba.initialize()
reload(sys)
sys.setdefaultencoding("utf-8")


# connect to database
try:
    client = MongoClient("mongodb://lionking:Tv6pAzDp@60.205.187.223:27017/Simba?authMechanism=SCRAM-SHA-1")
    db_mongo = client.Simba
    collect = db_mongo.entity_product
except Exception, e:
    print e
    sys.exit()


def my_str(s):
    if isinstance(s, list):
        if isinstance(s[0], dict):
            ss = ""
            for i in range(len(s)):
                for key, value in s[i].items():
                    ss += "%s: %s\n" % (key, value)
            return ss
        else:
            return " ".join(s)
    else:
        return s


def search(t, collection):
    name, prop = t[0], t[1]
    answer = "产品无此属性"
    cursor = collection.find_one({"name": name})
    if cursor is None:
        answer = "查无此项"
    else:
        """
        for i in range(len(cursor["props"])):
            if cursor["props"][i]["name"] == prop or prop in cursor["props"][i]["alias"]:
                answer = cursor["props"][i]["value"]
                break
        """
        answer = seq(cursor["props"])\
            .filter(lambda item: item["name"] == prop or prop in item["alias"])\
            .map(lambda item: my_str(item["value"]))
    return answer


if __name__ == "__main__":
    sent = "你好，请问太平福利全佑的险种是哪一类？"
    tt = ("太平福利全佑", "保费")
    time_start = time.time()
    ans = search(tt, collect)
    time_end = time.time()
    time = time_end - time_start
    print ans, time
