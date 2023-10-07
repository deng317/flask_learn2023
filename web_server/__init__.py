# encoding:utf-8
import os

from flask import Flask, render_template, flash, url_for, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail



app = Flask(__name__)
app.config['SECRET_KEY'] = "976114a709268b43a50a1719b504909f929908a815bf02e37ace5e50e92a8125"

# 配置数据库URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Mail配置
app.config['MAIL_SERVER'] = 'smtp.163.com'
# 163:Non SSL:25/ SSL:465/994
app.config['MAIL_PORT'] =25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'happylearn2021@163.com'
app.config['MAIL_PASSWORD'] = 'EQYYYDYYOTESKQSD'

# 生成数据库实例
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager=LoginManager(app)
login_manager.login_message_category = 'info'
login_manager.login_message = u'这里是只有会员才能接触到到页面'
login_manager.login_view = 'login'
mail = Mail(app)

from web_server import routes

#关于加密：1）明文储存，不需要破解
        # 2.对称加密，破解难度中等，但是前提是key必须保密
        # 3。hash,(单项、特殊、salt)
# 1. saltRounds:正数
# 2。myPassword:明文密码字符串
# 3。salt：128bit，22字符
# 4。 循环加salt