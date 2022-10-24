from flask import Blueprint, render_template, request, url_for, session, flash, g
import json
from flask.helpers import flash
from werkzeug.utils import redirect
from optics.models import Packing
from .auth_views import login_required
from optics import db
import pandas as pd

bp = Blueprint('packing', __name__, url_prefix='/packing')

@bp.route('/packing_update')
@login_required
def update():
    packing_list = []
    query_set = db.session.query(Packing.customerName, Packing.orderLength, Packing.packedLength, Packing.packedSpoolCount, Packing.stdLength)
    df = pd.read_sql_query(query_set.statement, query_set.session.bind)
    df['percent'] = df['packedLength'] / df['orderLength'] *100
    rows = df.shape[0]
    for row in range(0, rows):
        packing_list.append(df.iloc[row].to_list())
    return render_template('packing.html', packing_list=packing_list)