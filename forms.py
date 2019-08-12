from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password  = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	#user_role = StringField('User Role', validators=[DataRequired(), Length(min=2, max=20)])

	submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
	#username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password  = PasswordField('Password',validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Log In')


class Reservation(FlaskForm):
	garagename = StringField('Garage Name', validators=[DataRequired()])
	spotnum = IntegerField('Spot Number', validators=[DataRequired()])
	reserve = SubmitField('Reserve')


class GarageForm(FlaskForm):
	name = StringField('Garage Name', validators=[DataRequired()])
	address = StringField('Address', validators=[DataRequired()])
	add = SubmitField('Add')
