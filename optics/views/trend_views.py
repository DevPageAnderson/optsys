from operator import methodcaller
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

bp = Blueprint('trend', __name__, url_prefix='/trend')

@bp.route('/static_trend')
@login_required
def go_trend():
    drawList = DrawNumber.query.all()
    dList = []
    for draw in drawList:
        dList.append(draw.drawNumber)
    return render_template('daily_trend.html', drawList = dList)

@bp.route('/trend', methods = ['POST'])
@login_required
def cal_trend():
    day = request.form['date']
    draw = request.form['draw']

    queryset = db.session.query(Common.spoolID,Common.measure_date, OTDR.att1310ose, OTDR.att1550ose,\
        MFD.mfd1310ose, Cutoff.fiberCutoffOse, Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
        Coating.coat2Dia, Coating.coat1Dia, Chromatic.zwl, Chromatic.slope, Chromatic.disp1285,\
        Chromatic.disp1290, Chromatic.disp1550, PMD.pmd
        )\
        .filter(Common.drawNumber == draw)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.spoolID == MFD.spoolID)\
        .filter(Common.spoolID == Cutoff.spoolID)\
        .filter(Common.spoolID == Geometry.spoolID)\
        .filter(Common.spoolID == Coating.spoolID)\
        .filter(Common.spoolID == Chromatic.spoolID)\
        .filter(Common.spoolID == PMD.spoolID)\
        .filter(Common.measure_date>=datetime.strptime(day, '%Y-%m-%d') - timedelta(days=10))\
        .filter(Common.measure_date<=day)

    df = pd.read_sql_query(queryset.statement, queryset.session.bind)
    df = df.replace(0, np.nan)
    df = df.drop(['spoolID'],axis='columns')
    df = df.groupby('measure_date').mean()
    df = df.transpose()
    #df.to_csv('C:\\condaEnv\\web_api\\optics\\data\\test.csv')

    itemsList = ['att1310ose', 'att1550ose', 'mfd1310ose', 'fiberCutoffOse', 'cladDiaOse', 'cladOvoOse',\
                'eccOse', 'coat2Dia', 'coat1Dia', 'zwl', 'slope', 'disp1285', 'disp1290', 'disp1550',\
                    'pmd']
    itemsNameList = ['광손실 1310nm', '광손실 1550nm', 'MFD', '차단파장', '클래드 외경', '클래드 비원율',\
                    'ECC', '코팅외경 2차', '코팅외경 1차', '영분산 파장', '기울기', '색분산 1285nm',\
                    '색분산 1290nm', '색분산 1550nm', 'PMD']
    valueList = []
    dates = []
    dateList = df.columns.tolist()
    for date in dateList:
        dates.append(date.strftime('%Y-%m-%d'))

    for i in range(0, len(itemsList)):
        static_values = []
        static_values.append(itemsNameList[i])
        for date in range(0, len(dates)):
            static_values.append(round(df.iloc[i][date], 3))
            #print(df.iloc[i][date])

        valueList.append(static_values)

    return render_template('trend_result.html', day = day, draw = draw, valueList = valueList, dates = dates)