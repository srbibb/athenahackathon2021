from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, LogActivity
from app.models import User, Post
from sqlalchemy import desc

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template("index.html", title='Home Page')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/leaderboard/<username>')
@login_required
def leaderboard(username):
    return render_template("leaderboard.html", user=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, points=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations {}, are now a registered user!'.format(form.username.data))
        form = LogActivity()
        return render_template("user.html",user=user.username, form=form)
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = db.session.query(Post).order_by(desc(Post.id)).limit(20).all()
    form = LogActivity()
    if form.validate_on_submit():
        post = Post(action=form.action.data, item=form.item.data,body=form.comment.data, author=current_user)
        if post.body is None or post.body == '':
            post.body = post.action + ' ' + post.item       
        post.calculate_points()
         
        user.points = user.points + post.points
        db.session.add(post)
        db.session.commit()
        return redirect(request.url)
        
    return render_template("user.html",user=username, posts=posts, form=form, points=user.points)


@app.route('/test')
def found():
  return 





