from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.utils import redirect, secure_filename
from optics import db
from optics.models import MFD, OTDR, Chromatic, Coating, Common, Cutoff, DrawNumber, Geometry, PMD, MacroBending, NcrCode, Preform, Resin
import os
import sqlite3
import numpy as np
from .auth_views import login_required
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('information', __name__, url_prefix='/information')

@bp.route('/join')
@login_required
def table_join():
    SQL = """SELECT * FROM Common WHERE measure_date BETWEEN "2021-11-06" AND "2021-11-07"; """
    df = pd.read_sql_query(SQL, db.session.bind)
    df.to_csv('C:\\condaEnv\\web_api\\optics\\data\\test.csv')
    return 'complete save csv file to local'

@bp.route('/migrate')
@login_required
def migration():
    return render_template('migration.html')

@bp.route('/upload', methods = ["POST"])
@login_required
def upload():
    file = request.files['csv_name']
    fileName = secure_filename(file.filename)
    file.save(os.path.join('./upload', fileName))
    return redirect(url_for('information.migrate')) 

@bp.route('/preform_register', methods = ["POST"])
@login_required
def preformRegister():
    _preform = request.form['preform_name']
    _description = request.form['preform_description']
    query_preform = Preform(create_date=datetime.now(), 
                        preform = _preform, description = _description
                )
    db.session.add(query_preform)
    db.session.commit()
    return '프리폼 정보 업데이트 완료...'

@bp.route('/resin_register', methods = ["POST"])
@login_required
def resinRegister():
    _resin = request.form['resin_name']
    _description = request.form['resin_description']
    query_resin = Resin(create_date=datetime.now(), 
                        resin = _resin, description = _description
                )
    db.session.add(query_resin)
    db.session.commit()
    return '레진 정보 업데이트 완료...'

@bp.route('/ncrCodeRegister', methods = ["POST"])
@login_required
def ncrCodeRegister():
    _ncrCode = request.form['ncr_code']
    _description = request.form['ncr_description']
    query_ncr = NcrCode(create_date = datetime.now(), 
                        code = _ncrCode,
                        description = _description
                )
    db.session.add(query_ncr)
    db.session.commit()
    return '이상코드 등록 완료...'

@bp.route('drawRegister', methods = ["POST"])
@login_required
def drawNumberRegister():
    _drawNumber = request.form['draw_number']
    query_draw = DrawNumber(create_date = datetime.now(),
                            drawNumber = _drawNumber)
    db.session.add(query_draw)
    db.session.commit()
    return '드로우 호기 등록 완료...'

@bp.route('/migration')
@login_required
def migrate():
    lwpfList = ['2M', 'LM', 'SE', 'LE', 'W0', 'SM']
    a1List = ['ZW']
    a2List = ['AW', 'ZM', 'ZL']
    #200um도 확인해야 함
    file_path = './upload/meas.csv'
    
    try:
        dataFrame = pd.read_csv('./upload/meas.csv')
    except:
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'Can not make pandas data frame...'
    else:
        cnt = dataFrame.shape[0]
        for i in range(0, cnt):

            _ncrCode1 = None
            _ncrCode2 = None
            _ncrCode3 = None

            massInfo = str(dataFrame.iloc[i]['spoolno2'])
            _resin = massInfo[11:12]
            _draw = massInfo[12:14]
            _pt = massInfo[15:17]
            _com = str(dataFrame.iloc[i]['spoolno'])[0:2]
            
            if _com in lwpfList:
                _productType = 'LW'
            elif _com in a1List:
                _productType = 'A1'
            elif _com in a2List:
                _productType = 'A2'
            else:
                _productType = None

            if str(dataFrame.iloc[i]['spoolno'])[12:13] == '0':
                _rework = 'N'
            else:
                _rework = 'Y'
            
            if str(dataFrame.iloc[i]['graph1550']) != 'nan':
                ncrString = str(dataFrame.iloc[i]['graph1550']).strip().split('/')
                for n in range(0, len(ncrString)):
                    if n==0:
                        _ncrCode1 = ncrString[0]
                    elif n==1:
                        _ncrCode2 = ncrString[1]
                    elif n==2:
                        _ncrCode3 = ncrString[2]
            #200um 확인
            if dataFrame.iloc[i]['coat2o'] < 220:
                _coat200 = 'OK'
            else:
                _coat200 = 'NO'

            duplicate_check = Common.query.filter(Common.spoolID == dataFrame.iloc[i]['spoolno']).first()

            if duplicate_check:
                data = duplicate_check
                idx = duplicate_check.id
                data.create_date = datetime.now()
                data.measure_date = datetime.strptime(str(dataFrame.iloc[i]['hdate']), '%Y.%m.%d')
                data.measure_batchNumber = dataFrame.iloc[i]['batch_no']
                data.info = dataFrame.iloc[i]['spoolno2']
                data.preform = dataFrame.iloc[i]['preform']
                data.ncrCode1 = _ncrCode1
                data.ncrCode2 = _ncrCode2
                data.ncrCode3 = _ncrCode3
                data.resin = _resin
                data.drawNumber = _draw
                data.ptNumber = _pt
                data.com = _com
                data.rework = _rework
                data.productType = _productType
                data.coat200 = _coat200

                data = OTDR.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.length = dataFrame.iloc[i]['otdrlength']
                data.att1310ise = dataFrame.iloc[i]['l1310i']
                data.att1310ose = dataFrame.iloc[i]['l1310o']
                data.att1550ise = dataFrame.iloc[i]['l1550i']
                data.att1550ose = dataFrame.iloc[i]['l1550o']
                data.att1383ise = dataFrame.iloc[i]['l1383i']
                data.att1383ose = dataFrame.iloc[i]['l1383o']
                data.att1625ise = dataFrame.iloc[i]['l1625i']
                data.att1625ose = dataFrame.iloc[i]['l1625o']

                data = MFD.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.mfd1310ise = dataFrame.iloc[i]['mfd13pi']
                data.mfd1310ose = dataFrame.iloc[i]['mfd13po']
                data.mfd1550ise = dataFrame.iloc[i]['mfd15pi']
                data.mfd1550ose = dataFrame.iloc[i]['mfd15po']
                
                data = Cutoff.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.fiberCutoffIse = dataFrame.iloc[i]['cutoffi']
                data.fiberCutoffOse = dataFrame.iloc[i]['cutoffo']
                data.cableCutoff = dataFrame.iloc[i]['coat2i']

                data = Geometry.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.cladDiaIse = dataFrame.iloc[i]['claddiai'] 
                data.cladDiaOse = dataFrame.iloc[i]['claddiao']
                data.cladOvoIse = dataFrame.iloc[i]['cladovi']
                data.cladOvoOse = dataFrame.iloc[i]['cladovo']
                data.eccIse = dataFrame.iloc[i]['ecci']
                data.eccOse = dataFrame.iloc[i]['ecco']
                data.coreOvoIse = dataFrame.iloc[i]['coreovi']
                data.coreOvoOse = dataFrame.iloc[i]['coreovo']
                data.coreDiaIse = dataFrame.iloc[i]['corediai']
                data.coreDiaOse = dataFrame.iloc[i]['corediao']

                data = Coating.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.coat2Dia = dataFrame.iloc[i]['coat2o']
                data.coat2Ovo = dataFrame.iloc[i]['coat2ovo']
                data.coat2ECC = dataFrame.iloc[i]['coatecco']
                data.coat1Dia = dataFrame.iloc[i]['coat1o']
                data.coat1Ovo = dataFrame.iloc[i]['coat1ovo']

                data = Chromatic.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.zwl = dataFrame.iloc[i]['dispzero']
                data.slope = dataFrame.iloc[i]['dispslope']
                data.disp1285 = dataFrame.iloc[i]['max1285']
                data.disp1290 = dataFrame.iloc[i]['max1290']
                data.disp1330 = dataFrame.iloc[i]['max1330']
                data.disp1550 = dataFrame.iloc[i]['max1550']

                data = PMD.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.pmd = dataFrame.iloc[i]['pmd15']

                data = MacroBending.query.get(idx)
                data.common = duplicate_check.id
                data.create_date = datetime.now()
                data.R7_1550 = dataFrame.iloc[i]['coat2ovi']
                data.R7_1625 = dataFrame.iloc[i]['dmd_in']
                data.R10_1550 = dataFrame.iloc[i]['dmd_out']
                data.R10_1625 = dataFrame.iloc[i]['dmd_slide']
                data.R15_1550 = dataFrame.iloc[i]['r15mm_20turn_l1550']
                data.R15_1625 = dataFrame.iloc[i]['r15mm_20turn_l1625']
                db.session.commit()
    
            else:
                query_common = Common(spoolID=dataFrame.iloc[i]['spoolno'], create_date=datetime.now(),
                                measure_date = datetime.strptime(str(dataFrame.iloc[i]['hdate']), '%Y.%m.%d'),
                                measure_batchNumber=dataFrame.iloc[i]['batch_no'],
                                info=dataFrame.iloc[i]['spoolno2'], preform=dataFrame.iloc[i]['preform'],
                                ncrCode1 = _ncrCode1,
                                ncrCode2 = _ncrCode2,
                                ncrCode3 = _ncrCode3,
                                resin = _resin,
                                drawNumber = _draw,
                                ptNumber = _pt,
                                com = _com,
                                rework = _rework,
                                productType = _productType,
                                coat200 = _coat200
                                )

                rows = db.session.query(Common).count()

                query_otdr = OTDR(spoolID=dataFrame.iloc[i]['spoolno'], common_id = rows+1,
                                create_date=datetime.now(), 
                            length=dataFrame.iloc[i]['otdrlength'],
                            att1310ise=dataFrame.iloc[i]['l1310i'], att1310ose=dataFrame.iloc[i]['l1310o'],
                            att1550ise=dataFrame.iloc[i]['l1550i'], att1550ose=dataFrame.iloc[i]['l1550o'],
                            att1383ise=dataFrame.iloc[i]['l1383i'], att1383ose=dataFrame.iloc[i]['l1383o'],
                            att1625ise=dataFrame.iloc[i]['l1625i'], att1625ose=dataFrame.iloc[i]['l1625o']
                            )

                query_mfd = MFD(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                common_id = rows+1,
                                mfd1310ise = dataFrame.iloc[i]['mfd13pi'],
                                mfd1310ose = dataFrame.iloc[i]['mfd13po'],
                                mfd1550ise = dataFrame.iloc[i]['mfd15pi'],
                                mfd1550ose = dataFrame.iloc[i]['mfd15po']
                                )

                query_cutoff = Cutoff(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                    common_id = rows+1,
                                    fiberCutoffIse = dataFrame.iloc[i]['cutoffi'],
                                    fiberCutoffOse = dataFrame.iloc[i]['cutoffo'],
                                    cableCutoff = dataFrame.iloc[i]['coat2i']
                                )

                query_geometry = Geometry(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                        common_id = rows+1,
                                        cladDiaIse = dataFrame.iloc[i]['claddiai'],
                                        cladDiaOse = dataFrame.iloc[i]['claddiao'],
                                        cladOvoIse = dataFrame.iloc[i]['cladovi'],
                                        cladOvoOse = dataFrame.iloc[i]['cladovo'],
                                        eccIse = dataFrame.iloc[i]['ecci'],
                                        eccOse = dataFrame.iloc[i]['ecco'],
                                        coreOvoIse = dataFrame.iloc[i]['coreovi'],
                                        coreOvoOse = dataFrame.iloc[i]['coreovo'],
                                        coreDiaIse = dataFrame.iloc[i]['corediai'],
                                        coreDiaOse = dataFrame.iloc[i]['corediao']
                                )

                query_coating = Coating(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(), 
                                        common_id = rows+1,
                                        coat2Dia = dataFrame.iloc[i]['coat2o'],
                                        coat2Ovo = dataFrame.iloc[i]['coat2ovo'],
                                        coat2ECC = dataFrame.iloc[i]['coatecco'],
                                        coat1Dia = dataFrame.iloc[i]['coat1o'],
                                        coat1Ovo = dataFrame.iloc[i]['coat1ovo']
                                )

                query_chromatic = Chromatic(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                        common_id = rows+1,
                                        zwl = dataFrame.iloc[i]['dispzero'],
                                        slope = dataFrame.iloc[i]['dispslope'],
                                        disp1285  = dataFrame.iloc[i]['max1285'],
                                        disp1290  = dataFrame.iloc[i]['max1290'],
                                        disp1330  = dataFrame.iloc[i]['max1330'],
                                        disp1550  = dataFrame.iloc[i]['max1550']
                                )

                query_pmd = PMD(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                        common_id = rows+1,
                                        pmd = dataFrame.iloc[i]['pmd15']
                                )

                query_macro = MacroBending(spoolID = dataFrame.iloc[i]['spoolno'], create_date = datetime.now(),
                                        common_id = rows+1,
                                        R7_1550 = dataFrame.iloc[i]['coat2ovi'],           
                                        R7_1625 = dataFrame.iloc[i]['dmd_in'],           
                                        R10_1550 = dataFrame.iloc[i]['dmd_out'],           
                                        R10_1625 = dataFrame.iloc[i]['dmd_slide'],           
                                        R15_1550 = dataFrame.iloc[i]['r15mm_20turn_l1550'],           
                                        R15_1625 = dataFrame.iloc[i]['r15mm_20turn_l1625']           
                                )
    
                db.session.add(query_otdr)
                db.session.add(query_common)
                db.session.add(query_mfd)
                db.session.add(query_cutoff)
                db.session.add(query_geometry)
                db.session.add(query_coating)
                db.session.add(query_chromatic)
                db.session.add(query_pmd)
                db.session.add(query_macro)
                db.session.commit() 
        if os.path.exists(file_path):
            os.remove(file_path)

        return render_template('migration_result.html')