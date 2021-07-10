from app.models import User,Post
import secrets
import os
from app.forms import RegisterationForm,LoginForm,UpdateAccountForm
from flask import Flask,url_for,render_template,flash,redirect,request
from app import app,db,bcrypt
from flask_login import login_user, current_user,logout_user,login_required
from PIL import Image


posts = [
    {
        'author':'Rushil Shah',
        'title':"Blog post 1",
        'content':'first post content',
        'date_posted':'April 20,2018'
        
    },
    {
        'author':'Saloni Shah',
        'title':"Blog post 2",
        'content':'second post content',
        'date_posted':'August 20,2018'
        
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html',posts=posts,title='Home')

@app.route("/about")
def about():
    return render_template('about.html',title='about')

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    regForm = RegisterationForm()
    if regForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(regForm.password.data).decode('utf-8')
        user = User(username=regForm.username.data,email=regForm.email.data,password = hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {regForm.username.data}!','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=regForm)

@app.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user and bcrypt.check_password_hash(user.password,loginForm.password.data):
            login_user(user,remember = loginForm.remember.data)
            next_page = request.args.get('next')
            return redirect(nwxt_page) if next_page else redirect(url_for('home'))
            redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Please check email and password",'danger')
    return render_template('login.html',title='Login',form=loginForm)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))



def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.split(form_picture.filename)
    picture_fn = random_hex+f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)
    output_size = (125,125)
    i =Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route('/account',methods=['GET','POST'])
@login_required
def account():  
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated !",'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title="Account",image_file = image_file,form = form)
