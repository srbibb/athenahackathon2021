from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, LogActivity, EmptyForm
from app.models import User, Post
from sqlalchemy import desc
from datetime import datetime

@app.route('/')
@app.route('/index')
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
    pointlist = current_user.followed_points().all()
    return render_template("leaderboard.html", user=username, points=pointlist)

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
        flash('Congratulations {}, you are now a registered user!'.format(form.username.data))
        return redirect(url_for('user',username=user.username))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET','POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    posts = db.session.query(Post).order_by(desc(Post.id)).limit(20).all()
    form = LogActivity()
    form2 = EmptyForm()
    #posts = current_user.followed_posts().all()
    if form.validate_on_submit():
        post = Post(action=form.action.data, item=form.item.data,body=form.comment.data, author=current_user)
        post.calculate_points()
        if form.action.data != 'have something else to share':
            if post.points == 1:
                points_str = 'point'
            else:
                points_str = 'points'
            if post.item is None or len(form.comment.data)==0:
                post.body = ' says: "I {}." They have earned {} {}!'.format(post.action.lower(), str(post.points), points_str)
            else:
                post.body = ' says: "I {} {}." They have earned {} points!'.format(post.action.lower(), post.item,str(post.points))
            if form.comment.data is not None or len(form.comment.data)>0:
                post.body = post.body + '\n' + form.comment.data
        post.timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y ")

        user.points += post.points
        db.session.add(post)
        db.session.commit()
        form = LogActivity()
        return redirect(request.url)
        
    return render_template("user.html",user=user, posts=posts, form=form, points=user.points)

@app.route('/update_like',methods=['POST'])
@login_required
def update_like():
    username =  request.args.get('username')
    post_id = request.args.get('post_id')
   
    post = Post.query.get(post_id)
    post.likes += 1
    db.session.commit()
    return redirect(url_for('user', username=username))


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))