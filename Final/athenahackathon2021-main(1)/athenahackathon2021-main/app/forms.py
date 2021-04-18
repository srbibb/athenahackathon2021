from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username has already been registered. Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address has already been registered. Please use a different email address.')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class LogActivity(FlaskForm):
    actions = {'donated':20,'recycled':1,'upcycled':15,'reused':3,'purchased second hand':20, 'completed the weekly challenge':25,'have something else to share':0}
    action = SelectField('Action:',choices=list(actions.keys()), validators=[DataRequired()])
    item = StringField()
    comment = TextAreaField('Share a comment on your achievement?')
    submit = SubmitField('Log Activity')
