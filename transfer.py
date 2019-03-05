# -*- coding:utf-8 -*-

import json
import MySQLdb
from pymongo import MongoClient
import sys
import re
import string
reload(sys)
sys.setdefaultencoding('utf8')


def fetch_data(sql):
    try:
        db = MySQLdb.connect(host="xxx", user="xxx", passwd="xxx", db="dtbserver", port=13307,
                                charset="utf8")
    except Exception, ee:
        print ee
        sys.exit()
    result = None
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute("SET group_concat_max_len=20000")
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception, err:
        print err
    finally:
        cursor.close()
        db.close()
    return result


def t2list(res):
    intere = []
    row = []
    flag = 1
    t = None
    for t in res:
        if t[0] == flag:
            row.append([{"name": "保障项目", "value": t[1]}, {"name": "保额", "value": t[2]}, {"name": "说明", "value": my_strip(t[3])}])
        else:
            flag = t[0]
            intere.append(row)
            row = []
    row.append([{"name": "保障项目", "value": t[1]}, {"name": "保额", "value": t[2]}, {"name": "说明", "value": my_strip(t[3])}])
    intere.append(row)
    return intere


def my_strip(s):
    if s is None:
        return None
    else:
        res = re.sub("<[^>]*?>", "", s)
        return res.replace("\r", "").replace("\t", "").replace("\n", "").replace("&nbsp;", "").strip(string.punctuation)


def trip_pay(s):
    if s is None:
        return "年缴"
    else:
        return s.replace("\t", "").strip()

# connect to database
try:
    client = MongoClient("mongodb://xxx")
    db_mongo = client.Simba
    collection = db_mongo.entity_inner_product2
except Exception, e:
    print e
    sys.exit()

sql2 = "select pm.id, pm.local_product_name, pm.current_price, " \
       "ic.company," \
       "ps.ped," \
       "pr.age," \
       "pd.pay," \
       "py.type, py.note," \
       "pi.health," \
       "pf.fea," \
       "pc.url" \
       " from product_main AS pm" \
       " LEFT JOIN(" \
       " select product_main_id, GROUP_CONCAT(DISTINCT display_title) tt, GROUP_CONCAT(DISTINCT display_content) ped" \
       " from product_detail_rate_show" \
       " where display_title='保障期限'" \
                                 " GROUP BY product_main_id) ps" \
                                 " ON pm.id=ps.product_main_id" \
                                 " LEFT JOIN(" \
                                 " select product_main_id, GROUP_CONCAT(DISTINCT age_display) age" \
                                 " from product_rate " \
                                 " GROUP BY product_main_id) pr" \
                                 " ON pm.id=pr.product_main_id" \
                                 " LEFT JOIN(" \
                                 " select product_main_id, GROUP_CONCAT(DISTINCT display_title) a, GROUP_CONCAT(DISTINCT display_content) pay" \
                                 " from product_detail_rate_show " \
                                 " where display_title='缴费方式'" \
                                                           " GROUP BY product_main_id) pd" \
                                                           " ON pm.id=pd.product_main_id" \
                                                           " LEFT JOIN(" \
                                                           " select product_main_id, claim_type_text type, insure_notice note" \
                                                           " from product_display" \
                                                           " GROUP BY product_main_id) py" \
                                                           " ON pm.id=py.product_main_id" \
                                                           " LEFT JOIN(" \
                                                           " select product_main_id, GROUP_CONCAT(DISTINCT item_describe) health " \
                                                           " from product_notice_item" \
                                                           " GROUP BY product_main_id) pi" \
                                                           " ON pm.id=pi.product_main_id" \
                                                           " LEFT JOIN(" \
                                                           " select product_main_id, GROUP_CONCAT(DISTINCT feature_describe) fea" \
                                                           " from product_feature" \
                                                           " GROUP BY product_main_id) pf" \
                                                           " ON pm.id=pf.product_main_id" \
                                                           " LEFT JOIN(" \
                                                           " select product_main_id, GROUP_CONCAT(insurance_clause_doc_url) url" \
                                                           " from product_insurance_doc" \
                                                           " GROUP BY product_main_id) pc" \
                                                           " ON pm.id=pc.product_main_id" \
                                                           " LEFT JOIN(" \
                                                           " select id, company_full_name company" \
                                                           " from insurance_company) ic" \
                                                           " ON pm.insurance_company_id=ic.id" \
                                                           " ORDER BY pm.id"

sql3 = "select pm.id, pl.name, pl.amount, pl.liability " \
       " from product_main pm" \
       " LEFT JOIN product_liability pl" \
       " ON pm.id=pl.product_main_id" \
       " ORDER BY pm.id"

result2 = fetch_data(sql2)                       # result2 = ((id,item,price,state),(id,item,price,state))
result3 = fetch_data(sql3)                       # result3 = ((id,item,price,state),(id,item,price,state))
interest = t2list(result3)                       # interest= [[{"id":t[1], "it":t[2]}],[{"id":t[1], "it":t[2]}]]
# print len(result2), len(result3), len(interest)
# inp = codecs.open('inner_lib3.json', 'w', encoding='utf-8')

for index, row in enumerate(result2):
    item = {"name": row[1].replace("·", "")}
    alias = []
    item["alias"] = alias
    item["domain"] = "product"
    item["props"] = [
        {"name": "承保公司", "alias": ["公司"], "value": row[3]},
        {"name": "承保年龄", "alias": ["年龄", "出生日期"], "value": row[5]},
        {"name": "保险期间", "alias": ["保期"], "value": row[4]},
        {"name": "产品特色", "alias": ["产品特点"], "value": my_strip(row[10])},
        {"name": "支付方式", "alias": ["缴费方式"], "value": trip_pay(row[6])},
        {"name": "保障利益", "alias": ["保障范围", "保险责任", "保障权益", "保障利益", "保险项目"], "value": interest[index]},
        {"name": "产品类型", "alias": ["险种"], "value": row[7]},
        {"name": "投保须知", "alias": ["须知", "温馨提示", "责任免除"], "value": my_strip(row[8])},
        {"name": "保费", "alias": ["价格"], "value": row[2]},
        {"name": "保险条款", "alias": ["条款"], "value": row[11]},
        {"name": "健康告知", "alias": ["健康"], "value": my_strip(row[9])},
    ]

    for i in range(len(item["props"]) - 1, -1, -1):
        if item["props"][i]["value"] is None:
            del item["props"][i]

    collection.insert_one(item)
    # line = json.dumps(item, ensure_ascii=False) + "\n"
    # inp.write(line)
    print "successfully stacked"
