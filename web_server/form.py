from flask_wtf import FlaskForm  # 导入FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, TextAreaField, FormField, FieldList
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
import email_validator
from flask_login import current_user
from web_server.models import User


class RegistrationForm(FlaskForm):
    '''RegistrationForm(FlaskForm)，注册表单'''
    username = StringField('昵称', validators=[DataRequired(message="用户名不能为空"),
                                                   Length(min=6, max=20, message="长度6--20")])
    email = EmailField('邮箱', validators=[DataRequired(message="请输入Email"), Email(message="Email格式不正确")])
    password = PasswordField('密码',
                             validators=[DataRequired(message="请输入密码"), Length(min=6, max=20, message="长度6-20")])
    password_confirm = PasswordField('确认密码', validators=[DataRequired(message="再次输入密码"),
                                                                     Length(min=6, max=20, message="长度6-20"),
                                                                     EqualTo("password", message="两次输入密码不一致")])
    submit = SubmitField('点我注册')

    def validate_email(self, extra_validators=None):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            raise ValidationError(message='邮箱已被使用')
        else:
            try:
                email_validator.validate_email(self.email.data)
            except:
                raise ValidationError(message="没有此邮箱域名")

    def validate_username(self, extra_validators=None):
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            raise ValidationError(message='用户名已被使用')


class UpdateAccountForm(FlaskForm):
    '''RegistrationForm(FlaskForm)，注册表单'''
    username = StringField('昵称', validators=[DataRequired(message="用户名不能为空"),
                                                   Length(min=6, max=20, message="长度6--20")])
    email = EmailField('邮箱', validators=[DataRequired(message="请输入Email"), Email(message="Email格式不正确")])
    submit = SubmitField('确定更新')
    picture = FileField('头像', validators=[FileAllowed(['jpg', 'png', 'jpeg'], message="")])

    def validate_email(self, extra_validators=None):
        if self.email.data != current_user.email:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                raise ValidationError(message='邮箱已被使用')
            else:
                try:
                    email_validator.validate_email(self.email.data)
                except:
                    raise ValidationError(message="没有此邮箱域名")

    def validate_username(self, extra_validators=None):
        if self.username.data != current_user.username:
            user = User.query.filter_by(username=self.username.data).first()
            if user:
                raise ValidationError(message='用户名已被使用')


class LoginForm(FlaskForm):
    '''LoginForm'''
    email = StringField('邮箱', validators=[DataRequired(message="请输入邮箱"), Email(message="邮箱验证错误")])
    password = PasswordField('密码', validators=[DataRequired(message="请输入密码")])
    remember = BooleanField('记住我')
    submit = SubmitField('点我登录')


class NewPost(FlaskForm):
    title = StringField("标题", validators=[DataRequired(message="请输入标题")])
    content = TextAreaField('内容', validators=[DataRequired(message="请输入内容")])
    submit = SubmitField("提交")


class RequestResetPassword(FlaskForm):
    email = StringField('邮箱', validators=(DataRequired(message='输入邮箱'), Email(message='输入正确格式邮箱')))
    submit = SubmitField('提交')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('未查询到此邮箱到注册信息，请确认')


class ResetPasswordForm(FlaskForm):
    '''RegistrationForm(FlaskForm)，注册表单'''
    password = PasswordField('密码',
                             validators=[DataRequired(message="请输入密码"), Length(min=6, max=20, message="长度6-20"),
                                         EqualTo('password_confirm', message="两次输入密码不一致")])
    password_confirm = PasswordField('确认密码', validators=[DataRequired(message="再次输入密码"),
                                                                     Length(min=6, max=20, message="长度6-20"),
                                                                     EqualTo("password", message="两次输入密码不一致")])
    submit = SubmitField('确认更新密码')


class SpecListForm(FlaskForm):
    title = StringField("标题", validators=[DataRequired(message="请输入标题")])
    content = TextAreaField('内容', validators=[DataRequired(message="请输入内容")])
    submit = SubmitField("提交")

class TagFieldForm(FlaskForm):
    tag = FieldList(FormField(SpecListForm))