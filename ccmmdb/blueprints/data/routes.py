from flask_login import login_required, current_user
import os
from datetime import datetime
from flask import redirect, url_for, render_template, current_app, abort, jsonify, send_file
from ccmmdb.blueprints.data import bp
from ccmmdb.core.db import db
from ccmmdb.core.app import csrf
from ccmmdb.utils.dbterms import total_db_terms
from ccmmdb.blueprints.data.parsing import *
from ccmmdb.models.models import User, Results
from ccmmdb.blueprints.data.forms import DataForm, allowed_file, VARIABLE_CHOICES, NUMERICAL_VARIABLES
from ccmmdb.blueprints.data.tables import DatabaseTable

def dataerror(errors, e):
    flash('An error has occurred', 'danger')
    errors.append('Unable to add items to database. Error: ' + str(e))
    return errors

def verify(d):
    errors = {}
    d = d.astype('str')
    newVARIABLECHOICES = VARIABLE_CHOICES.copy()
    if 'hyd_solvent' in newVARIABLECHOICES:
        del newVARIABLECHOICES['hyd_solvent']
    if 'additives' in newVARIABLECHOICES:
        del newVARIABLECHOICES['additives']
    for key in newVARIABLECHOICES:
        allowed_vals = [i[0].lower() for i in newVARIABLECHOICES[key]]
        allowed_vals.append(str(numpy.nan))
        if key in d.keys():
            mask = d[~d[key].str.casefold().isin(allowed_vals)]
            mask = pd.unique(mask[key])
            if len(mask):
                errors[key] = str(mask).strip('\',[,]') + ' not in the allowed options, please check your spelling for typos and trailing spaces!'
    return errors

@bp.route('/index', methods=['GET', 'POST'])
@login_required
def data():
    form = DataForm()
    user = current_user.crsid
    errors = []
    if form.validate_on_submit() and request.method == 'POST':
        try:
            d = form_to_dict()
            if d:
                d = solventparse(d)
                d = solvent_additive_update_dict(d)
                for key in request.files:
                    if key == 'log' and allowed_file(request.files[key].filename):
                        d = microct_log_parse(request.files['log'], d)
                    elif key == 'imagej' and allowed_file(request.files[key].filename):
                        d = imagej_data(request.files['imagej'], d)
                    elif key == 'ctan' and allowed_file(request.files[key].filename):
                        d, e = ctan_parse(request.files['ctan'], d)
                    elif key == 'mechtest' and allowed_file(request.files[key].filename):
                        d,e = mechtest_upload(request.files['mechtest'], d)
                    elif key == 'thermocouple_data' and allowed_file(request.files[key].filename):
                        d,e = thermocouple_data(request.files['thermocouple'], d)
                d['deleted'] = False
                d['user_id'] = user
                user = User.query.filter_by(crsid=current_user.id).first()
                results = Results(**d, researcher=user)
                db.session.add(results)
                db.session.commit()
                flash('Successfully submitted data!', 'success')
        except Exception as e:
            errors = dataerror(errors, e)
            errors = jsonify(errors)
            flash('Issue in submitting data!', 'danger')
    return render_template('data/data.html', form=form, user=user, errors=errors, discreteparameterspace = VARIABLE_CHOICES,
                           numericalparameterspace = NUMERICAL_VARIABLES, invertnames = total_db_terms)


@bp.route('/data_upload', methods=['POST'])
@login_required
def data_upload():
    form = DataForm()
    e = None
    if form.validate_on_submit():
        d = form_to_dict()
        d = solventparse(d)
        d = solvent_additive_update_dict(d)
        for key in request.files:
            if key == 'log' and allowed_file(request.files[key].filename):
                d = microct_log_parse(request.files['log'], d)
            elif key == 'imagej' and allowed_file(request.files[key].filename):
                d = imagej_data(request.files['imagej'], d)
            elif key == 'ctan' and allowed_file(request.files[key].filename):
                d, e = ctan_parse(request.files['ctan'], d)
                if e:
                    form.ctan.errors.append(e)
            elif key == 'mechtest' and allowed_file(request.files[key].filename):
                d,e = mechtest_upload(request.files['mechtest'], d)
                if e:
                    form.mechtest.errors.append(e)
            elif key == 'thermocouple' and allowed_file(request.files[key].filename):
                d,e = thermocouple_data(request.files['thermocouple'], d)
                if e:
                    form.thermocouple.errors.append(e)
        if form.errors:
            return jsonify(form.errors)
        d = parse_to_readable(d)
        return jsonify(d)
    else:
        return jsonify(form.errors)

@bp.route('/batch_csv_upload', methods=['POST'])
@login_required
def batch_csv_upload():
    form = DataForm()
    errors = {}
    if form.validate_on_submit():
        try:
            d = {}
            logmessage = 'None'
            df = pd.read_csv(request.files['csv'], header = 0)
            excludedvalues = set(df.keys()) - (set(total_db_terms.keys()))
            if not set(df.keys()).issubset(set(total_db_terms.keys())):
                errors['KeyError'] = 'The parameter codes: ' + str(excludedvalues)+  ' do not exist in our database, please check the spelling, or remove extra columns if necessary\n'
            df = df.loc[:,df.columns.isin(total_db_terms.keys())]
            if 'id' in df.columns:
                df.drop(['id'], axis=1, inplace=True)
            errors.update(verify(df))
            if not len(errors):
                if request.files['log']:
                    d = microct_log_parse(request.files['log'], d)
                    for uCTterm in dbterms.inverted_microCT_terms.keys():
                        df.loc[:, uCTterm] = d[uCTterm]
                    logmessage = 'Any microCT acquisition information from the CSV file has been overwritten by the log file.'
                df = solvent_additive_update_df(df)
                user = str(current_user.crsid)
                df.loc[:, 'user_id'] = user
                df.loc[:, 'created'] = datetime.utcnow()
                df.loc[:, 'deleted'] = 0
                df.to_sql('results', db.engine, if_exists='append', index=False)
                db.session.commit()
                flash('Successfully submitted data!', 'success')
                return jsonify({'CSV Upload Status': 'Batch upload successful!', 'microCT Status': logmessage})
            else:
                return jsonify({'CSV Upload Status': 'Batch upload unsuccessful, Error Messages: \n' + str(errors)[1:-1]} )
        except Exception as e:
            return jsonify({'CSV Upload Status': 'Batch upload unsuccessful, Error Messages: \n ' + str(e)})

@bp.route('/batch_json_upload', methods=['POST'])
@login_required
def batch_json_upload():
    form = DataForm()
    errors = {}
    if form.validate_on_submit():
        try:
            d = {}
            logmessage = 'None'
            df = pd.read_json(request.files['json'])
            if 'id' in df.columns:
                df.drop(['id'], axis=1, inplace=True)
            excludedvalues = set(df.keys()) - (set(total_db_terms.keys()))
            if not set(df.keys()).issubset(set(total_db_terms.keys())):
                errors['KeyError'] = 'The parameter codes: ' + str(
                    excludedvalues) + ' do not exist in our database, please check the spelling, or remove extra columns if necessary\n'
            df = df.loc[:, df.columns.isin(total_db_terms.keys())]
            if 'id' in df.columns:
                df.drop(['id'], axis=1, inplace=True)
            errors.update(verify(df))
            if not len(errors):
                if request.files['log']:
                    d = microct_log_parse(request.files['log'], d)
                    for uCTterm in dbterms.inverted_microCT_terms.keys():
                        df.loc[:, uCTterm] = d[uCTterm]
                    logmessage = 'Any microCT acquisition information from the CSV file has been overwritten by the log file.'
                df = solvent_additive_update_df(df)
                user = str(current_user.crsid)
                df.loc[:, 'user_id'] = user
                df.loc[:, 'created'] = datetime.utcnow()
                df.loc[:, 'deleted'] = 0
                df.to_sql('results', db.engine, if_exists='append', index=False)
                db.session.commit()
                flash('Successfully submitted data!', 'success')
                return jsonify({'JSON Upload Status': 'Batch upload successful!', 'microCT Status': logmessage})
            else:
                return jsonify({'CSV Upload Status': 'Batch upload unsuccessful, Error Messages: \n' + str(errors)[1:-1]})
        except Exception as e:
            return jsonify({'JSON Status': 'Batch upload unsuccessful, Error Message: \n ' + str(e)})


@bp.route('/admin', methods=['GET','POST'])
@login_required
def admin_page():
    crsid = str(current_user.crsid)
    with current_app.app_context():
        if crsid in current_app.config['ADMIN_MEMBERS']:
            data = Results.query.filter_by(deleted=False)
        elif crsid in current_app.config['CCMM_MEMBERS']:
            data = Results.query.filter_by(user_id=crsid, deleted=False)
        else:
            abort(403)
    form, showlist = table_display_choices()
    table = DatabaseTable(data, classes=['table, table-hover'], table_id='admin_table', html_attrs={'style': 'width:100%'})
    for i in showlist:
        setattr(getattr(table,i),'show',True)
    return render_template('data/admin.html', table=table, form = form)

@bp.route('/admin/<data>/delete', methods=['POST'])
@csrf.exempt #Have temporarily disabled csrf protection to allow for deleting. Need to come up with a more permanent fix.
@login_required
def delete_post(data):
    entry = Results.query.filter_by(id=data).first()
    user = str(current_user.crsid)

    if not entry:
        abort(404)
    with current_app.app_context():
        if entry.user_id != user and user not in current_app.config['ADMIN_MEMBERS']:
            abort(403)

    entry.deleted = True
    db.session.merge(entry)
    db.session.commit()

    return redirect(url_for('data.admin_page'))


@bp.route('/admin/data_download_csv', methods=['GET'])
@login_required
def data_download_csv():
    crsid = str(current_user.crsid)
    with current_app.app_context():
        if crsid in current_app.config['ADMIN_MEMBERS']:
            df = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            prefix = 'total-db'
        elif crsid in current_app.config['CCMM_MEMBERS']:
            df = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            df = df[df.user_id.isin([crsid])]
            prefix = crsid
        else:
            abort(403)
    path = os.path.join(current_app.root_path, 'generatedfiles')
    df.to_csv(os.path.join(path, prefix + '-data.csv'), index=False)
    return send_file(os.path.join(path, prefix + '-data.csv'), as_attachment=True)


@bp.route('/admin/data_download_json', methods=['GET'])
@login_required
def data_download_json():
    crsid = str(current_user.crsid)
    with current_app.app_context():
        if crsid in current_app.config['ADMIN_MEMBERS']:
            df = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            prefix = 'total-db'
        elif crsid in current_app.config['CCMM_MEMBERS']:
            df = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            df = df[df.user_id.isin([crsid])]
            prefix = crsid
        else:
            abort(403)
    path = os.path.join(current_app.root_path, 'generatedfiles')
    df.to_json(os.path.join(path, prefix + '-data.json'), orient='records')
    return send_file(os.path.join(path, prefix + '-data.json'), as_attachment=True)


@bp.route('/admin/example_download_csv', methods=['GET'])
@login_required
def example_download_csv():
    crsid = str(current_user.crsid)
    with current_app.app_context():
        if crsid in current_app.config['ADMIN_MEMBERS'] or crsid in current_app.config['CCMM_MEMBERS']:
            example = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            df = pd.DataFrame(columns=example.columns.values)
        else:
            abort(403)
    path = os.path.join(current_app.root_path, 'generatedfiles')
    df.to_csv(os.path.join(path, 'example-data.csv'), index=False)
    return send_file(os.path.join(path, 'example-data.csv'), as_attachment=True)


@bp.route('/admin/example_download_json', methods=['GET'])
@login_required
def example_download_json():
    crsid = str(current_user.crsid)
    with current_app.app_context():
        if crsid in current_app.config['ADMIN_MEMBERS'] or crsid in current_app.config['CCMM_MEMBERS']:
            example = pd.read_sql('SELECT * FROM results WHERE deleted= 0', db.engine)
            df = pd.DataFrame(columns=example.columns.values)
        else:
            abort(403)
    path = os.path.join(current_app.root_path, 'generatedfiles')
    df.to_json(os.path.join(path, 'example-data.json'), orient='records')
    return send_file(os.path.join(path, 'example-data.json'), as_attachment=True)