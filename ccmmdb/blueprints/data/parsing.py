import csv
import io
from builtins import any as b_any

import numpy
import pandas as pd
from flask import request, flash
import ccmmdb.utils.dbterms as dbterms
from ccmmdb.blueprints.data.forms import AdminFieldSelectionForm, SOLVENTCHOICES, ADDITIVECHOICES, VARIABLE_CHOICES

def form_to_dict():
    '''
    Strips out the None values, csrf_token, and submit response from the ImmutableMultiDict provided by werkzeug. Add
    any extra terms to be stripped out to b.
    '''
    d = request.form.to_dict()
    s = {}
    b = ('csrf_token', 'submit', 'log', 'imagej', 'ctan')
    for k, v in d.items():
        if v is not None and k not in b:
            s.update({k: v})
    return s

def solventparse(d):
    for i in range(0,SOLVENTCHOICES):
        if d['hyd_solvent-'+str(i)+'-solvent'] == 'A':
            d.update({'A' : True,
                      'A_conc' : d['hyd_solvent-' + str(i) + '-solvent_concentration'],
                      'A_prop' : d['hyd_solvent-' + str(i) + '-proportion']})
        elif d['hyd_solvent-'+str(i)+'-solvent'] == 'E':
            d.update({'E' : True,
            'E_conc' : d['hyd_solvent-' + str(i) + '-solvent_concentration'],
            'E_prop' : d['hyd_solvent-' + str(i) + '-proportion']})
        elif d['hyd_solvent-'+str(i)+'-solvent'] == 'H':
            d.update({'H' : True,
            'H_conc' : d['hyd_solvent-' + str(i) + '-solvent_concentration'],
            'H_prop' : d['hyd_solvent-' + str(i) + '-proportion']})
        elif d['hyd_solvent-'+str(i)+'-solvent'] == 'W':
            d.update({'W' : True,
            'W_prop' : d['hyd_solvent-' + str(i) + '-proportion']})
        del d['hyd_solvent-'+str(i)+'-solvent']
        del d['hyd_solvent-' + str(i) + '-solvent_concentration']
        del d['hyd_solvent-' + str(i) + '-proportion']
        del d['hyd_solvent-'+str(i)+'-csrf_token']

    for i in range(0, ADDITIVECHOICES):
        if d['additives-' + str(i) + '-additive'] == 'NaCl':
            d.update({'NaCl' : True, 'NaCl_conc' : d['additives-' + str(i) + '-additive_concentration']})
        elif d['additives-' + str(i) + '-additive'] == 'Suc':
            d.update({'Suc' : True, 'Suc_conc' : d['additives-' + str(i) + '-additive_concentration']})
        elif d['additives-' + str(i) + '-additive'] == 'El':
            d.update({'El' : True, 'El_conc' : d['additives-' + str(i) + '-additive_concentration']})
        elif d['additives-' + str(i) + '-additive'] == 'Hya':
            d.update({['Hya'] : True, 'Hya_conc' : d['additives-' + str(i) + '-additive_concentration']})
        del d['additives-' + str(i) + '-additive']
        del d['additives-' + str(i) + '-additive_concentration']
        del d['additives-' + str(i) + '-csrf_token']
    return d

def update_solvent_list(d):
    solvents = []
    for solvent in VARIABLE_CHOICES['hyd_solvent']:
        if solvent[0] in d.keys():
            if bool(getattr(d,solvent[0])) and str(getattr(d,solvent[0])) != str(numpy.nan):
                solvents.append(solvent[1])
    return str(solvents).strip('\', [, ]')

def update_additives_list(d):
    additives = []
    for additive in VARIABLE_CHOICES['additives']:
         if additive[0] in d.keys():
            if bool(getattr(d,additive[0])) and str(getattr(d,additive[0])) != str(numpy.nan):
                additives.append(additive[1])
    return str(additives).strip('\', [, ]')

def solvent_additive_update_dict(d):
    additives = []
    for additive in VARIABLE_CHOICES['additives']:
        if additive[0] in d.keys():
            if bool(d[additive[0]]):
                additives.append(additive[1])
    solvents = []
    for solvent in VARIABLE_CHOICES['hyd_solvent']:
        if solvent[0] in d.keys():
            if bool(d[solvent[0]]):
                solvents.append(solvent[1])
    d.update({'hyd_solvent': str(solvents)[1:-1], 'additives': str(additives)[1:-1]})
    return d

def solvent_additive_update_df(df):
    df['hyd_solvent'] = df.apply(update_solvent_list, axis = 1)
    df['additives'] = df.apply(update_additives_list, axis = 1)
    return df

def microct_log_parse(file, dictionary={}):
    '''
    A function that takes the log file submitted and parses out the data we , updating the any previous dictionary. Add
    desired terms to terms dictionary.

    :param file: Takes the log file generated through request.files['log']
    :param dictionary: The dictionary produced by form_to_dict and updates it with additional info
    :return: Dictionary to be submitted to the database.
    '''
    init_dict = {}
    terms = dbterms.microCT_terms
    f = file.readlines()
    for line in f:
        l = line.decode()
        if '=' in l and 'Hamming' not in l: #Hack to get round a log line with two '=' present and skip all other lines.
            k, v = l.strip().split('=')
            init_dict[k.strip()] = v.strip()
            for k, v in init_dict.items():
                if k in terms:
                    dictionary.update({terms[k]: v})
    return dictionary

def imagej_data(file, d={}):
    '''
    Function for pulling the data out of an imagej log, need to check that pandas reads it happily without saving it
    somewhere first. Needs some more work to pull all the data, and some input from Malavika on what's important/how to
    classify some of the data.

    :param file: Imagej log file
    :param d: Previously passed dictionary to update
    :return: Dictionary with added pore size data
    '''
    if 'pixel_size' in d:
        f = file.read()
        df = pd.read_csv(io.StringIO(f.decode('utf-8')), sep='\t', index_col=0)
        major_mean = str(numpy.mean(df['Major']) * float(d['pixel_size']))
        minor_mean = str(numpy.mean(df['Minor']) * float(d['pixel_size']))
        pore_size = str(numpy.mean([float(major_mean), float(minor_mean)]))
        d.update({'pore_size': pore_size, 'major_mean': major_mean, 'minor_mean': minor_mean})
    else:
        flash('ImageJ data must be accompanied by a micro-CT log.', 'danger')
    return d

def ctan_parse(file, dictionary={}):
    '''
    Reads in data from a ctan csv file, parses it line by line looking for terms in the dictionary. If found it then
    pulls the associated data and updates the dictionary.

    :param file: Takes the log file generated through request.files['ctan']
    :param dictionary: The dictionary produced by form_to_dict and updates it with additional info
    :return: Dictionary to be submitted to the database.
    '''
    init_dict = {}
    e = None
    terms = dbterms.CTan_terms
    f = file.read()
    cv = list(csv.reader(io.StringIO(f.decode('utf-8', 'ignore'))))
    if b_any('Mode : Shrink-wrap (3D space)' in row for row in cv):
        e = 'Please remove any Shrink-Wrap data from your CTan file.'
    else:
        for row in cv:
            for k in terms:
                if k in row and k == 'Structure separation':
                    if row[3] == 'mm':
                        init_dict[terms[k]] = str(float(row[2]) * 1000)
                    elif row[3] == 'um':
                        init_dict[terms[k]] = str(row[2])
                    else:
                        try:
                            init_dict[terms[k]] = str(row[2])*dictionary['pixelsize']
                        except KeyError:
                            e = 'CTan data has not been normalised, so must be accompanied by a micro-CT log'
                            flash('CTan data has not been normalised, so must be accompanied by a micro-CT log.', 'danger')
                            return e
                elif k in row and k == 'Percent object volume':
                    init_dict[terms[k]] = str(100 - float(row[2]))
                elif k in row and k == 'Degree of anisotropy':
                    init_dict[terms[k]] = str(row[2])
                elif k in row and k == 'Standard deviation of structure separation':
                    if row[3] == 'mm':
                        init_dict[terms[k]] = str(float(row[2]) * 1000)
                    elif row[3] == 'um':
                        init_dict[terms[k]] = str(row[2])
                    else:
                        try:
                            init_dict[terms[k]] = str(row[2])*dictionary['pixelsize']
                        except KeyError:
                            e = 'CTan data has not been normalised, so must be accompanied by a micro-CT log'
                            flash('CTan data has not been normalised, so must be accompanied by a micro-CT log.', 'danger')
                            return e
                elif k in row and k == 'Object surface':
                    if row[3] == 'mm^2':
                        init_dict[terms[k]] = str(float(row[2]) * 1000000)
                    elif row[3] == 'um^2':
                        init_dict[terms[k]] = str(row[2])
                    else:
                        try:
                            init_dict[terms[k]] = str(row[2])*dictionary['pixelsize']**2
                        except KeyError:
                            e = 'CTan data has not been normalised, so must be accompanied by a micro-CT log'
                            flash('CTan data has not been normalised, so must be accompanied by a micro-CT log.', 'danger')
                            return e
    dictionary.update(init_dict)
    return dictionary, e

def mechtest_upload(file, dictionary={}):
    def rename_cols(x):
        if 'stress' in x:
            return "stress"
        elif 'strain' in x:
            return 'strain'
        else:
            return x
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()
    if 'stress' and 'strain' not in df.columns:
        df = df.T.reset_index()
        df.columns = df.iloc[0]
        df = df.iloc[pd.RangeIndex(len(df)).drop(0)]
        df.columns = df.columns.str.strip().str.lower()
        if 'stress' and 'strain' not in df.columns:
            return {}, 'Stress and Strain are not labelled in either the rows or the columns!'
    df = df.rename(columns=rename_cols)
    dictionary['raw_stress'] = numpy.array2string(df['stress'].values.astype('float64'),separator=',')[1:-1]
    dictionary['raw_strain'] = numpy.array2string(df['strain'].values.astype('float64'),separator=',')[1:-1]
    return dictionary, None

def thermocouple_data(file, dictionary={}):
    def rename_cols(x):
        if 'time' in x:
            return "time"
        elif 'temp' in x:
            return 'temperature'
        else:
            return x

    df = pd.read_csv(file)
    df.columns = df.columns.str.strip().str.lower()
    if 'time' and 'temp' not in df.columns:
        df = df.T.reset_index()
        df.columns = df.iloc[0]
        df = df.iloc[pd.RangeIndex(len(df)).drop(0)]
        df.columns = df.columns.str.strip().str.lower()
        if 'time' and 'temp' not in df.columns:
            return {}, 'Time and Temperature are not labelled in either the rows or the columns!'
    df = df.rename(columns=rename_cols)
    dictionary['therm_time'] = numpy.array2string(df['time'].values.astype('float64'), separator=',')[1:-1]
    dictionary['therm_temperature'] = numpy.array2string(df['temperature'].values.astype('float64'), separator=',')[1:-1]
    return dictionary, None

def table_display_choices():
    form = AdminFieldSelectionForm()
    showlist = []
    if form.validate_on_submit() and request.method == 'POST':
        showlist = form.data['selectionfield']
    return form, showlist

def parse_to_readable(database_dict):
    '''
    Function that takes a database for submission to the database and switches the key names to human friendly values.

    :return: Dictionary containing descriptive keys and values for display
    '''
    terms = dbterms.total_db_terms
    results_dict = dict()
    for k, v in database_dict.items():
        if k in terms.keys():
            results_dict.update({terms[k]: v})
    return results_dict