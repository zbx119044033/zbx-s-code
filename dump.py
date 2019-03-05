# -*- coding:utf-8 -*-

from bson.json_util import dumps
from json import dumps
from pymongo import MongoClient
import sys
import io
import os
reload(sys)
sys.setdefaultencoding('utf-8')


def my_dump():
    with io.open("extra.json", "w", encoding='utf-8') as fw:
        result = {"alias": [], "domain": "foundation", "name": "保险有效期",
                  "props": [{"name": "link",
                             "value": u"http://wiki.mbalib.com/wiki/%E4%BF%9D%E9%99%A9%E6%9C%89%E6%95%88%E6%9C%9F"},
                            {"name": "desc", "value": u"从生效时起到保险限届满时止的阶段。"}]}
        fw.write(dumps(result, ensure_ascii=False))
    print "download completed!"


try:
    client = MongoClient("mongodb://xxx")
    db_mongo = client.Simba
    collection = db_mongo.faq
except Exception, e:
    print e
    sys.exit()

result = collection.find({})
# data_path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "resources/data.json")
with io.open('data.json', "w", encoding='utf-8') as fw:
    for index, item in enumerate(result):
        if index < 50:
            data = {'question': item['question'], 'answer': item['answer'], 'label': item['status']}
            fw.write(dumps(data, ensure_ascii=False))
        else:
            break
print "download completed!"
