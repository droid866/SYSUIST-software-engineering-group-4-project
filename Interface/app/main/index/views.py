from app import db
from app.models import User, Book, Comment, Log, Permission, Residents, Visitors, Temperature
from flask import render_template
from flask_login import current_user
from . import main
from ..people.forms import SearchForm
import datetime


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
    time = []
    now = datetime.datetime.now()
    yesterday = now + datetime.timedelta(-1)
    time1 = now + datetime.timedelta(-5/6.0)
    time2 = now + datetime.timedelta(-4/6.0)
    time3 = now + datetime.timedelta(-3/6.0)
    time4 = now + datetime.timedelta(-2/6.0)
    time5 = now + datetime.timedelta(-1/6.0)
    time.append(time1)
    time.append(time2)
    time.append(time3)
    time.append(time4)
    time.append(time5)
    time.append(now)
    log = []
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(yesterday, time1)).all())
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(time1, time2)).all())
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(time2, time3)).all())
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(time3, time4)).all())
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(time4, time5)).all())
    log.append(Temperature.query.filter(Temperature.record_timestamp.between(time5, now)).all())
    count = []
    count2 = []
    for i in log:
        count.append(len(i))
        count3 = 0
        for j in i:
            if j.temperature > 37.3:
                count3 = count3 + 1
        count2.append(count3)
    return render_template("index.html", time=time, log=log, count=count, count2=count2, search_form=search_form, residents=residents, visitors=visitors)
