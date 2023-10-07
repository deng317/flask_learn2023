# encoding:utf-8
import datetime
import os
import secrets

from PIL import Image
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from web_server import app, db, bcrypt, mail
from web_server.form import RegistrationForm, LoginForm, UpdateAccountForm, NewPost, RequestResetPassword, \
    ResetPasswordForm, TagFieldForm
from web_server.models import User, Post

# 全局变量
per_page = 10


@app.route('/', methods=["GET"])
def index():
    # Paginate操作
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.post_time.desc()).paginate(per_page=per_page, page=page)
    return render_template('main.html', posts=posts, title="主页")


@app.route('/about/')
def about():
    return render_template('about.html', title="关于我们")


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        # create_db.create_db()
        db.session.add(user)
        db.session.commit()
        flash(f'账号【{form.username.data}】注册成功', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Sign Up', form=form)


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                # user login操作
                login_user(user, remember=form.remember.data)
                # get next_page
                next_page = request.args.get('next')
                flash(f"用户【{form.email.data}】登录成功！", category='success')
                # return redirect(next_page) if next_page else redirect(url_for('index'))

                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('index'))
            else:
                flash("密码错误", category='danger')
        else:
            flash('注册信息不存在，请再次确认', category='danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/change_account/')
def change_account():
    logout_user()
    return redirect(url_for('login'))


# 裁切thumbnail图片
def thumbnail_pic_save(form_picture, path):
    out_picture_size = (100, 100)
    thumbnail_img = Image.open(form_picture)
    thumbnail_img.thumbnail(out_picture_size)
    thumbnail_img.save(path)


def save_pic(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    picture_path_old = os.path.join(app.root_path, 'static/icon', current_user.image_file)
    picture_path = os.path.join(app.root_path, 'static/icon', picture_filename)

    # 引用thumbnail处理function
    thumbnail_pic_save(form_picture, picture_path)

    if current_user.image_file != 'default.jpg':
        os.remove(picture_path_old)
    return picture_filename


@app.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    image_file = url_for('static', filename='icon/' + current_user.image_file)

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_pic(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash(message="个人信息更新成功", category='success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title=f'【{current_user.username}】的个人页面', image_file=image_file,
                           form=form)


@app.route("/post/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = NewPost()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    content=form.content.data,
                    author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(message="发表成功", category="success")
        return redirect(url_for('index'))
    return render_template('new_post.html', title=f'发帖页面页面', form=form, legend='发布新文章')


@app.route("/post/post_detail<post_id>/", methods=['GET'])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', title=f'{post.title}', post=post)


@app.route("/post/post_update<post_id>/", methods=['GET', 'POST'])
@login_required
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = NewPost()
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.post_time = datetime.datetime.now()
        db.session.commit()
        flash(message='文章更新成功', category='success')
        return redirect(url_for('post_detail', post_id=post.id))
    return render_template('new_post.html', title=f'正在更新文章[{post.title}]', post=post, form=form,
                           legend=f'正在更新文章[{post.title}]')


@app.route("/post/delete_post<post_id>", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash(message=f'文章【{post.title}】已经被删除', category='info')
        return redirect(url_for('index'))


@app.route('/user/<user_name>_posts/', methods=['GET', 'POST'])
def user_posts(user_name):
    page = request.args.get('page', 1, type=int)

    user = User.query.filter_by(username=user_name).first_or_404()
    posts = Post.query.order_by(Post.post_time.desc()).filter_by(author=user).paginate(page=page, per_page=per_page)

    return render_template('user_posts.html', posts=posts, title=f"【{user.username}】的文章", user=user)


def send_reset_email(user):
    token = user.generate_reset_token()
    msg = Message(f'关于重置用户【{user.email}】账号密码的邮件',
                  sender='happylearn2021@163.com',
                  recipients=[user.email])
    msg.body = f'''请点击下列链接进行密码重置操作：
    {url_for('reset_password', token=token, _external=True)}
    _____如果没有进行重置密码操作，却收到了这封邮件，请尽快确认您的账户信息
    '''
    mail.send(msg)


@app.route('/user/request_reset_password/', methods=['GET', 'POST'])
def request_reset_password():
    form = RequestResetPassword()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = User.generate_reset_token(user)
            send_reset_email(user)
            flash(message=f'重置密码邮件发送成功，请尽快打开邮件内链接', category='success')
            return redirect(url_for('index'))
        else:
            flash(message='这个邮箱没有注册过呢', category='danger')
    return render_template('request_reset_password.html', form=form)


@app.route('/user/reset_password/token=<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    user = User.validate_token(token)
    if user == None:
        abort(401)
        flash(f'{user}', "danger")
    elif form.validate_on_submit():
        user.password = bcrypt.generate_password_hash(form.password.data)
        db.session.commit()
        flash(message='密码修改成功', category='success')
        return redirect(url_for('index'))
    return render_template('reset_password.html', form=form)


@app.route("/users/", methods=['GET', 'POST'])
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', title=f'用户列表', users=users)


@app.route('/equipment_spec/', methods=['GET', 'POST'])
def equipment_spec():
    posts = Post.query.all()
    if request.method == 'POST':
        datas = request.form.to_dict()
        for key, value in datas.items():
            if '-' in key:
                name, id = key.split('-')
                post = Post.query.get_or_404(int(id))
                if name == 'title':
                    post.title = value
                elif name == 'content':
                    post.content = value
                db.session.commit()
            else:
                pass
        flash('保存成功', 'info')

    return render_template('equipt_spec.html', posts=posts, title='设备规格书')
