# -*- coding:utf-8 -*-

import json
import MySQLdb
import codecs
import sys
import io
import csv
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

"""
sql2 = "select pm.local_product_name, pc.url" \
       " from product_main AS pm" \
       " RIGHT JOIN(" \
       " select product_main_id, GROUP_CONCAT(insurance_clause_doc_url) url" \
       " from product_insurance_doc" \
       " GROUP BY product_main_id) pc" \
       " ON pm.id=pc.product_main_id"

result2 = fetch_data(sql2)

# print len(result2), len(result3), len(interest)
# inp = codecs.open('inner_lib3.json', 'w', encoding='utf-8')

with open("docs.txt", "w") as f:
    for row in result2:
        line = row[0] + "\t" + row[1] + "\n"
        f.write(line)
        # line = json.dumps(item, ensure_ascii=False) + "\n"
        # inp.write(line)
        print "successfully stacked"

with io.open('docs2.csv', 'w') as f:
    fieldnames = ['name', 'url']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in result2:
        writer.writerow({'name': row[0], 'url': row[1]})
"""
