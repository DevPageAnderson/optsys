from re import L
from typing import Reversible
from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
import pandas as pd
from datetime import date, datetime, timedelta
from pandas.core.frame import DataFrame
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.utils import redirect, secure_filename
from optics import db
from optics.models import MFD, PMD, Chromatic, Coating, Common, Cutoff, DrawNumber, Geometry, Preform, User, OTDR
from datetime import datetime
import os
import sqlite3
import numpy as np
from .auth_views import login_required
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('realTime', __name__, url_prefix='/realTime')

@bp.route('/realTime_measue')
@login_required
def go_measure():
    return render_template('realTime_measure.html')

@bp.route('/cal_measure', methods = ['POST'])
@login_required
def cal_measure():
    start = request.form['start_date']
    stop = request.form['stop_date']
    results = []

    queryset_total = db.session.query(Common.spoolID,Common.measure_date, OTDR.length)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.measure_date>=start)\
        .filter(Common.measure_date<=stop)
    queryset_rework = db.session.query(Common.spoolID,Common.measure_date, OTDR.length, Common.rework)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.rework == 'Y')\
        .filter(Common.measure_date>=start)\
        .filter(Common.measure_date<=stop)
    queryset_daily = db.session.query(Common.spoolID,Common.measure_date, OTDR.length)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.measure_date>=start)\
        .filter(Common.measure_date<=stop)

    df = pd.read_sql_query(queryset_total.statement, queryset_total.session.bind)
    df = df.replace(0, np.nan)
    df_rework = pd.read_sql_query(queryset_rework.statement, queryset_rework.session.bind)
    df_rework = df_rework.replace(0, np.nan)
    df_daily = pd.read_sql_query(queryset_daily.statement, queryset_daily.session.bind)
    df_daily = df_daily.replace(0, np.nan)

    df_daily = df_daily.drop(['spoolID'],axis='columns')
    df_daily_length = df_daily.groupby('measure_date').sum()/1000
    df_daily_spool = df_daily.groupby('measure_date').count()
    df_daily_length.unstack()
    df_daily_spool.unstack()
    df_daily_length['date'] = df_daily_length.index
    df_daily_spool['date'] = df_daily_spool.index

    dates = []
    for i in range(0, df_daily_spool.shape[0]):
        dates.append(df_daily_spool.iloc[i]['date'].strftime('%Y-%m-%d'))

    valueList = []
    for i in range(0, df_daily_spool.shape[0]):
        valueList.append(df_daily_spool.iloc[i]['length'])

    totalLength = df['length'].sum()/1000
    totalSpool = df.shape[0]
    averageLength = totalLength/totalSpool
    longSpool = df[df['length'] >= 75000].shape[0]
    reworkLength = df_rework['length'].sum()/1000
    reworkSpool = df_rework.shape[0]

    results.append(totalLength)
    results.append(totalSpool)
    results.append(reworkLength)
    results.append(reworkSpool)
    results.append(averageLength)
    results.append(longSpool)

    return render_template('realTime_measure_result.html', results = results, dates = dates, valueList = valueList)