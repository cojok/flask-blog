from flask import render_template, url_for, flash, redirect
from flask_login import login_user, current_user, logout_user
from flaskBlog import app, db, bcrypt, login_manager
from flaskBlog.forms import RegistrationForm, LoginForm
from flaskBlog.models import User, Post

posts = [
  {
    'author': 'cojokka',
    'title': 'Blog Post 1',
    'content': 'First post content',
    'date_posted': 'June 11, 2020'
  },
  {
    'author': 'deea',
    'title': 'Blog Post 2',
    'content': 'Second post content',
    'date_posted': 'June 05, 2020'
  },
]

@app.route('/')
@app.route('/home')
def home():
   return render_template('home.html', posts=posts)
 
@app.route('/about')
def about():
   return render_template('about.html', title='About Page')

@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = RegistrationForm()
  if form.validate_on_submit():
    hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    flash('Your account was created. You can now login!', 'success')
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)
 
@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=form.remember.data)
      return redirect(url_for('home'));
    else:
      flash(f'Login unsuccessfull. Please check your email and/or password!', 'danger')
  return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('home'))