from app import db
from app.models import User, Book, Comment, Log, Permission, Residents, Visitors
from flask import render_template
from flask_login import current_user
from . import main
from ..people.forms import SearchForm


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.route('/')
def index():
    search_form = SearchForm()
    the_books = Book.query
    if not current_user.can(Permission.UPDATE_BOOK_INFORMATION):
        the_books = the_books.filter_by(hidden=0)
    residents = Residents.query
    visitors = Visitors.query
    return render_template("index.html", search_form=search_form, residents=residents, visitors=visitors)
