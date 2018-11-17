import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, ImageResize, ResizeAgain
from flaskblog.models import User, Post, Photos
from flask_login import login_user, current_user, logout_user, login_required
import time
import logging
from time import gmtime, strftime

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    # posts = Post.query.all()
    # return render_template('home.html', posts=posts)
    if not current_user.is_authenticated:
        logging.warning('Unauthorize access used to route home on time ' \
            + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
        return redirect(url_for('login'))

    logger_helper('info', str(current_user.username), ' accesed the home page ', \
            strftime("%Y-%m-%d %H:%M:%S", gmtime()), request.remote_addr)

    form = ImageResize()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if form.picture.data:
            try:
                picture_file = save_picture(form.picture.data, float(form.dimension.data))
                _temp = save_original_picture(form.picture.data, picture_file['picture_fn'])
                logger_helper('info', str(current_user.username), ' resized the image ' \
                + str(picture_file['picture_fn']) + ' with dimensions ' \
                + str(form.dimension.data), strftime("%Y-%m-%d %H:%M:%S", gmtime()), request.remote_addr)
            except Exception as e:
                logging.error('User ' + str(current_user.username) + ' failed to save the original image at ' \
                 + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
            
            try:
                photo = Photos(original=os.path.join('/static/profile_pics', 'original_'+picture_file['picture_fn']), 
                                            squared=os.path.join('/static/profile_pics', picture_file['picture_fn']), 
                                            author=current_user)
                db.session.add(photo)
                db.session.commit()
                logging.info('User ' + str(current_user.username) + \
                    ' saved an image ti the DB and the access was successful' \
                 + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
            except Exception as e:
                logging.error('User ' + str(current_user.username) + \
                    ' failed to save the image to the DB ' \
                 + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)

            flash('Your post has been created!', 'success')

        
        return redirect(url_for('show_uploaded'))
    
    elif request.method == 'GET':
        form = ImageResize()
        return render_template('home.html', title='Home', form=form)
    return render_template('home.html', title='Home', form=form)


@app.route("/uploaded", methods=['GET', 'POST'])
def show_uploaded():
    if not current_user.is_authenticated:
        logging.warning('Unauthorize access used to route home on time ' \
            + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
        return redirect(url_for('login'))
    logging.info('User ' + str(current_user.username) + \
        ' accessed the uploaded page at ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + \
        ' from ' + request.remote_addr)
    posts = Photos.query.filter_by(user_id=current_user.id).all()
    return render_template('images.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        logging.info('New user ' + str(form.username.data) + \
            ' just signed on! ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            logging.info("Login successful for email id " + str(form.email.data) + \
                ' at ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            logging.info("Login Unsuccessful for email id " + str(form.email.data) + \
                ' at ' + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + ' from ' \
                + str(request.remote_addr))
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    logging.info("Logout successful for email id " + str(current_user.username) + \
        ' at ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
    logout_user()
    return redirect(url_for('login'))


def save_original_picture(form_picture, filename):
    picture_fn = 'original_' + filename
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)
    return {'picture_fn':picture_fn, 'picture_path': picture_path}

def save_picture(form_picture, dimension):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    i = Image.open(form_picture)
    width, height = i.size
    width = min(width, height)
    if width < dimension: dimension=width
    output_size = (int(dimension), int(dimension))
    i = i.resize(output_size)
    i.save(picture_path)
    return {'picture_fn':picture_fn, 'picture_path': picture_path}


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data, 125)['picture_fn']
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        logging.info("Account updated for User " + str(current_user.username) + \
            ' at ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        logging.info("Account info requested for " + str(current_user.username) + \
            ' at ' + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ' from ' + request.remote_addr)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


def logger_helper(typ, identity, accessed, at_time, ip_addr):
    if typ=='info':
        logging.info('User ' + str(identity) + str(accessed) + ' at: ' +  str(at_time) + ' from ' + str(ip_addr))
