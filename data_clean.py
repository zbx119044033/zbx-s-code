# -*- coding:utf-8 -*-

from pymongo import MongoClient
import json
import sys
from bson.json_util import dumps
import io
from functional import seq
reload(sys)
sys.setdefaultencoding("utf-8")


def connect():
    # connect to database
    try:
        client = MongoClient("mongodb://lionking:Tv6pAzDp@60.205.187.223:27017/Simba?authMechanism=SCRAM-SHA-1")
        db_mongo = client.Simba
        collection = db_mongo.entity_all
    except Exception, e:
        print e
        sys.exit()
    return collection


def download(collection):
    result = collection.find({})
    with io.open("entity_all0.json", "w", encoding='utf-8') as fw:
        fw.write(dumps(result, ensure_ascii=False))
    print "download completed!"


def upload(collection):
    with open("mba_found0.json", "r") as fr:
        for line in fr.readlines():
            content = json.loads(line)
            collection.insert(content)
    print "upload completed!"


def clean():
    with open("gold_product4.json", "r") as fr:
        content = json.load(fr)

        def process_kv(kvs):
            res = []
            for k, v in kvs.items():
                res.append({"name": k, "value": v})
            return res

        def process_prop(prop):
            if prop["name"] == u"保障利益":
                prop["value"] = seq(prop["value"]).map(process_kv).list()
            return prop

        def process_item(item):
            item["domain"] = "product"
            del item["_id"]
            item["props"] = seq(item["props"]).map(process_prop).list()
            return item

        result = seq(content).map(process_item).list()
        return result


def my_clean():
    with open("gold_product.json", "r") as fr:
        content = json.load(fr)
        for items in content:
            items['domain'] = 'product'
            ans = seq(items["props"]).filter(lambda item: item['name'] == u"保障利益")
            interest = seq(ans['value'])\
                .map(lambda item: [{'name': u'保障项目', 'value': item[u'保障项目']}, {'name': u'保额', 'value': item[u'保额']}])
            ans['value'] = interest
            print items
            break


def transfer():
    with open("gold_agency.json", "r") as fr:
        content = json.load(fr)

    def process_lis(d):
        lis = []
        for i in range(0, len(d['value']), 3):
            lis.append([d['value'][i], d['value'][i+1], d['value'][i+2]])
        return lis

    def process_prop(prop):
        if prop["name"] == u"保障利益":
            lis = []
            for i in range(0, len(prop['value']), 3):
                lis.append([prop['value'][i], prop['value'][i + 1], prop['value'][i + 2]])
            prop["value"] = lis
        return prop

    def process_item(item):
        del item["_id"]
        # item["props"] = seq(item["props"]).map(process_prop).list()
        return item

    result = seq(content).map(process_item).list()
    return result


def clear():
    with open("vobao_product.json", "r") as fr:
        content = json.load(fr)

    def process_prop(prop):
        if prop["name"] == u"投保须知":
            prop["value"] = seq(prop["value"]).map(lambda item: item[u"说明"] + item[u"内容"]) \
                .reduce(lambda s1, s2: s1 + s2)
        return prop

    def process_list(lis):
        for index, d in enumerate(lis):
            if d["value"] == "" or d["value"] == [] or d["value"] is None:
                del lis[index]
        return lis

    def process_prop2(prop):
        if prop["name"] == u"保障利益":
            prop['value'] = seq(prop['value']).map(process_list).list()
        return prop

    def process_item(item):
        del item["_id"]
        item['domain'] = 'product'
        for i in range(len(item["props"]) - 1, -1, -1):
            if item["props"][i]["value"] is None or item["props"][i]["value"] == [] or item["props"][i]["value"] == '':
                del item["props"][i]
        # item["props"] = seq(item["props"]).map(process_prop2).list()
        return item

    result = seq(content).map(process_item).list()
    return result


if __name__ == "__main__":
    collect = connect()
    # download(collect)
    upload(collect)
    # res = clean()
    # res = clear()
    # res = transfer()
    # collect.insert(res)
