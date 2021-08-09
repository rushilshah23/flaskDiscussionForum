from discussionForum.models import User,Post

from discussionForum.users.forms import RegisterationForm,LoginForm,UpdateAccountForm,RequestRestForm,ResetPasswordForm
from discussionForum.posts.forms import PostForm
from flask import Flask,url_for,render_template,flash,redirect,request,Blueprint
from discussionForum import db,bcrypt,mail
from flask_login import login_user, current_user,logout_user,login_required

from discussionForum.users.utils import send_reset_email,save_picture


from flask import Blueprint,current_app

users = Blueprint('users',__name__)

@users.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    regForm = RegisterationForm()
    if regForm.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(regForm.password.data).decode('utf-8')
        user = User(username=regForm.username.data,email=regForm.email.data,password = hashed_password)
        db.session.add(user)
        db.session.commit()

        flash(f'Account created for {regForm.username.data}!','success')
        return redirect(url_for('users.login'))
    return render_template('register.html',title='Register',form=regForm)

@users.route('/login',methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    loginForm = LoginForm()
    if loginForm.validate_on_submit():
        user = User.query.filter_by(email=loginForm.email.data).first()
        if user and bcrypt.check_password_hash(user.password,loginForm.password.data):
            login_user(user,remember = loginForm.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
            redirect(url_for('main.home'))
        else:
            flash("Login unsuccessful. Please check email and password",'danger')
    return render_template('login.html',title='Login',form=loginForm)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account',methods=['GET','POST'])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='profile_pics/'+current_user.image_file)
    return render_template('account.html',title="Account",image_file = image_file,form = form)


@users.route("/user/<string:username>",methods=['GET'])
def user_posts(username):
    page = request.args.get('page',1,type=int)
    user= User.query.filter_by(username = username).first_or_404()
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('user_post.html',posts=posts,title=username+" Posts",user=user)


@users.route("/reset_password",methods=['POST','GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestRestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password",'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html',title='Reset Password Request',form=form)


@users.route("/reset_password/<token>",methods=['POST','GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expire token",'warning')
        return redirect(url_for('users.reset_request'))
    print(user.email)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()

        flash(f'Password has been updated. You are now able to Login !','success')
        return redirect(url_for('users.login'))
    
    return render_template('reset_token.html',title='Reset Password',form=form)