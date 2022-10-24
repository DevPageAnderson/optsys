from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
import pandas as pd
from datetime import date, datetime
from pandas.core.frame import DataFrame
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.utils import redirect, secure_filename
from optics import db
from optics.models import MFD, PMD, Chromatic, Coating, Common, Cutoff, Geometry, NcrCode, Preform, Resin, User, OTDR, DrawNumber
from datetime import datetime
import os
import sqlite3
import numpy as np
sqlite3.register_adapter(np.int64, lambda val: int(val))
from sqlalchemy import or_
from .auth_views import login_required
bp = Blueprint('ncr', __name__, url_prefix='/ncr')

@bp.route('/draw')
@login_required
def go_draw():
    formList = Preform.query.all()
    preformList = ['None']
    for pre in formList:
        preformList.append(pre.preform)
    
    resins= Resin.query.all()
    resinList = ['None']
    for re in resins:
        resinList.append(re.resin)
        
    ncrs = NcrCode.query.all()
    ncrList = ['None']
    for n in ncrs:
        ncrList.append(n.code)

    return render_template('ncr_draw.html', preformList = preformList, resinList = resinList,\
        ncrList = ncrList)

@bp.route('/draw_result', methods = ['POST'])
@login_required
def cal_draw():
    start = request.form['start_date']
    stop = request.form['stop_date']
    preform = request.form['preform']
    resin = request.form['resin']
    ncr = request.form['ncr']

    drawList = DrawNumber.query.all()
    dList = []
    for draw in drawList:
        dList.append(draw.drawNumber)

    queryset_total = db.session.query(Common.spoolID,Common.measure_date, Common.com, OTDR.length,\
        Common.drawNumber, Common.resin)\
        .filter(Common.measure_date>=start)\
        .filter(Common.measure_date<=stop)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.com == preform)\
        .filter(Common.resin == resin)
    df_total = pd.read_sql_query(queryset_total.statement, queryset_total.session.bind)
    df_total = df_total[['drawNumber', 'length']]

    df_total = df_total.groupby(['drawNumber']).sum()
    df_total.unstack()
    df_total['drawT'] = df_total.index

    TotalDic = {}
    for i in range(0, df_total.shape[0]):
        if df_total.iloc[i]['length']:
            TotalDic[df_total.iloc[i]['drawT']] = df_total.iloc[i]['length']

    queryset_part = db.session.query(Common.spoolID,Common.measure_date, Common.com, OTDR.length,\
        Common.drawNumber, Common.resin)\
        .filter(Common.measure_date>=start)\
        .filter(Common.measure_date<=stop)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.com == preform)\
        .filter(Common.resin == resin)\
        .filter(or_(Common.ncrCode1 == ncr , Common.ncrCode2 == ncr , Common.ncrCode3 == ncr ))
    df_part = pd.read_sql_query(queryset_part.statement, queryset_part.session.bind)
    df_part = df_part[['drawNumber', 'length']]

    df_part = df_part.groupby(['drawNumber']).sum()
    df_part.unstack()
    df_part['drawT'] = df_part.index

    PartDic = {}
    for i in range(0, df_part.shape[0]):
        if df_part.iloc[i]['length']:
            PartDic[df_part.iloc[i]['drawT']] = df_part.iloc[i]['length']

    labels = []
    values = []
    for key, value in TotalDic.items():
        if key in PartDic:
            labels.append(key)
            values.append(PartDic[key] / value *100)
        else:
            labels.append(key)
            values.append(0.00)

    return render_template('ncrDraw_result.html', labels = labels, values = values, ncr = ncr, start=start, stop=stop, resin=resin, preform=preform)