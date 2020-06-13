from flask import Blueprint

book = Blueprint('book', __name__, url_prefix='/people',template_folder='templates')

from . import views
