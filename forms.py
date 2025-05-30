from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, SubmitField, SelectField,
    DateField, FloatField, IntegerField, TextAreaField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional


class RegisterForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('Account Type', choices=[
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('company', 'Company')
    ], validators=[DataRequired()])
    

    # Student fields
    university = StringField('University', validators=[Optional(), Length(max=128)])
    major = StringField('Major', validators=[Optional(), Length(max=64)])
    gpa = FloatField('GPA', validators=[Optional(), NumberRange(min=0, max=4)])
    expected_graduation_date = DateField('Expected Graduation Date', validators=[Optional()], format='%Y-%m-%d')

    # Instructor fields
    department = StringField('Department', validators=[Optional(), Length(max=128)])
    specialization = StringField('Specialization', validators=[Optional(), Length(max=128)])
    experience = IntegerField('Years of Experience', validators=[Optional(), NumberRange(min=0)])

    # Company fields
    company_name = StringField('Company Name', validators=[Optional(), Length(max=128)])
    industry = StringField('Industry', validators=[Optional(), Length(max=128)])
    location = StringField('Location', validators=[Optional(), Length(max=128)])
    company_size = IntegerField('Company Size', validators=[Optional(), NumberRange(min=1)])
    founded_date = DateField('Founded Date', validators=[Optional()], format='%Y-%m-%d')

    submit = SubmitField('Create Account')



class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Profile Form
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    duration = StringField('Duration', validators=[DataRequired(), Length(max=50)])