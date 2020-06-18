import os
import secrets
from PIL import Image
from flask import url_for, current_app
from sendgrid.helpers.mail import Mail

from flaskBlog import sg

def save_profile_picture(form_picture):
  random_hex = secrets.token_hex(8)
  _, f_ext = os.path.splitext(form_picture.filename)
  picture_filename = random_hex + f_ext
  picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_filename)
  output_size = (125, 125)
  i = Image.open(form_picture)
  i.thumbnail(output_size)
  i.save(picture_path)
  return picture_filename

def send_reset_email(user):
    token = user.get_reset_token()
    message = Mail(
    from_email='cojokka@gmail.com',
    to_emails=user.email,
    subject='Password Reset Request flask Blog',
    html_content=f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
''')
    response = sg.send(message)