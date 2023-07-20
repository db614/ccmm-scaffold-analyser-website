total_db_terms = {}
inverted_db_terms = {}
microCT_terms = {'Image Pixel Size (um)': 'pixel_size', 'Source Current (uA)': 'source_current',
                 'Source Voltage (kV)': 'source_voltage', 'Number of Rows': 'number_rows',
                 'Number of Columns': 'number_cols', 'Exposure (ms)': 'exposure_time',
                 'Rotation Step (deg)': 'rotation_step', 'Frame Averaging': 'frame_average'}
ImageJ_terms = {'Major Axis':'major_mean', 'Minor Axis': 'minor_mean'}
CTan_terms = {'Object surface': 'internal_sa', 'Structure separation': 'pore_size',
              'Standard deviation of structure separation': 'pore_sd', 'Percent object volume': 'porosity', 'Degree of anisotropy':'anisotropy',}
form_input_terms = {'construct_type': 'Construct Type', 'species': 'Collagen Species',
                    'solubility': 'Collagen Solubility',
                    'source': 'Collagen Source',
                    'conc': 'Collagen Concentration (%)', 'A' : 'Acetic Acid (0 for False, 1 for True)', 'A_conc': 'Acetic Acid Concentration (M)', 'A_prop' : 'Proportion of Acetic Acid (%)',
                    'H' : 'Hydrochloric Acid (0 for False, 1 for True)', 'H_conc': 'Hydrochloric Acid Concentration (M)', 'H_prop' : 'Proportion of Hydrochloric Acid (%)',
                    'E' : 'Ethanol (0 for False, 1 for True)', 'E_conc': 'Ethanol Concentration (M)', 'E_prop' : 'Proportion of Ethanol (%)',
                    'W' : 'Water (0 for False, 1 for True)', 'W_prop' : 'Proportion of Water (%)',
                    'NaCl' : 'Sodium chloride (0 for False, 1 for True)', 'NaCl_conc' : 'Sodium chloride concentration (w/v%)',
                    'Suc': 'Sucrose (0 for False, 1 for True)', 'Suc_conc': 'Sucrose concentration (w/v%)',
                    'El': 'Elastin (0 for False, 1 for True)', 'El_conc': 'Elastin concentration (w/v%)',
                    'Hya': 'Hyaluronic Acid (0 for False, 1 for True)', 'Hya_conc': 'Hyaluronic Acid concentration (w/v%)',
                    'additives': 'Additives', 'hyd_solvent': 'Collagen Hydration Solvent',
                    'dialysis': 'Collagen Dialysis', 'blending': 'Collagen Blending',
                    'mould_type': 'Mould Type',
                    'mould_area': 'Mould Area (mm\u00B2)', 'mould_fillheight': 'Mould Fill height (mm)',
                    'freezing_temp': 'Collagen Freezing Temperature (\xb0C)',
                    'cool_rate': 'Collagen Cooling Rate (\xb0C/min)',
                    'nucleation_temp':'Nucleation Temperature (\xb0C)',
                    'time_at_eq' : 'Time at equilibrium (s)',
                    'drying_temp': 'Collagen Drying Temperature (\xb0C)',
                    'drying_pressure': 'Collagen Drying Pressure (mTorr)',
                    'crosslink': 'Crosslinker',
                    'crosslink_conc': 'Crosslinking Concentration (%)',
                    'crosslink_degree' : 'Degree of Crosslinking (%)',
                    'pore_size': 'Pore Size (\u03BCm)',
                    'perc_diameter': 'Percolation Diameter (\u03BCm)',
                    'median_interconnection_diameter': 'Median Interconnection Diameter (\u03BCm)',
                    'mech_loading': 'Mechanical Loading Type', 'mech_temp':'Mechanical Testing Temperature (\xb0C)',
                    'mech_hydration':'Hydration State at Mechanical Testing','modulus': 'Modulus (Pa)',
                    'mech_alignment': 'Angle of Mechanical Loading (as measured from collagen fibre alignment) (\xb0)',
                    'field_strength':'Deposition field strength (V/cm)',
                    'pulse_width':'Pulse Width (ms)',
                    'duty_cycle': 'Duty Cycle (%)',
                    'failurestress': 'Failure Strength (Pa)', 'failurestrain': 'Failure Strain',
                    'raw_stress':'Raw Stress (Pa)', 'raw_strain':'Raw Strain',
                    'therm_time':'Time (s)', 'therm_temperature':'Thermocouple Temperature (\xb0C)',
                    'freeze_drier': 'Freeze Drier', 'id': 'Entry ID', 'user_id': 'User ID', 'created': 'Created',
                    'deleted': 'Deleted', 'publication_field':'DOI of Associated Publications' ,'otherinfo': 'Other Information'}
extradashterms = {'porosity': 'Porosity (%)', 'pixel_size': 'Pixel Size (\u03BCm)', 'pore_size': 'Pore Size (\u03BCm)',
                  'pore_sd': 'Pore Size StDev', 'internal_sa': 'Internal Surface Area'}
inverted_microCT_terms = {v: k for k, v in microCT_terms.items()}
inverted_imageJ_terms = {v: k for k,v in ImageJ_terms.items()}
inverted_CTan_terms = {v: k for k, v in CTan_terms.items()}
inverted_form_terms = {v: k for k, v in form_input_terms.items()}
inverted_dash_terms = {v: k for k, v in extradashterms.items()}
total_db_terms.update(form_input_terms)
total_db_terms.update(inverted_CTan_terms)
total_db_terms.update(inverted_imageJ_terms)
total_db_terms.update(inverted_microCT_terms)
inverted_db_terms.update(inverted_form_terms)
inverted_db_terms.update(CTan_terms)
inverted_db_terms.update(ImageJ_terms)
inverted_db_terms.update(inverted_dash_terms)
inverted_db_terms.update(microCT_terms)