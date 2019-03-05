# -*- coding:utf-8 -*-
# interpreted via python3.6

import codecs
import json
from pymongo import MongoClient
import sys
from bson import ObjectId
from bson.json_util import dumps
import csv
import io
import string
reload(sys)
sys.setdefaultencoding('utf-8')


# connect to database
try:
    client = MongoClient("mongodb://xxx")
    db_mongo = client.Simba
    collection = db_mongo.entity_foundation
except Exception as e:
    print(e)
    sys.exit()

# 抓取产品名称
items = []
for item in collection.find():
    if item["name"] is None or item['props'][1]["value"] is None:
        print(item["_id"])
    else:
        items.append(item["name"].strip(string.punctuation))
        # items.append(item["name"])

with open("userdict_found.txt", "w") as f:
    for index, item in enumerate(items):
        # print(index, item)
        f.write(item + " " + "3" + " " + "nz" + "\n")
        # f.write(str(index) + item + "\n")
        # f.write(item + "\n")

"""
# 
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


with io.open('test.json', 'w', encoding='utf-8') as f:
    index = 0
    for item in collection.find():
        # ss = json.encode(item, cls=JSONEncoder)
        # ss = JSONEncoder().encode(item)
        line = dumps(item, ensure_ascii=False) + "\n"
        f.write(line)
        index += 1
        print index
"""
