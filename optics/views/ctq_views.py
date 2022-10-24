from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
from numpy.lib.function_base import append
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
import copy

bp = Blueprint('ctq', __name__, url_prefix='/ctq')

@bp.route('/static_ctq')
@login_required
def go_ctq():
    itemsList = ['att1310ose', 'att1550ose', 'mfd1310ose', 'fiberCutoffOse', 'cladDiaOse', 'cladOvoOse',
                 'eccOSe', 'coat2Dia', 'coat1Dia', 'zwl', 'slope', 'disp1285', 'disp1290',
                 'disp1550', 'pmd']

    return render_template('ctq_trend.html', itemList = itemsList)

@bp.route('/trend_ctq', methods = ['POST'])
@login_required
def cal_ctq():
    day = request.form['date']
    item = request.form['item']

    queryset = db.session.query(Common.spoolID,Common.measure_date, Common.drawNumber,\
        OTDR.att1310ose, OTDR.att1550ose,\
        MFD.mfd1310ose, Cutoff.fiberCutoffOse, 
        Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
        Coating.coat2Dia, Coating.coat1Dia,\
        Chromatic.zwl, Chromatic.slope,\
        Chromatic.disp1285, Chromatic.disp1290, Chromatic.disp1550,\
        PMD.pmd
        )\
        .filter(Common.measure_date>=datetime.strptime(day, '%Y-%m-%d') - timedelta(days=10))\
        .filter(Common.measure_date<=day)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.spoolID == MFD.spoolID)\
        .filter(Common.spoolID == Cutoff.spoolID)\
        .filter(Common.spoolID == Geometry.spoolID)\
        .filter(Common.spoolID == Coating.spoolID)\
        .filter(Common.spoolID == Chromatic.spoolID)\
        .filter(Common.spoolID == PMD.spoolID)

    df = pd.read_sql_query(queryset.statement, queryset.session.bind)
    df = df[['measure_date', 'drawNumber', item]]
    df = df.replace(0, np.nan)

    date_range = (df['measure_date'].drop_duplicates()).sort_values()
    df = df.groupby(['drawNumber', 'measure_date']).mean()
    df = df.unstack()

    dates = []
    for i in range(0, date_range.shape[0]):
        dates.append((date_range.iloc[i]).strftime('%Y-%m-%d'))
    df.columns = dates
    df['tower'] = df.index
    #######################################################
    valueList = []
    valuesList_nonDraw = []
    for i in range(0, df.shape[0]):
        static_values = []
        static_values.append(df.iloc[i]['tower'])
        for date in range(0, len(dates)):
            static_values.append(round(df.iloc[i][date], 3))
        valueList.append(static_values)
    valuesList_nonDraw = copy.deepcopy(valueList)
    for i in range(0, len(valuesList_nonDraw)):
        valuesList_nonDraw[i].pop(0)

    return render_template('ctq_result.html', day = day, item = item, valueList = valueList, 
                           valuesList_nonDraw = valuesList_nonDraw, dates = dates)