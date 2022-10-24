from flask import Blueprint, render_template, request, url_for
from flask_sqlalchemy import model
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from sqlalchemy.orm import query
from sqlalchemy.orm.session import Session
from werkzeug.utils import redirect, secure_filename
from optics import db
from optics.models import User 
import os
import sqlite3
import numpy as np
from .auth_views import login_required
sqlite3.register_adapter(np.int64, lambda val: int(val))

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/registrate')
@login_required
def registrate():
    return render_template('user_registration.html')

@bp.route('/registration', methods=['POST'])
@login_required
def registration():
    if request.form['email']:
        query_user = User(create_date = datetime.now(),
                        userEmail = str(request.form['email'])
                )
        db.session.add(query_user)
        db.session.commit()
        
    return '사용자 등록 완료...'