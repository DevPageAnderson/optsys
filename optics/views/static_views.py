from operator import methodcaller
from re import M
from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
import pandas as pd
from datetime import date, datetime
from pandas.core.frame import DataFrame
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.utils import redirect, secure_filename
from optics import db
from optics.models import MFD, PMD, Chromatic, Coating, Common, Cutoff, Geometry, Preform, User, OTDR
from datetime import datetime
import os
import sqlite3
import numpy as np
from . auth_views import login_required
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('state', __name__, url_prefix='/state')

@bp.route('/static_home')
@login_required
def go_static():
    formList = Preform.query.all()
    preformList = ['None']
    for pre in formList:
        preformList.append(pre.preform)
    return render_template('basic_static.html', preformList = preformList)

@bp.route('/total', methods = ['POST'])
@login_required
def cal_total():
    start = request.form['start_date']
    stop = request.form['stop_date']
    preform = request.form['preform']

    if preform == 'None':
        queryset = db.session.query(Common.spoolID,Common.measure_date, OTDR.att1310ose, OTDR.att1550ose,\
            MFD.mfd1310ose, Cutoff.fiberCutoffOse, Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
            Coating.coat2Dia, Coating.coat1Dia, Chromatic.zwl, Chromatic.slope, Chromatic.disp1285,\
            Chromatic.disp1290, Chromatic.disp1550, PMD.pmd
            )\
            .filter(Common.spoolID == OTDR.spoolID)\
            .filter(Common.spoolID == MFD.spoolID)\
            .filter(Common.spoolID == Cutoff.spoolID)\
            .filter(Common.spoolID == Geometry.spoolID)\
            .filter(Common.spoolID == Coating.spoolID)\
            .filter(Common.spoolID == Chromatic.spoolID)\
            .filter(Common.spoolID == PMD.spoolID)\
            .filter(Common.measure_date>=start)\
            .filter(Common.measure_date<=stop)
    elif preform == 'coat200':
        queryset = db.session.query(Common.spoolID,Common.measure_date, Common.coat200, OTDR.att1310ose, OTDR.att1550ose,\
            MFD.mfd1310ose, Cutoff.fiberCutoffOse, Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
            Coating.coat2Dia, Coating.coat1Dia, Chromatic.zwl, Chromatic.slope, Chromatic.disp1285,\
            Chromatic.disp1290, Chromatic.disp1550, PMD.pmd
            )\
            .filter(Common.coat200 == 'OK')\
            .filter(Common.spoolID == OTDR.spoolID)\
            .filter(Common.spoolID == MFD.spoolID)\
            .filter(Common.spoolID == Cutoff.spoolID)\
            .filter(Common.spoolID == Geometry.spoolID)\
            .filter(Common.spoolID == Coating.spoolID)\
            .filter(Common.spoolID == Chromatic.spoolID)\
            .filter(Common.spoolID == PMD.spoolID)\
            .filter(Common.measure_date>=start)\
            .filter(Common.measure_date<=stop)
    else:
        queryset = db.session.query(Common.spoolID,Common.measure_date, OTDR.att1310ose, OTDR.att1550ose,\
            MFD.mfd1310ose, Cutoff.fiberCutoffOse, Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
            Coating.coat2Dia, Coating.coat1Dia, Chromatic.zwl, Chromatic.slope, Chromatic.disp1285,\
            Chromatic.disp1290, Chromatic.disp1550, PMD.pmd
            )\
            .filter(Common.com == preform)\
            .filter(Common.spoolID == OTDR.spoolID)\
            .filter(Common.spoolID == MFD.spoolID)\
            .filter(Common.spoolID == Cutoff.spoolID)\
            .filter(Common.spoolID == Geometry.spoolID)\
            .filter(Common.spoolID == Coating.spoolID)\
            .filter(Common.spoolID == Chromatic.spoolID)\
            .filter(Common.spoolID == PMD.spoolID)\
            .filter(Common.measure_date>=start)\
            .filter(Common.measure_date<=stop)

    df = pd.read_sql_query(queryset.statement, queryset.session.bind)
    df = df.replace(0, np.nan)
    df.to_csv('C:\\condaEnv\\web_api\\optics\\data\\test.csv')

    itemsList = ['att1310ose', 'att1550ose', 'mfd1310ose', 'fiberCutoffOse', 'cladDiaOse', 'cladOvoOse',\
                'eccOse', 'coat2Dia', 'coat1Dia', 'zwl', 'slope', 'disp1285', 'disp1290', 'disp1550',\
                    'pmd']

    specListL = [0.34, 0.21, 8.85, 1320, 124.3, 0.9,\
                0.5, 235, 199, 1302, 0.092, 3.2, 3.5, 17.5,\
                    0.07]
    
    specListU = [0.34, 0.21, 9.2, 1320, 124.7, 0.9,\
                0.5, 255, 210, 1322, 0.092, 3.2, 3.5, 17.5,\
                    0.07]
    itemsNameList = ['광손실 1310nm', '광손실 1550nm', 'MFD', '차단파장', '클래드 외경', '클래드 비원율',\
                    'ECC', '코팅외경 2차', '코팅외경 1차', '영분산 파장', '기울기', '색분산 1285nm',\
                    '색분산 1290nm', '색분산 1550nm', 'PMD']
    valueList = []

    if df.shape[0] !=0:
        for i in range(0, len(itemsList)):
            static_values = []
            static_values.append(itemsNameList[i])
            static_values.append(round(df[itemsList[i]].describe()['25%'], 3))
            static_values.append(round(df[itemsList[i]].describe()['mean'], 3))
            static_values.append(round(df[itemsList[i]].describe()['75%'], 3))
            static_values.append(round(df[itemsList[i]].describe()['std'], 3))
            
            mean = df[itemsList[i]].describe()['mean']
            std = df[itemsList[i]].describe()['std']
            cpkL = (mean - specListL[i]) / (3*std)
            cpkU = (specListU[i] - mean) / (3*std)
            minmaxList = []
            if cpkL > 0:
                minmaxList.append(cpkL)
            if cpkU > 0:
                minmaxList.append(cpkU)
            if minmaxList:
                static_values.append(round(min(minmaxList), 3))
            valueList.append(static_values)

    return render_template('static_result.html', preform = preform, valueList = valueList, start = start, stop = stop)