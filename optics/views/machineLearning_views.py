from http.client import OK
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
import joblib
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('machineLearning', __name__, url_prefix='/machineLearning')

@bp.route('/ml')
@login_required
def go_ML():
    return render_template('machineLearning_intro.html')

@bp.route('/cutoff')
@login_required
def go_cutoff():
    return render_template('cutoff_intro.html')

@bp.route('/bending')
@login_required
def go_bending():
    return render_template('bending_intro.html')

@bp.route('/upload', methods = ["POST"])
@login_required
def upload():
    file = request.files['csv_name']
    #fileName = secure_filename(file.filename)
    fileName = secure_filename('test.csv')
    file.save(os.path.join('./upload', fileName))
    return redirect(url_for('machineLearning.migrate'))

@bp.route('/migration')
@login_required
def migrate():
    file_path = './upload/test.csv'

    try:
        df_test = pd.read_csv('./upload/test.csv', index_col=0)
        model = joblib.load('./optics/MLmodels/cutoff_tree.pkl')
        spoolID = df_test.index
        spoolID = spoolID.tolist()
        if model:
            y_pred = model.predict(df_test)
            y_pred = y_pred.tolist()
            if os.path.exists(file_path):
                os.remove(file_path)
                return render_template('cutoff_intro.html', spoolID=spoolID, y_pred=y_pred)
                #return 'OK...'
    except:
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'Can not make pandas data frame...'
#################################################################

@bp.route('/upload_bending', methods = ["POST"])
@login_required
def upload_bending():
    file = request.files['csv_name']
    #fileName = secure_filename(file.filename)
    fileName = secure_filename('test.csv')
    file.save(os.path.join('./upload', fileName))
    return redirect(url_for('machineLearning.migrate_bending'))

@bp.route('/migration_bending')
@login_required
def migrate_bending():
    file_path = './upload/test.csv'

    try:
        df_test = pd.read_csv('./upload/test.csv', index_col=0)
        model = joblib.load('./optics/MLmodels/bending_tree.pkl')
        spoolID = df_test.index
        spoolID = spoolID.tolist()
        if model:
            y_pred = model.predict(df_test)
            y_pred = y_pred.tolist()
            if os.path.exists(file_path):
                os.remove(file_path)
                return render_template('bending_intro.html', spoolID=spoolID, y_pred=y_pred)
                return 'OK...'
    except:
        if os.path.exists(file_path):
            os.remove(file_path)
        return 'Can not make pandas data frame...'
    
    # df_test = pd.read_csv('./upload/test.csv', index_col=0)
    # model = joblib.load('./optics/MLmodels/bending_tree.pkl')
    # spoolID = df_test.index
    # spoolID = spoolID.tolist()
    # if model:
    #     y_pred = model.predict(df_test)
    #     y_pred = y_pred.tolist()
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #         return 'OK...'