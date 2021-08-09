import secrets
import os
from PIL import Image
from flask_mail import Message
from discussionForum import mail
from flask import Flask,url_for
from flask import current_app

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.split(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(current_app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i =Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password reset request',sender='noreply@demo.com',recipients=[user.email])
    msg.body= f'''To reset your password visit the following link:
    {url_for('users.reset_token',token=token,_external=True)}
    If you did not make this request then simply ignore this email and no changes would be made
    '''
    mail.send(msg)