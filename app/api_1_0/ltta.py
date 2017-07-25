import datetime
import json
import math
import os

import pymongo
from flask import abort, current_app, jsonify, make_response, request

from . import api
from .. import mongo


def payload_to_list(payload):
    result = []
    for gid in payload:
        item = payload[gid]
        item["gid"] = int(gid)
        result.append(item)
    return result


def get_index(data_in):
    """
    Parse mongoDB index part from data input
    Also return a datetime object from datefield
    """
    dt = datetime.datetime.strptime(data_in["date"], "%Y%m%d")
    date = dt.date()

    index = {
        "year": date.year,
        "month": date.month,
        "day": date.day,
        "qtr": data_in["qtr"],
        "city": data_in["city"],
        "weekday": date.weekday(),
        "date": dt
    }
    return (index, dt)


def payload_to_dict(payload, key, aggregate_func):
    if type(payload) is dict:
        return payload
    elif type(payload) is list:
        result = {}
        for item in payload:
            if type(item) is dict:
                item[key] = str(item[key])
                if item[key] in result:
                    result[item[key]] = aggregate_func(
                        result[item[key]], item)
                else:
                    result[item[key]] = item
                del item[key]
            else:
                # return payload if item is not a dict
                return payload
        return result
    else:
        # might cause exception if payload type is unknown
        return dict(payload)


def aggregate_ltta(old, new):
    result = {}
    if "count" in old and "count" in new:
        result["count"] = old["count"] + new["count"]
    else:
        return new
    if "ltta" in old and "ltta" in new:
        old_sum = old["count"] * old["ltta"]
        new_sum = new["count"] * new["ltta"]
    else:
        return new
    # LTTA is the average of two
    result["ltta"] = (old_sum + new_sum) / result["count"]
    if "std" in old and "std" in new:
        # aggregate std
        a = old["count"] * old["std"] * old["std"]
        b = new["count"] * new["std"] * new["std"]
        c = math.pow(old["ltta"] - (result["ltta"]), 2)
        d = math.pow(new["ltta"] - (result["ltta"]), 2)
        result["std"] = math.sqrt((a + b + c + d) / result["count"])
    return result


def aggregate_payload(old, new, aggregate_func):
    dict_old = payload_to_dict(old, "gid", aggregate_func)
    dict_new = payload_to_dict(new, "gid", aggregate_func)
    result = dict(dict_old)
    for key in dict_new:
        if key in dict_old:
            result[key] = aggregate_func(result[key], dict_new[key])
        else:
            result[key] = dict_new[key]
    return result


def update_mm(data_in):
    trafficDB = mongo.db
    mm = data_in["mm"]
    index = {
        "RID": data_in["RID"],
        "city": data_in["city"]
    }
    result = trafficDB.MM.update_one(index, {
        "$set": {
            "mm": mm,
            "start": data_in["start"],
            "end": data_in["end"]
        },
        "$currentDate": {
            "lastModified": True
        }
    }, upsert=True)
    return jsonify({
        "modified": result.modified_count
    })


def update_ltte(data_in):
    trafficDB = mongo.db
    ltte = data_in["ltte"]
    index = {
        "RID": data_in["RID"],
        "city": data_in["city"]
    }
    result = trafficDB.LTTE.update_one(index, {
        "$set": {
            "ltte": ltte,
            "start": datetime.datetime.strptime(
                data_in["start"], "%Y-%m-%d %H:%M:%S"),
            "end": datetime.datetime.strptime(
                data_in["end"], "%Y-%m-%d %H:%M:%S"),
        },
        "$currentDate": {
            "lastModified": True
        }
    }, upsert=True)
    return jsonify({
        "modified": result.modified_count
    })


def update_ltta(data_in):
    trafficDB = mongo.db
    ltta = data_in["ltta"]
    index, dt = get_index(data_in)
    result = trafficDB.LTTA.find_one(index)
    if result is not None:
        ltta = aggregate_payload(ltta, result["ltta"], aggregate_ltta)
    else:
        ltta = payload_to_dict(ltta, "gid", aggregate_ltta)
    result = trafficDB.LTTA.update_one(index, {
        "$set": {
            "ltta": payload_to_list(ltta)
        },
        "$currentDate": {
            "lastModified": True
        }
    }, upsert=True)
    rt = {
        "modified": result.modified_count
    }
    directory = os.path.join(current_app.root_path,
                             'static', 'traffic', 'insert')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, '%s_%d_%s_ltta.json' % (
        dt.strftime('%Y%m%d'), data_in['qtr'], data_in['city']))
    with open(filename, 'w') as f:
        json.dump(ltta, f)
    return jsonify(rt)


def update_inrix(data_in):
    trafficDB = mongo.db
    inrix = data_in['inrix']
    # convert gid and speed to number
    for i in range(len(inrix)):
        inr = inrix[i]
        inr["gid"] = int(inr["gid"])
        if "speed" in inr:
            inr["speed"] = int(inr["speed"])
        if "tt" in inr:
            inr["tt"] = float(inr["tt"])
    index, dt = get_index(data_in)
    result = trafficDB.INRIX.update_one(index, {
        "$set": {
            "inrix": inrix
        },
        "$currentDate": {
            "lastModified": True
        }
    }, upsert=True)
    rt = {
        "modified": result.modified_count
    }
    directory = os.path.join(current_app.root_path,
                             'static', 'traffic', 'update')
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = os.path.join(directory, '%s_%d_%s_inrix.json' % (
        dt.strftime('%Y%m%d'), data_in['qtr'], data_in['city']))
    with open(filename, 'w') as f:
        json.dump(inrix, f)
    return jsonify(rt)


def lamb_convert(array, lamb):
    result = []
    lamb = int(lamb)
    cur_val = None
    for idx, val in enumerate(array):
        if cur_val is None:
            if val is not None:
                if idx > 0:
                    result.append((cur_val, idx - 1))
            cur_val = val
            continue
        if val is None:
            result.append((cur_val, idx - 1))
            cur_val = val
            continue
        val = int(val)
        cur_val = int(cur_val)
        if val > cur_val:
            diff = val - cur_val
        else:
            diff = cur_val - val
        if diff > lamb:
            result.append((cur_val, idx - 1))
            cur_val = val
    result.append((cur_val, idx))
    return result


def get_ltta_by_date(date, city, meta):
    trafficDB = mongo.db
    res = trafficDB.LTTA.find({
        "city": city,
        "date": datetime.datetime.strptime(date, "%Y%m%d")
    })
    if res is None:
        return jsonify(None)
    g = {}
    for r in res:
        for item in r['ltta']:
            gid = item["gid"]
            if gid not in g:
                # Create a new list
                data = [r["qtr"], item["count"], round(item["ltta"], 2)]
                if 'std' in item:
                    data.append(round(item["std"], 2))
                g[gid] = [data]
            else:
                g[gid].append(data)
    if len(meta) > 0:
        networkDB = mongoClient.dma
        for gid in g:
            res = networkDB.Link.find_one({
                "city": city,
                "gid": gid
            })
            if res is None:
                continue
            g[gid] = {
                "ltta": g[gid],
                "link": {}
            }
            for item in meta:
                g[gid]["link"][item] = res[item]
    return jsonify(g)


def get_ltta_by_qtr(date, qtr, city, meta):
    print(meta)
    trafficDB = mongo.db
    r = trafficDB.LTTA.find_one({
        "city": city,
        "date": datetime.datetime.strptime(date, "%Y%m%d"),
        "qtr": int(qtr)
    })
    if r is None:
        return jsonify(None)
    return jsonify(r["ltta"])


def get_inrix_by_date(date, lamb, city):
    trafficDB = mongo.db
    res = trafficDB.INRIX.find({
        "city": city,
        "date": datetime.datetime.strptime(date, "%Y%m%d")
    })
    g = {}
    if res is None:
        return jsonify(None)
    for r in res:
        for item in r['inrix']:
            gid = item["gid"]
            if gid not in g:
                # Create a new list
                g[gid] = [None] * 96
            g[gid][r["qtr"]] = item["speed"]
    for gid in g:
        g[gid] = lamb_convert(g[gid], lamb)
    return jsonify(g)


def get_range_qtr(source):
    trafficDB = mongo.db
    date = request.args.get('date')
    qtr = request.args.get('qtr')
    dstr = date
    date = datetime.datetime.strptime(date, "%Y%m%d")
    qtr = int(qtr)
    start = datetime.datetime.strptime(dstr, "%Y%m%d")
    start.replace(hour=(qtr // 4), minute=(qtr % 4 // 15))
    end = datetime.datetime.strptime(dstr, "%Y%m%d")
    end.replace(hour=((qtr + 1) // 4), minute=((qtr + 1) % 4 // 15))
    print(start)
    r = trafficDB[source].find({
        "start": {
            "$lte": end
        },
        "end": {
            "$gte": start
        }
    })
    result = []
    for item in r:
        result.append(item["RID"])
    return jsonify(result)


def get_inrix_by_qtr(date, qtr):
    trafficDB = mongo.db
    r = trafficDB.INRIX.find_one({
        "date": datetime.datetime.strptime(date, "%Y%m%d"),
        "qtr": int(qtr)
    })
    if r is None:
        return jsonify(None)
    return jsonify(r["inrix"])
