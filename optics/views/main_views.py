from flask import Blueprint, render_template, request, url_for, session, flash, g
import json
from flask.helpers import flash
from werkzeug.utils import redirect
from optics.models import User
from .auth_views import login_required
import random
import pandas as pd
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


bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def log_in():
    return render_template('log_in.html')

@bp.route('/login', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        error = None
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        user = User.query.filter_by(userEmail=request.form['inputEmail']).first()
        #print(user.userEmail)
        if not user:
            error = "등록되지 않은 사용자 입니다"
        elif not password:
            error = "패스워드를 입력하세요"
        elif password != 'lsuser':
            error = "패스워드가 정확하지 않습니다"
        if error is None:
            session['user_id'] = user.id
            return redirect(url_for('main.re_home'))
        flash(error)
    return render_template('log_in.html')

@bp.route('/home')
@login_required
def re_home():
    return render_template('home.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.rehome'))