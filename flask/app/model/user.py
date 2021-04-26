from datetime import datetime, timedelta
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user

from itsdangerous import TimedJSONWebSignatureSerializer, SignatureExpired, BadSignature
import time

from werkzeug.security import generate_password_hash, check_password_hash

from marshmallow import Schema, fields, pre_load, validate
from marshmallow import ValidationError

from flask import session, current_app
from .. import db
from .. import login_manager


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'
    user_pk = db.Column(db.String(255), primary_key=True, unique=True)
    user_name = db.Column(db.String(80))
    user_password = db.Column(db.String(255))
    user_role = db.Column(db.String(10), default='normal')
    user_email = db.Column(db.String(255))
    user_createdOn = db.Column(db.DateTime, default=datetime.now)
    user_createdBy = db.Column(db.String(100), default=None)
    user_modifiedOn = db.Column(db.DateTime,
                            onupdate=datetime.now,
                            default=datetime.now)
    user_modifiedBy = db.Column(db.String(100), default=None)
    is_active = db.Column(db.Boolean(1), default=False)

    def __init__(self, user_data=None):
        if user_data != None:
            self.user_name = user_data['username']
            self.password = user_data['password']
            self.user_pk = user_data['user_id']
            # self.user_email = user_data['email']

    @property
    def is_group(self):
        return True

    @property
    def is_administator(self):
        return True

    @property
    def password(self):
        raise AttributeError('passowrd is not readabilty attribute')

    @password.setter
    def password(self, password):
        self.user_password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.user_password, password)

    @classmethod
    def get_user(cls, name):
        return cls.query.filter_by(user_name=name).first()

    def save_db(self):
        db.session.add(self)
        db.session.commit()

    def create_confirm_token(self, expires_in=600):

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expires_in=expires_in)

        return s.dumps({'user_pk':self.user_pk, 'user_email':self.user_email})

    def validate_confirm_token(self, token):

        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        
        try:
            data = s.loads(token)  # 驗證
        except SignatureExpired:
            #  當時間超過的時候就會引發SignatureExpired錯誤
            return False
        except BadSignature:
            #  當驗證錯誤的時候就會引發BadSignature錯誤
            return False
        return data
        

class UserSchema(Schema):
    user_id = fields.String()
    csrf_token = fields.String()
    submit = fields.String()
    username = fields.String(required=True, validate=validate.Length(3))
    password = fields.String(required=True, validate=validate.Length(6))
    confirm_password = fields.String(validate=validate.Length(6))
    email = fields.String(validate=validate.Length(6))
    remember_me = fields.Boolean()
    role = fields.String()
    create_time = fields.DateTime()
    modify_time = fields.DateTime()



    