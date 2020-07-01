from app import db
from app.models import Book, Log, Comment, Permission, Tag, book_tag, Residents, Visitors, Temperature, Face
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user
from . import book
from .forms import SearchForm, EditBookForm, AddBookForm, EditPeopleForm, AddPeopleForm
from ..comment.forms import CommentForm
from ..decorators import admin_required, permission_required


@book.route('/')
def people():
    search_word = request.args.get('search')
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)

    the_residents = Residents.query
    the_visitors = Visitors.query

    if search_word:
        search_word = search_word.strip()
        the_residents = the_residents.filter(db.or_(
            Residents.id_number.ilike(u"%%%s%%" % search_word), Residents.id_type.ilike(u"%%%s%%" % search_word), Residents.name.ilike(
                u"%%%s%%" % search_word), Residents.gender.ilike(u"%%%s%%" % search_word), Residents.address.ilike(u"%%%s%%" % search_word),
                Residents.phone_number.ilike(u"%%%s%%" % search_word)))
        the_visitors = the_visitors.filter(db.or_(
            Visitors.id_number.ilike(u"%%%s%%" % search_word), Visitors.id_type.ilike(u"%%%s%%" % search_word), Visitors.name.ilike(
                u"%%%s%%" % search_word), Visitors.gender.ilike(u"%%%s%%" % search_word), Visitors.address.ilike(u"%%%s%%" % search_word),
                Visitors.phone_number.ilike(u"%%%s%%" % search_word)))
        search_form.search.data = search_word
    else:
        the_residents = Residents.query.order_by(Residents.id_number.desc())
        the_visitors = Visitors.query.order_by(Visitors.id_number.desc())

    residents_pagination = the_residents.paginate(page, per_page=8)
    residents_result = residents_pagination.items

    visitors_pagination = the_visitors.paginate(page, per_page=8)
    visitors_result = visitors_pagination.items

    return render_template("people.html", residents=residents_result, visitors=visitors_result,
        visitors_pagination=visitors_pagination, residents_pagination=residents_pagination, search_form=search_form,
        title_resident=u"小区居民", title_visitor=u"外来人员")


@book.route('/<people_id>/<isresident>/')
def people_detail(people_id, isresident):
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if isresident == 'True':
        the_people = Residents.query.get_or_404(people_id)
        pagination = Temperature.query.filter(Temperature.id_number==people_id).order_by(Temperature.record_timestamp.desc()).paginate(page, per_page=10)
        pagination2 = Face.query.filter(Face.id_number==people_id).paginate(page, per_page=10)
    else:
        the_people = Visitors.query.get_or_404(people_id)
        pagination = Temperature.query.filter(Temperature.id_number==people_id).order_by(Temperature.record_timestamp.desc()).paginate(page, per_page=10)
        pagination2 = Face.query.filter(Face.id_number==people_id).paginate(page, per_page=10)

    logs = pagination.items
    face = pagination2.items

    return render_template("people_detail.html", people=the_people, face=face, logs=logs, form=form,
        isresident=isresident, title=the_people.name)


@book.route('/<people_id>/<isresident>/people_edit/', methods=['GET', 'POST'])
@permission_required(Permission.UPDATE_BOOK_INFORMATION)
def people_edit(people_id, isresident):
    if isresident == 'True':
        people = Residents.query.get_or_404(people_id)
        face = Face.query.filter(Face.resident_id==people_id).all()[0]
    else:
        people = Visitors.query.get_or_404(people_id)
        face = Face.query.filter(Face.visitors_id==people_id).all()[0]
    form = EditPeopleForm()
    if form.validate_on_submit():
        people.name = form.name.data
        people.id_type = form.id_type.data
        people.id_number = form.id_number.data
        people.gender = form.gender.data
        people.phone_number = form.phone_number.data
        people.address = form.address.data
        db.session.add(people)
        db.session.commit()
        flash(u'人员信息已保存!', 'success')
        return redirect(url_for('book.people_detail', people_id=people_id, isresident=isresident))
    form.id_type.data = people.id_type
    form.id_number.data = people.id_number
    form.name.data = people.name
    form.gender.data = people.gender
    form.phone_number.data = people.phone_number
    form.address.data = people.address
    return render_template("people_edit.html", form=form, face=face, isresident=isresident, people=people, title=u"编辑人员信息")

@book.route('/addResidents/', methods=['GET', 'POST'])
@permission_required(Permission.ADD_BOOK)
def add_residents():
    form = AddPeopleForm()
    if form.validate_on_submit():
        new_people = Residents(
            id_number=form.id_number.data,
            id_type=form.id_type.data,
            name=form.name.data,
            gender=form.gender.data,
            address=form.address.data,
            phone_number=form.phone_number.data)
        new_face = Face(
            avatar=None,
            id_type=new_people.id_type,
            id_number=new_people.id_number)
        db.session.add(new_people)
        db.session.add(new_face)
        db.session.commit()
        flash(u'新访者 %s 已添加至居民信息表!' % new_people.name, 'success')
        #return redirect(url_for('book.detail', book_id=new_book.id))
    return render_template("people_add.html", form=form, title=u"添加居民信息")

@book.route('/addVisitors/', methods=['GET', 'POST'])
@permission_required(Permission.ADD_BOOK)
def add_visitors():
    form = AddPeopleForm()
    if form.validate_on_submit():
        new_people = Visitors(
            id_number=form.id_number.data,
            id_type=form.id_type.data,
            name=form.name.data,
            gender=form.gender.data,
            address=form.address.data,
            phone_number=form.phone_number.data)
        new_face = Face(
            avatar=None,
            id_type=new_people.id_type,
            id_number=new_people.id_number)
        db.session.add(new_people)
        db.session.add(new_face)
        db.session.commit()
        flash(u'新访者 %s 已添加至外来人员信息表!' % new_people.name, 'success')
        #return redirect(url_for('book.detail', book_id=new_book.id))
    return render_template("people_add.html", form=form, title=u"添加外来人员信息")


@book.route('/<people_id>/<isResident>/delete/')
@permission_required(Permission.DELETE_BOOK)
def people_delete(people_id, isResident):
    if isResident == 'True':
        the_people = Residents.query.get_or_404(people_id)
        face = Face.query.filter(Face.resident_id==people_id).all()[0]
    else:
        the_people = Visitors.query.get_or_404(people_id)
        face = Face.query.filter(Face.visitors_id==people_id).all()[0]
    db.session.delete(the_people)
    db.session.delete(face)
    db.session.commit()
    flash(u'成功删除人员信息,人员信息已从数据库中移除', 'info')
    return redirect(request.args.get('next') or url_for('book.people_detail', people_id=people_id, isResident=isResident))
