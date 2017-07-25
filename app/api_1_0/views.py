import datetime
import json
import math
import os

import pymongo
from flask import abort, current_app, jsonify, make_response, request

from .ltta import *

from . import api
from .. import mongo

"""""
"API"
"""""


@api.route('/traffic/mm', methods=["GET", "POST"])
def traffic_mm():
    if request.method == 'POST':
        data_in = request.json
        return update_mm(data_in)
    else:
        return get_range_qtr("MM")


@api.route('/traffic/ltte', methods=["GET", "POST"])
def traffic_ltte():
    if request.method == 'POST':
        data_in = request.json
        return update_ltte(data_in)
    else:
        return get_range_qtr("LTTE")


@api.route('/traffic/revservation/ltte')
def revservation_ltte():
    rid = request.args.get("rid")
    trafficDB = mongo.db
    r = trafficDB.LTTE.find_one({
        "RID": rid
    })
    return jsonify(r["ltte"])


@api.route('/traffic/ltta', methods=['GET', 'POST'])
def traffic_ltta():
    if request.method == 'POST':
        # UPDATE
        data_in = request.json
        return update_ltta(data_in)
    else:  # GET
        date = request.args.get("date")
        qtr = request.args.get("qtr")
        city = request.args.get("city")
        meta = request.args.getlist("meta")
        if qtr is None:
            return get_ltta_by_date(date, city, meta)
        else:
            return get_ltta_by_qtr(date, qtr, city, meta)


@api.route('/traffic/inrix', methods=['GET', 'POST'])
def traffic_inrix():
    if request.method == 'POST':
        data_in = request.json
        return update_inrix(data_in)
    else:
        date = request.args.get("date")
        city = request.args.get("city")
        qtr = request.args.get("qtr")
        lamb = request.args.get("lambda")
        if lamb is None:
            lamb = 0
        if qtr is None:
            return get_inrix_by_date(date, lamb, city)
        else:
            return get_inrix_by_qtr(date, qtr, city)


@api.route('/traffic/dates/<mod>')
def get_dates(mod):
    return get_days(mod.upper())


"""""""""
"Helpers"
"""""""""


def get_days(source):
    end = request.args.get('end')
    days = request.args.get('days')
    city = request.args.get('city')
    weekday = request.args.get('weekday')

    # city is required
    if city is None:
        return make_response("city not specified", 400)

    # end default to today
    if end is None:
        end_datetime = datetime.datetime.utcnow()
        end_date = datetime.date.today()
    else:  # if end is specified
        end_datetime = datetime.datetime.strptime(end, "%Y%m%d")
        end_date = end_datetime.date()

    result = []
    filt = {}
    # Verify Integrity of Weekday
    # If weekday is not specified
    # return all days
    if weekday is not None:
        weekday = int(weekday)
        if weekday < 0 or weekday > 6:
            return make_response(
                "invalid weekday (0 Monday - 6 Sunday)", 400
            )
        filt["weekday"] = weekday
    filt["date"] = {
        "$lte": end_datetime
    }
    if days is not None:
        days = int(days)
        if days < 0:
            return make_response(
                "Invalid days (>= 0)", 400
            )

    result = []
    trafficDB = mongo.db
    query = trafficDB[source].find(filt).sort(
        "date", pymongo.ASCENDING).distinct("date")[:days]
    # if days is None, there are no limits
    # if days is set, return days result
    if days is not None and days > 0:
        query = query[:days]
    for r in query:
        result.append(r.strftime("%Y%m%d"))
    return jsonify(result)
