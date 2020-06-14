import os
import secrets

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sendgrid.helpers.mail import Mail

from flaskBlog import app, db, bcrypt, login_manager, sg
from flaskBlog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskBlog.models import User, Post

# posts = [
  # {
  #   'author': 'cojokka',
  #   'title': 'Blog Post 1',
  #   'content': 'First post content',
  #   'date_posted': 'June 11, 2020'
  # },
  # {
  #   'author': 'deea',
  #   'title': 'Blog Post 2',
  #   'content': 'Second post content',
  #   'date_posted': 'June 05, 2020'
  # },
# ]

@app.route('/')
@app.route('/home')
def home():
  page = request.args.get('page', 1, type=int)
  posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
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
    if form.validate_on_submit():
      profile_pic = None
      if form.picture.data:
        profile_pic = save_profile_picture(form.picture.data)
    user = User(username=form.username.data, email=form.email.data, password=hashed_pw, image_file=profile_pic)
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
      next_page = request.args.get('next')
      return redirect(next_page) if next_page else redirect(url_for('home'))
    else:
      flash(f'Login unsuccessfull. Please check your email and/or password!', 'danger')
  return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('home'))

def save_profile_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_filename = random_hex + f_ext
  picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
  output_size = (125, 125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)
  return picture_filename

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
  form = UpdateAccountForm()
  if form.validate_on_submit():
    if form.picture.data:
      picture_file = save_profile_picture(form.picture.data)
      current_user.image_file = picture_file
    current_user.username = form.username.data
    current_user.email = form.email.data
    db.session.commit()
    flash('Your account has been updated!', 'success')
    return redirect(url_for('account'))
  elif request.method == 'GET':
    form.username.data = current_user.username
    form.email.data = current_user.email
  image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
  return render_template('account.html', 
                         title='Account Page', image_file=image_file, form=form)
  
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
  form = PostForm()
  if form.validate_on_submit():
    title = form.title.data
    content = form.content.data
    author = current_user
    new_post = Post(title=title, content=content, author=author)
    db.session.add(new_post)
    db.session.commit()
    flash('Your post has been created!', 'success')
    return redirect(url_for('home'))
  return render_template('post_form.html', title='New Post',
                          form=form, legend='New Post')
  
@app.route('/post/<int:post_id>')
def post(post_id):
   post = Post.query.get_or_404(post_id)
   return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
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
  return render_template('post_form.html', title='Edit Post',
                          form=form, legend='Edit Post')
  
@app.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
  post = Post.query.get_or_404(post_id)
  if post.author != current_user:
    abort(403)
  db.session.delete(post)
  db.session.commit()
  flash('Your post have been deleted', 'success')
  return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_post(username):
  page = request.args.get('page', 1, type=int)
  user = User.query.filter_by(username=username).first_or_404()
  posts = Post.query.filter_by(author=user)\
    .order_by(Post.date_posted.desc())\
      .paginate(page=page, per_page=2)
  return render_template('user_post.html', posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    message = Mail(
    from_email='cojokka@gmail.com',
    to_emails=user.email,
    subject='Password Reset Request flask Blog',
    html_content=f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
''')
    response = sg.send(message)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  form = RequestResetForm()
  if form.validate_on_submit():
    email = form.email.data
    user = User.query.filter_by(email=email).first()
    send_reset_email(user)
    flash('An email have been sent with instructions to reset your password!', 'info')
    return redirect(url_for('login'))
  return render_template('reset_request.html', title="Reset Password", form=form)

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for('home'))
  user = User.verify_reset_token(token)
  if user is None:
    flash('Token invalid or expired.', 'warning')
    return redirect(url_for('reset_request'))
  form = ResetPasswordForm()
  if form.validate_on_submit():
    hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user.password = hashed_pw
    db.session.commit()
    flash('Your password was updated! You can now login!', 'success')
    return redirect(url_for('login'))
  return render_template('reset_token.html', title='Reset Password', form=form)