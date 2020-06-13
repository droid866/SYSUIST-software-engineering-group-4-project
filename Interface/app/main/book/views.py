from app import db
from app.models import Book, Log, Comment, Permission, Tag, book_tag, Residents, Visitors, Temperature
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user
from . import book
from .forms import SearchForm, EditBookForm, AddBookForm, EditPeopleForm, AddPeopleForm
from ..comment.forms import CommentForm
from ..decorators import admin_required, permission_required


@book.route('/')
def index():
    search_word = request.args.get('search', None)
    search_form = SearchForm()
    page = request.args.get('page', 1, type=int)

    the_books = Book.query
    if not current_user.can(Permission.UPDATE_BOOK_INFORMATION):
        the_books = Book.query.filter_by(hidden=0)

    if search_word:
        search_word = search_word.strip()
        the_books = the_books.filter(db.or_(
            Book.title.ilike(u"%%%s%%" % search_word), Book.author.ilike(u"%%%s%%" % search_word), Book.isbn.ilike(
                u"%%%s%%" % search_word), Book.tags.any(Tag.name.ilike(u"%%%s%%" % search_word)), Book.subtitle.ilike(
                u"%%%s%%" % search_word))).outerjoin(Log).group_by(Book.id).order_by(db.func.count(Log.id).desc())
        search_form.search.data = search_word
    else:
        the_books = Book.query.order_by(Book.id.desc())

    pagination = the_books.paginate(page, per_page=8)
    result_books = pagination.items
    return render_template("book.html", books=result_books, pagination=pagination, search_form=search_form,
                           title=u"书籍清单")

@book.route('/people/')
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
        the_residents = Residents.query.order_by(Residents.id.desc())
        the_visitors = Visitors.query.order_by(Visitors.id.desc())

    residents_pagination = the_residents.paginate(page, per_page=8)
    residents_result = residents_pagination.items

    visitors_pagination = the_visitors.paginate(page, per_page=8)
    visitors_result = visitors_pagination.items

    return render_template("people.html", residents=residents_result, visitors=visitors_result,
        visitors_pagination=visitors_pagination, residents_pagination=residents_pagination, search_form=search_form,
        title_resident=u"小区居民", title_visitor=u"外来人员")

@book.route('/<book_id>/')
def detail(book_id):
    the_book = Book.query.get_or_404(book_id)

    if the_book.hidden and (not current_user.is_authenticated or not current_user.is_administrator()):
        abort(404)

    show = request.args.get('show', 0, type=int)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if show in (1, 2):
        pagination = the_book.logs.filter_by(returned=show - 1) \
            .order_by(Log.borrow_timestamp.desc()).paginate(page, per_page=5)
    else:
        pagination = the_book.comments.filter_by(deleted=0) \
            .order_by(Comment.edit_timestamp.desc()).paginate(page, per_page=5)

    data = pagination.items
    return render_template("book_detail.html", book=the_book, data=data, pagination=pagination, form=form,
                           title=the_book.title)

'''
@book.route('/<int:book_id>/edit/', methods=['GET', 'POST'])
@permission_required(Permission.UPDATE_BOOK_INFORMATION)
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = EditBookForm()
    if form.validate_on_submit():
        book.isbn = form.isbn.data
        book.title = form.title.data
        book.origin_title = form.origin_title.data
        book.subtitle = form.subtitle.data
        book.author = form.author.data
        book.translator = form.translator.data
        book.publisher = form.publisher.data
        book.image = form.image.data
        book.pubdate = form.pubdate.data
        book.tags_string = form.tags.data
        book.pages = form.pages.data
        book.price = form.price.data
        book.binding = form.binding.data
        book.numbers = form.numbers.data
        book.summary = form.summary.data
        book.catalog = form.catalog.data
        db.session.add(book)
        db.session.commit()
        flash(u'书籍资料已保存!', 'success')
        return redirect(url_for('book.detail', book_id=book_id))
    form.isbn.data = book.isbn
    form.title.data = book.title
    form.origin_title.data = book.origin_title
    form.subtitle.data = book.subtitle
    form.author.data = book.author
    form.translator.data = book.translator
    form.publisher.data = book.publisher
    form.image.data = book.image
    form.pubdate.data = book.pubdate
    form.tags.data = book.tags_string
    form.pages.data = book.pages
    form.price.data = book.price
    form.binding.data = book.binding
    form.numbers.data = book.numbers
    form.summary.data = book.summary or ""
    form.catalog.data = book.catalog or ""
    return render_template("book_edit.html", form=form, book=book, title=u"编辑书籍资料")
'''
'''
@book.route('/add/', methods=['GET', 'POST'])
@permission_required(Permission.ADD_BOOK)
def add():
    form = AddBookForm()
    form.numbers.data = 3
    if form.validate_on_submit():
        new_book = Book(
            isbn=form.isbn.data,
            title=form.title.data,
            origin_title=form.origin_title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            translator=form.translator.data,
            publisher=form.publisher.data,
            image=form.image.data,
            pubdate=form.pubdate.data,
            tags_string=form.tags.data,
            pages=form.pages.data,
            price=form.price.data,
            binding=form.binding.data,
            numbers=form.numbers.data,
            summary=form.summary.data or "",
            catalog=form.catalog.data or "")
        db.session.add(new_book)
        db.session.commit()
        flash(u'书籍 %s 已添加至图书馆!' % new_book.title, 'success')
        return redirect(url_for('book.detail', book_id=new_book.id))
    return render_template("book_edit.html", form=form, title=u"添加新书")
'''

@book.route('/people/<people_id>/<isresident>/')
def people_detail(people_id, isresident):
    show = request.args.get('show', 0, type=int)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()

    if show != 0:
        show = 1

    if isresident == 'True':
        the_people = Residents.query.get_or_404(people_id)
        pagination = Temperature.query.filter(Temperature.resident_id==people_id).order_by(Temperature.record_timestamp.desc()).paginate(page, per_page=10)
    else:
        the_people = Visitors.query.get_or_404(people_id)
        pagination = Temperature.query.filter(Temperature.visitors_id==people_id).order_by(Temperature.record_timestamp.desc()).paginate(page, per_page=10)
    
    logs = pagination.items

    return render_template("people_detail.html", people=the_people, logs=logs, form=form,
        isresident=isresident, title=the_people.name)



@book.route('/<int:book_id>/edit/', methods=['GET', 'POST'])
@permission_required(Permission.UPDATE_BOOK_INFORMATION)
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    form = EditBookForm()
    if form.validate_on_submit():
        book.isbn = form.isbn.data
        book.title = form.title.data
        book.origin_title = form.origin_title.data
        book.subtitle = form.subtitle.data
        book.author = form.author.data
        book.translator = form.translator.data
        book.publisher = form.publisher.data
        book.image = form.image.data
        book.pubdate = form.pubdate.data
        book.tags_string = form.tags.data
        book.pages = form.pages.data
        book.price = form.price.data
        book.binding = form.binding.data
        book.numbers = form.numbers.data
        book.summary = form.summary.data
        book.catalog = form.catalog.data
        db.session.add(book)
        db.session.commit()
        flash(u'书籍资料已保存!', 'success')
        return redirect(url_for('book.detail', book_id=book_id))
    form.isbn.data = book.isbn
    form.title.data = book.title
    form.origin_title.data = book.origin_title
    form.subtitle.data = book.subtitle
    form.author.data = book.author
    form.translator.data = book.translator
    form.publisher.data = book.publisher
    form.image.data = book.image
    form.pubdate.data = book.pubdate
    form.tags.data = book.tags_string
    form.pages.data = book.pages
    form.price.data = book.price
    form.binding.data = book.binding
    form.numbers.data = book.numbers
    form.summary.data = book.summary or ""
    form.catalog.data = book.catalog or ""
    return render_template("book_edit.html", form=form, book=book, title=u"编辑人员信息")

@book.route('/<int:people_id>/<isresident>/resident_edit/', methods=['GET', 'POST'])
@permission_required(Permission.UPDATE_BOOK_INFORMATION)
def people_edit(people_id, isresident):
    if isresident == 'True':
        people = Residents.query.get_or_404(people_id)
    else:
        people = Visitors.query.get_or_404(people_id)
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
        flash(u'书籍资料已保存!', 'success')
        return redirect(url_for('book.people_detail', people_id=people_id, isresident=isresident))
    form.id_type.data = people.id_type
    form.id_number.data = people.id_number
    form.name.data = people.name
    form.gender.data = people.gender
    form.phone_number.data = people.phone_number
    form.address.data = people.address
    return render_template("people_edit.html", form=form, people=people, title=u"编辑人员信息")

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
        db.session.add(new_people)
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
        db.session.add(new_people)
        db.session.commit()
        flash(u'新访者 %s 已添加至外来人员信息表!' % new_people.name, 'success')
        #return redirect(url_for('book.detail', book_id=new_book.id))
    return render_template("people_add.html", form=form, title=u"添加外来人员信息")

@book.route('/<int:book_id>/delete/')
@permission_required(Permission.DELETE_BOOK)
def delete(book_id):
    the_book = Book.query.get_or_404(book_id)
    the_book.hidden = 1
    db.session.add(the_book)
    db.session.commit()
    flash(u'成功删除书籍,用户已经无法查看该书籍', 'info')
    return redirect(request.args.get('next') or url_for('book.detail', book_id=book_id))

@book.route('/<int:people_id>/<isResident>/delete/')
@permission_required(Permission.DELETE_BOOK)
def people_delete(people_id, isResident):
    if isResident == 'True':
        the_people = Residents.query.get_or_404(people_id)
    else:
        the_people = Visitors.query.get_or_404(people_id)
    db.session.delete(the_people)
    db.session.commit()
    flash(u'成功删除人员信息,人员信息已从数据库中移除', 'info')
    return redirect(request.args.get('next') or url_for('book.people_detail', people_id=people_id, isResident=isResident))

@book.route('/<int:book_id>/put_back/')
@admin_required
def put_back(book_id):
    the_book = Book.query.get_or_404(book_id)
    the_book.hidden = 0
    db.session.add(the_book)
    db.session.commit()
    flash(u'成功恢复书籍,用户现在可以查看该书籍', 'info')
    return redirect(request.args.get('next') or url_for('book.detail', book_id=book_id))


@book.route('/tags/')
def tags():
    search_tags = request.args.get('search', None)
    page = request.args.get('page', 1, type=int)
    the_tags = Tag.query.outerjoin(book_tag).group_by(book_tag.c.tag_id).order_by(
        db.func.count(book_tag.c.book_id).desc()).limit(30).all()
    search_form = SearchForm()
    search_form.search.data = search_tags

    data = None
    pagination = None

    if search_tags:
        tags_list = [s.strip() for s in search_tags.split(',') if len(s.strip()) > 0]
        if len(tags_list) > 0:
            the_books = Book.query
            if not current_user.can(Permission.UPDATE_BOOK_INFORMATION):
                the_books = Book.query.filter_by(hidden=0)
            the_books = the_books.filter(
                db.and_(*[Book.tags.any(Tag.name.ilike(word)) for word in tags_list])).outerjoin(Log).group_by(
                Book.id).order_by(db.func.count(Log.id).desc())
            pagination = the_books.paginate(page, per_page=8)
            data = pagination.items

    return render_template('book_tag.html', tags=the_tags, title='Tags', search_form=search_form, books=data,
                           pagination=pagination)
