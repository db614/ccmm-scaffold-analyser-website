from flask import render_template, redirect
from flask_login import login_required

from ccmmdb.blueprints.main import bp


@bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('main/index.html')

@bp.route('/privacy')
def privacy_page():
    return render_template('main/privacy.html')

@bp.route('/logout')
def logout():
    return render_template('main/logout.html')

@bp.route('/graphapp')
@login_required
def graph_app():
    return redirect('/graphapp/')

@bp.route('/predictapp')
@login_required
def predict_app():
    return redirect('/predictapp/')
