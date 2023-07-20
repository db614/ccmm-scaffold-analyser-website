from flask import Blueprint

bp = Blueprint('data', __name__, template_folder='templates', static_folder='static')

from . import forms, parsing, routes, tables

