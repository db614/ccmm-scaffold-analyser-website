from ccmmdb.core.db import db
from datetime import datetime
from flask_login import UserMixin
# TODO: Check that this is a sensible way to deal with setting up the database.

class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True)
    crsid = db.Column(db.String(32), index=True)
    results = db.relationship('Results', backref='researcher', lazy='dynamic')


class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    construct_type = db.Column(db.String(32))
    species = db.Column(db.String(32))
    solubility = db.Column(db.String(32))
    source = db.Column(db.String(32))
    conc = db.Column(db.String(32))
    additives = db.Column(db.String(32))
    hyd_solvent = db.Column(db.String(32))
    A = db.Column(db.String(32))
    A_conc = db.Column(db.String(32))
    A_prop = db.Column(db.String(32))
    H = db.Column(db.String(32))
    H_conc = db.Column(db.String(32))
    H_prop = db.Column(db.String(32))
    E = db.Column(db.String(32))
    E_conc = db.Column(db.String(32))
    E_prop = db.Column(db.String(32))
    W = db.Column(db.String(32))
    W_prop = db.Column(db.String(32))
    NaCl = db.Column(db.String(32))
    NaCl_conc = db.Column(db.String(32))
    Suc = db.Column(db.String(32))
    Suc_conc = db.Column(db.String(32))
    El = db.Column(db.String(32))
    El_conc = db.Column(db.String(32))
    Hya = db.Column(db.String(32))
    Hya_conc = db.Column(db.String(32))
    dialysis = db.Column(db.String(32))
    blending = db.Column(db.String(32))
    mould_type = db.Column(db.String(32))
    mould_area = db.Column(db.String(32))
    mould_fillheight = db.Column(db.String(32))
    freezing_temp = db.Column(db.String(32))
    nucleation_temp = db.Column(db.String(32))
    time_at_eq = db.Column(db.String(32))
    cool_rate = db.Column(db.String(32))
    drying_temp = db.Column(db.String(32))
    drying_pressure = db.Column(db.String(32))
    crosslink = db.Column(db.String(32))
    crosslink_conc = db.Column(db.String(32))
    crosslink_degree = db.Column(db.String(32))
    mech_alignment = db.Column(db.String(32))
    field_strength = db.Column(db.String(32))
    pulse_width = db.Column(db.String(32))
    duty_cycle = db.Column(db.String(32))
    publication_field = db.Column(db.String(32))
    mech_loading = db.Column(db.String(32))
    mech_hydration = db.Column(db.String(32))
    mech_temp = db.Column(db.String(32))
    raw_stress = db.Column(db.String(32))
    raw_strain = db.Column(db.String(32))
    therm_time = db.Column(db.String(32))
    therm_temperature = db.Column(db.String(32))
    modulus = db.Column(db.String(32))
    failurestrain = db.Column(db.String(32))
    failurestress = db.Column(db.String(32))
    freeze_drier = db.Column(db.String(32))  # Name of the freeze drier used
    porosity = db.Column(db.String(32))  # Percentage
    pore_size = db.Column(db.String(32))  # In um
    perc_diameter = db.Column(db.String(32))  # In um
    median_interconnection_diameter = db.Column(db.String(32))  # In um
    pore_sd = db.Column(db.String(32))  # SD of the pore size for a single sample in um
    anisotropy = db.Column(db.String(32))  # Degree of anisotropy
    internal_sa = db.Column(db.String(32))  # Total internal surface area in mm2
    pixel_size = db.Column(db.String(32))  # In um
    source_current = db.Column(db.String(32))  # In uA
    source_voltage = db.Column(db.String(32))  # In kV
    number_rows = db.Column(db.String(32))  # Determining camera size
    number_cols = db.Column(db.String(32))  # Determining camera size
    exposure_time = db.Column(db.String(32))  # In ms
    rotation_step = db.Column(db.String(32))  # In deg
    frame_average = db.Column(db.String(32))  # Frame averaging on/off
    major_mean = db.Column(db.String(32))  # ImageJ major axis mean
    minor_mean = db.Column(db.String(32))  # ImageJ minor axis mean
    user_id = db.Column(db.String(32), db.ForeignKey('user.crsid'))
    otherinfo = db.Column(db.String(32))
    deleted = db.Column(db.Boolean())  # Whether the data has been deleted by a user
