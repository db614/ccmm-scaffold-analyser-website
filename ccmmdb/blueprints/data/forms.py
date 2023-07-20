from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import widgets, SelectField, SelectMultipleField, SubmitField, FileField, DecimalField, TextAreaField, FieldList, FormField
from wtforms.validators import Optional, NumberRange
from ccmmdb.utils.dbterms import total_db_terms


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


VARIABLE_CHOICES = {
    'construct_type': [('None', 'None or N/A'),('2Dc', '2D-Cast'), ('2D-e', '2D-Electrophoretic Deposition'), ('3D', '3D scaffold')],
    'species': [('None', 'None or N/A'),('Bov', 'Bovine'), ('Ov', 'Ovine'), ('Por', 'Porcine'), ('Mur', 'Murine'), ('Rat', 'Rat'), ('Hum', 'Human')],
    'solubility': [('None', 'None or N/A'),('Insol', 'Insoluble'), ('Sol', 'Soluble'), ('Neu', "Neutralised")],
    'source': [('None', 'None or N/A'),('D', 'Dermal'), ('T', 'Tendon'), ('X', 'Tail')],
    'hyd_solvent': [('None', 'None or N/A'), ('A', 'Acetic Acid'), ('H', 'Hydrochloric Acid'), ('E', 'Ethanol'), ('W', 'Water')],
    'additives': [('None', 'None'),('NaCl', 'Sodium chloride'), ('Suc', 'Sucrose'), ('El', 'Elastin'), ('Hya', 'Hyaluronic Acid')],
    'dialysis': [('None', 'None'), ('P', 'Powder'), ('S', 'Slurry')],
    'blending': [('None', 'None or N/A'), ('1', 'Total of 2 minutes at 22000 rpm'), ('2', 'Total of 2 minutes at (18000 + 22000) rpm'),
                      ('3', 'Total of 4 minutes at 22000 rpm'), ('4', 'Total of 4 minutes at (18000 + 22000) rpm'), ('5', 'Total of 6 minutes at 20000 rpm')],
    'mould_type': [('None', 'None or N/A'), ('PCC', 'Polycarbonate, copper base'), ('PCS', 'Polycarbonate, steel base'),
                        ('Si', 'Silicone mould'), ('SS', 'Stainless steel'), ('T6', '6 well plate'),
                        ('T24', '24 well plate'), ('T48', '48 well plate'), ('T96', '96 well plate'),('X', 'Composite or Other')],
    'crosslink': [('NonXL', 'Non-crosslinked'), ('EDC-NHS', 'EDC-NHS'), ('Gen', 'Genipin'),
                       ('TG2', 'Transglutaminase'), ('UV', 'UV crosslinking')],
    'mech_loading': [('None', 'None or N/A'),('Ten', 'Tensile'),('Com','Compressive'),('Probe', 'QNM/Nanoindentation')],
    'mech_hydration': [('None', 'None or N/A'),('Dry', 'Dry'),('Wet','Wet')],
    'freeze_drier': [('None', 'None or N/A'), ('Gloria', 'Gloria'), ('Clive', 'Clive'), ('Elton', 'Elton'), ('Other', 'Other')]}
NUMERICAL_VARIABLES = ['conc','mould_area', 'freezing_temp','cool_rate', 'nucleation_temp','time_at_eq','drying_temp', 'drying_pressure',
                       'crosslink_conc', 'crosslink_degree', 'pore_size','major_mean', 'minor_mean','median_interconnection_diameter', 'perc_diameter', 'anisotropy', 'field_strength',
                       'pulse_width', 'duty_cycle', 'mech_temp', 'mech_alignment',
                       'modulus', 'failurestress', 'failurestrain', 'publication_field','otherinfo']
ALLOWED_EXTENSIONS = {'log', 'txt', 'csv', 'json'}

CONDITION_LIST = list(total_db_terms.items())

SOLVENTCHOICES = 2
ADDITIVECHOICES = 2


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AdminFieldSelectionForm(FlaskForm):
    # Need to add proper validators for each of these selectors.
    selectionfield = SelectMultipleField(u'Select the fields you would like to see in the table. Press down Ctrl to select multiple fields', choices=CONDITION_LIST,
                       validators=[Optional()])
    submit = SubmitField('Submit')

class AdditiveForm(FlaskForm):
    additive = SelectField(u'Additives to slurry', choices=VARIABLE_CHOICES['additives'],
                                   validators=[Optional()])
    additive_concentration = DecimalField(u'Concentration (w/v%)', validators=[Optional(), NumberRange(min=0,
                                                                                                         message='Concentration must be more than 0')],)

class SolventForm(FlaskForm):
    solvent = SelectField(u'Hydration solvent', choices=VARIABLE_CHOICES['hyd_solvent'],
                                   validators=[Optional()])
    proportion = DecimalField(u'Proportion of solvent(%)', validators=[Optional(), NumberRange(min=0, max =0,
                                                                                                         message='Proportion must be between 0 and 100%')],)
    solvent_concentration = DecimalField(u'Concentration (M)', validators=[Optional(), NumberRange(min=0,
                                                                                                         message='Concentration must be more than 0')],)

class DataForm(FlaskForm):
    # Need to add proper validators for each of these selectors.
    construct_type = SelectField(u'Construct Type', choices=VARIABLE_CHOICES['construct_type'],
                                 validators=[Optional()],
                                 default='B')
    species = SelectField(u'Species', choices=VARIABLE_CHOICES['species'], validators=[Optional()],
                               default='B')
    solubility = SelectField(u'Solubility', choices=VARIABLE_CHOICES['solubility'],
                                  validators=[Optional()], default='I')
    source = SelectField(u'Source', choices=VARIABLE_CHOICES['source'], validators=[Optional()],
                              default='D')
    conc = DecimalField(u'Collagen concentration (wt. %)',
                             validators=[Optional(), NumberRange(min=0, message='Please check your input')], default=1)
    additives = FieldList(FormField(AdditiveForm), min_entries=ADDITIVECHOICES)
    hyd_solvent = FieldList(FormField(SolventForm), min_entries=SOLVENTCHOICES)
    dialysis = SelectField(u'Dialysis method', choices=VARIABLE_CHOICES['dialysis'],
                                validators=[Optional()], default='None')
    blending = SelectField(u'Blending method', choices=VARIABLE_CHOICES['blending'],
                                validators=[Optional()], default='')
    mould_type = SelectField(u'Mould type', choices=VARIABLE_CHOICES['mould_type'],
                                  validators=[Optional()], default='')
    mould_area = DecimalField(u'Mould filling area (cm\xb2)', validators=[Optional(), NumberRange(min=0,
                                                                                                       message='Please check your input; Mould filling area must be greater than 0')])
    mould_fillheight = DecimalField(u'Mould filling height (mm)', validators=[Optional(), NumberRange(min=0,
                                                                                                           message='Please check your input; Mould filling height must be greater than 0')])
    freezing_temp = DecimalField(u'Freezing temperature \xb0C', validators=[Optional(), NumberRange(min=-200, max=0,
                                                                                                    message='Please check your input; Please put -196 for a liquid nitrogen quench')],
                                 default=-30)
    cool_rate = DecimalField(u'Cooling rate (\xb0C/min)', validators=[Optional()])
    nucleation_temp = DecimalField(u'Nucleation temperature (\xb0C)', validators=[Optional()])
    time_at_eq = DecimalField(u'Time at equilibrium (s)', validators=[Optional()])
    drying_temp = DecimalField(u'Drying temperature (\xb0C)', validators=[Optional(), NumberRange(min=0,
                                                                                                       message='Pressure cannot be negative, pleease check your input')],
                                    default=0)
    drying_pressure = DecimalField(u'Drying pressure (mTorr)', validators=[Optional(), NumberRange(min=0,
                                                                                                        message='Pressure cannot be negative, please check your input')],
                                        default=80)

    crosslink = SelectField(u'Crosslinker', choices=VARIABLE_CHOICES['crosslink'],
                                 validators=[Optional()], default='EDC-NHS')
    crosslink_conc = DecimalField(u'Crosslinking Concentration (%)', validators=[Optional(), NumberRange(min=0,
                                                                                                              message='Crosslinking concentration cannot be negative. If zero, please put non-crosslinked in the input above')],
                                       default=100)
    crosslink_degree = DecimalField(u'Degree of Crosslinking (%)', validators=[Optional(), NumberRange(min=0,
                                                                                                         message='Degree of crosslinking must be between 0 and 100%')],)
    freeze_drier = SelectField(u'Freeze drier', choices=VARIABLE_CHOICES['freeze_drier'], validators=[Optional()],
                               default='')
    pore_size = DecimalField(u'Pore size (for CTan, or average of min and max if ImageJ) (\u03BCm)',
                                                   validators=[Optional(), NumberRange(min=0,
                                                                                       message='Pore size cannot be negative')])
    major_mean = DecimalField(u'Major Axis pore size (for elliptical 2D pore size) (\u03BCm)',
                             validators=[Optional(), NumberRange(min=0,
                                                                 message='Major axis cannot be negative')])
    minor_mean = DecimalField(u'Major Axis pore size (for elliptical 2D pore size) (\u03BCm)',
                              validators=[Optional(), NumberRange(min=0,
                                                                  message='Minor axis cannot be negative')])
    median_interconnection_diameter = DecimalField(u'Median Interconnection Diameter (\u03BCm)',
                                                   validators=[Optional(), NumberRange(min=0,
                                                                                       message='Median interconnection diameter cannot be negative')])
    perc_diameter = DecimalField(u'Percolation Diameter (\u03BCm)', validators=[Optional(), NumberRange(min=0,
                                                                                                   message='Percolation diameter cannot be negative')])
    anisotropy = DecimalField(u'Degree of anisotropy', validators=[Optional(), NumberRange(min=0, max = 1,
                                                                                                    message='Degree of anisotropy must be between 0 and 1')])
    field_strength = DecimalField(u'Deposition Field Strength (V/cm)', validators=[Optional(), NumberRange(min=0, message='Field strength must be a positive value')])
    pulse_width = DecimalField(u'Pulse Width (ms)', validators=[Optional(), NumberRange(min=0, message='Pulse width must be a positive value')])
    duty_cycle = DecimalField(u'Duty Cycle (%)', validators=[Optional(), NumberRange(min=0, max = 100, message='Duty cycle must be between 0 and 100')])


    mech_loading = SelectField(u'Mechanical Loading Type', choices=VARIABLE_CHOICES['mech_loading'], validators=[Optional()], default = '')
    mech_hydration = SelectField(u'Mechanical Testing Hydration State', choices=VARIABLE_CHOICES['mech_hydration'], validators=[Optional()], default = '')
    mech_temp  = DecimalField(u'Mechanical Testing Temperature (\xb0C)', validators=[Optional(), NumberRange(min=0,
                                                               message='Modulus cannot be negative')])
    mech_alignment = DecimalField(u'Angle of Mechanical Loading (as measured from collagen fibre alignment) (\xb0)', validators=[Optional(), NumberRange(min=0, max = 90,
                                                               message=u'Alignment must be between 0\xb0 and 90\xb0')])
    modulus = DecimalField(u'Modulus (Pa)', validators=[Optional(), NumberRange(min=0,
                                                               message='Modulus cannot be negative')])
    failurestress = DecimalField(u'Failure Strength (Pa)', validators=[Optional(), NumberRange(min=0,
                                                                                                 message='Failure strength cannot be negative')])
    failurestrain = DecimalField(u'Failure Strain', validators=[Optional(), NumberRange(min=0,
                                                                                        message='Failure strain cannot be negative')])
    publication_field = TextAreaField(u'Associated Publications (DOI preferred)', validators=[Optional()], default='')

    otherinfo = TextAreaField(u'Other information, e.g.', validators=[Optional()], default='')
    log = FileField(u' MicroCT Acquisition log file', validators=[Optional(), FileAllowed(['log'], '.log file only!')])
    imagej = FileField(u'ImageJ Structural Analysis files',
                       validators=[Optional(), FileAllowed(['txt', 'csv'], '.txt or .csv file only!')])
    ctan = FileField(u'CTAnalyser Structural Analysis [ctan/batman.txt, not .log] files.',
                     validators=[Optional(), FileAllowed(['txt', 'csv'], '.txt or .csv file only!')])
    mechtest = FileField(
        u'Raw Mechanical testing data, please only give two columns (stress in Pa and strain) as a csv file.',
        validators=[Optional(), FileAllowed(['csv'], '.csv file only!')])
    thermocouple = FileField(
        u'Thermocouple data during freeze-drying, please only give two columns (time in s and temperature in \xb0C) as a csv file.',
        validators=[Optional(), FileAllowed(['csv'], '.csv file only!')])
    csv = FileField(u'Import CSV file with Structural Analysis',
                    validators=[Optional(), FileAllowed(['csv'], '.csv file only!')])
    json = FileField(u'Import JSON file with Structural Analysis',
                     validators=[Optional(), FileAllowed(['json'], '.json file only!')])
    submit = SubmitField('Submit')