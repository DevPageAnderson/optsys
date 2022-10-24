from dis import dis
from pdb import pm
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
from optics.models import MFD, PMD, Chromatic, Coating, Common, Cutoff, DrawNumber, Geometry, Preform, User, OTDR, Resin
from datetime import datetime
import os
import sqlite3
import numpy as np
from .auth_views import login_required
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('yield', __name__, url_prefix='/yield')

@bp.route('/yield')
@login_required
def go_yield():
    productType = ['LW', 'A1', 'A2']
    resinList = Resin.query.all()
    rList = ['None']
    for re in resinList:
        rList.append(re.resin)
    return render_template('yield_input.html', productType = productType, rList = rList)

@bp.route('/yield_result', methods = ['POST'])
@login_required
def cal_yield():
    start_date = request.form['start_date']
    stop_date = request.form['stop_date']
    resin = request.form['resin']
    productType = request.form['productType']

    att1310 = float(request.form['att1310'])
    att1550 = float(request.form['att1550'])
    att1383 = float(request.form['att1383'])
    att1625 = float(request.form['att1625'])
    mfd1310L = float(request.form['mfd1310L'])
    mfd1310U = float(request.form['mfd1310U'])
    cutoff = float(request.form['cutoff'])
    cladDiaL = float(request.form['cladDiaL'])
    cladDiaU = float(request.form['cladDiaU'])
    cladovo = float(request.form['cladovo'])
    ecc = float(request.form['ecc'])
    coat2L = float(request.form['coat2L'])
    coat2U = float(request.form['coat2U'])
    zwlL = float(request.form['zwlL'])
    zwlU = float(request.form['zwlU'])
    slope = float(request.form['slope'])
    disp1285 = float(request.form['disp1285'])
    disp1290 = float(request.form['disp1290'])
    disp1550 = float(request.form['disp1550'])
    pmd = float(request.form['pmd'])
    
    queryset = db.session.query(Common.spoolID,Common.measure_date, OTDR.att1310ose, OTDR.att1550ose,\
        Common.resin, Common.productType, OTDR.length,\
        MFD.mfd1310ose, Cutoff.fiberCutoffOse, Geometry.cladDiaOse, Geometry.cladOvoOse, Geometry.eccOse,\
        Coating.coat2Dia, Coating.coat1Dia, Chromatic.zwl, Chromatic.slope, Chromatic.disp1285,\
        Chromatic.disp1290, Chromatic.disp1550, PMD.pmd, OTDR.att1383ose, OTDR.att1625ose
        )\
        .filter(Common.measure_date>=start_date)\
        .filter(Common.measure_date<=stop_date)\
        .filter(Common.spoolID == OTDR.spoolID)\
        .filter(Common.spoolID == MFD.spoolID)\
        .filter(Common.spoolID == Cutoff.spoolID)\
        .filter(Common.spoolID == Geometry.spoolID)\
        .filter(Common.spoolID == Coating.spoolID)\
        .filter(Common.spoolID == Chromatic.spoolID)\
        .filter(Common.spoolID == PMD.spoolID)\
        .filter(Common.resin == resin)\
        .filter(Common.productType == productType)

    df = pd.read_sql_query(queryset.statement, queryset.session.bind)

    if df.shape[0] != 0:
        df = df.replace(0, np.nan)
        df.to_csv('test.csv')
        passCountList = []
        totalCount = df.shape[0]
        print(totalCount)
        passCountList.append(df[df['att1310ose'] <= att1310].shape[0])
        passCountList.append(df[df['att1550ose'] <= att1550].shape[0])
        passCountList.append(df[df['att1383ose'] <= att1383].shape[0])
        passCountList.append(df[df['att1625ose'] <= att1625].shape[0])
        passCountList.append(df[(df['mfd1310ose'] >= mfd1310L) & (df['mfd1310ose'] <= mfd1310U)].shape[0])
        passCountList.append(df[df['fiberCutoffOse'] <= cutoff].shape[0])
        passCountList.append(df[(df['cladDiaOse'] >= cladDiaL) & (df['cladDiaOse'] <= cladDiaU)].shape[0])
        passCountList.append(df[df['cladOvoOse'] <= cladovo].shape[0])
        passCountList.append(df[df['eccOse'] <= ecc].shape[0])
        passCountList.append(df[(df['coat2Dia'] >= coat2L) & (df['coat2Dia'] <= coat2U)].shape[0])
        passCountList.append(df[(df['zwl'] >= zwlL) & (df['zwl'] <= zwlU)].shape[0])
        passCountList.append(df[df['slope'] <= slope].shape[0])
        passCountList.append(df[df['disp1285'] <= disp1285].shape[0])
        passCountList.append(df[df['disp1290'] <= disp1290].shape[0])
        passCountList.append(df[df['disp1550'] <= disp1550].shape[0])
        passCountList.append(df[df['pmd'] <= pmd].shape[0])
        #전체 수율 계산
        #df = df[df['att1310ise'] <= att1310]
        df = df[df['att1310ose'] <= att1310]
        #df = df[df['att1550ise'] <= att1550]
        df = df[df['att1550ose'] <= att1550]
        #df = df[df['att1383ise'] <= att1383]
        df = df[df['att1383ose'] <= att1383]
        #df = df[df['att1625ise'] <= att1625]
        df = df[df['att1625ose'] <= att1625]
        #df = df[df['mfd1310ise'] >= mfd1310L]
        #df = df[df['mfd1310ise'] <= mfd1310U]
        df = df[df['mfd1310ose'] >= mfd1310L]
        df = df[df['mfd1310ose'] <= mfd1310U]
        df = df[df['fiberCutoffOse'] <= cutoff]
        #df = df[df['cladDiaIse'] >= cladDiaL]
        #df = df[df['cladDiaIse'] <= cladDiaU]
        df = df[df['cladDiaOse'] >= cladDiaL]
        df = df[df['cladDiaOse'] <= cladDiaU]
        #df = df[df['cladOvoIse'] <= cladovo]
        df = df[df['cladOvoOse'] <= cladovo]
        #df = df[df['eccIse'] < ecc]
        df = df[df['eccOse'] < ecc]
        df = df[df['coat2Dia'] >= coat2L]
        df = df[df['coat2Dia'] <= coat2U]
        df = df[df['zwl'] >= zwlL]
        df = df[df['zwl'] <= zwlU]
        df = df[df['slope'] <= slope]
        df = df[df['disp1285'] <= disp1285]
        df = df[df['disp1290'] <= disp1290]
        df = df[df['disp1550'] <= disp1550]
        df = df[df['pmd'] <= pmd]

        if df.shape[0] != 0:
            result = round(df.shape[0] / totalCount * 100, 2)
        else:
            result = 0

        for cnt in range(0, len(passCountList)):
            if(passCountList[cnt] != 0):
                passCountList[cnt] = passCountList[cnt] / totalCount * 100

        return render_template('yield_result.html', passCountList = passCountList, result = result)
    else:
        return render_template('yield_result_none.html')