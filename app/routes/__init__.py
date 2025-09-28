"""
Main routes for the Rafad Clinic System
"""
from flask import Blueprint, render_template

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route"""
    return render_template('index.html', title='Rafad Clinic System')


@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html', title='About Us')