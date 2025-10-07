from flask import Blueprint

medical_records = Blueprint('medical_records', __name__, url_prefix='/medical-records')

from . import routes  # Import routes to register them with the blueprint