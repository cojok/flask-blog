from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from flaskBlog import db
from flaskBlog.models import Post
from flaskBlog.posts.forms import PostForm
posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET', 'POST'])
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
    return redirect(url_for('main.home'))
  return render_template('post_form.html', title='New Post',
                          form=form, legend='New Post')
  
@posts.route('/post/<int:post_id>')
def post(post_id):
   post = Post.query.get_or_404(post_id)
   return render_template('post.html', title=post.title, post=post)

@posts.route("/post/<int:post_id>/edit", methods=['GET', 'POST'])
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
      return redirect(url_for('posts.post', post_id=post.id))
  elif request.method == 'GET':
      form.title.data = post.title
      form.content.data = post.content
  return render_template('post_form.html', title='Edit Post',
                          form=form, legend='Edit Post')
  
@posts.route('/post/<int:post_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
  post = Post.query.get_or_404(post_id)
  if post.author != current_user:
    abort(403)
  db.session.delete(post)
  db.session.commit()
  flash('Your post have been deleted', 'success')
  return redirect(url_for('main.home'))