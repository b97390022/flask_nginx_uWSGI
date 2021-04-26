from flask import Flask, current_app, render_template, request, session, Blueprint, make_response, flash, url_for, redirect
from flask_restful import Api, Resource, reqparse

from marshmallow import ValidationError, INCLUDE, EXCLUDE

from ..model.user import UserModel, UserSchema
from .. import login_manager, db, mail
from .abort_message import abort_msg

from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email
from datetime import timedelta
import uuid

auth = Blueprint('auth', __name__, template_folder='auth', static_folder='static')
api = Api(auth)

users_schema = UserSchema()

@login_manager.user_loader  
def user_loader(user_id):  

    # query = UserModel.get_user(user_id)
    # if query == None:
    #     return

    user = UserModel()  
    user.id = user_id

    return user 
    

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired()])
    email = StringField('Email', validators=[Email()])
    submit = SubmitField('Sign up')

class Signup(Resource):
    def post(self):
        try:
            # 資料驗證
            user_data = users_schema.load(request.form, partial=True, unknown=EXCLUDE)
            # 註冊
            
            user_name = user_data['username']
            query = UserModel.get_user(user_name)
 
            if query != None:
                return 'repead_user'

            if user_data['password'] != user_data['confirm_password']:
                return 'password_not_match'
            # UUID
            user_data['user_id'] = str(uuid.uuid4())
            new_user = UserModel(user_data)
            new_user.user_email = user_data['email']
            
            token = new_user.create_confirm_token()

            mail.send_confirm_email(current_app._get_current_object(), user = new_user, token = token)

            new_user.save_db()
            # new_user.save_session()

            # 重新登入
            # return redirect(url_for('.login'))

        except ValidationError as error:
            return {'errors': error.messages}, 400

        except Exception as e:
            return {'errors': abort_msg(e)}, 500

    def get(self):

        sign_up_form = SignupForm()

        return make_response(render_template('/auth/signup.html', form=sign_up_form))


class Login(Resource):

    def get(self):

        login_form = LoginForm()

        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'GET':
            return make_response(render_template('/auth/login.html', form=login_form))

    def post(self):
        try:
            # 資料驗證
            user_data = users_schema.load(request.form)
            # print(user_data)
            user_id = user_data['username']
            user_password = user_data['password']
            remember_me = user_data.get('remember_me')
            
            # Find Database
            query = UserModel.get_user(user_id)

            if query != None and query.verify_password(user_password):

                if not query.is_active:
                    flash('使用者帳號尚未啟用。', 'error')
                    return redirect(url_for('.login'))

                user_data['user_id'] = user_id
                user = UserModel(user_data)
                user.id = user_id

                session.permanent = True
                login_user(user, duration=timedelta(minutes=60), remember=remember_me, force=True)

                # flash(f'Logged in as: {current_user.id}, have a nice day.')

                return redirect(url_for('index'))

                # return {'msg': 'ok'}, 200
            else:
                flash('使用者帳號或密碼錯誤，請再試一次。', 'error')
                return redirect(url_for('.login'))
                # return {'errors': 'incorrect username or password'}, 400

        except ValidationError as error:
            # flash(f'ValidationError error: {error}', 'error')
            return {'errors': error.messages}, 400

        except Exception as e:
            # flash(f'Other errors: {abort_msg(e)}', 'error')
            return {'errors': abort_msg(e)}, 500

class user_confirm(Resource):
    def get(self, token):
        user = UserModel()
        data = user.validate_confirm_token(token)
        if data:
            user = UserModel.query.filter_by(user_pk=data.get('user_pk')).first()
            user.is_active = True
            user.user_email = data.get('user_email')
            db.session.add(user)
            db.session.commit()

            flash('驗證完成!請重新登入一次。', 'info')
            
            return redirect(url_for('.login'))
        else:
            flash('wrong token, 請重新申請一次。', 'error')

            return redirect(url_for('.login'))

class Logout(Resource):
    def get(self):

        logout_user()  

        return redirect(url_for('.login'))
        # UserModel.remove_session()
        # return {'msg': 'logout'}, 200

api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(user_confirm, '/user_confirm/<token>')
