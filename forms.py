from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, EmailField, SubmitField, 
    SelectField, DateField, FloatField, IntegerField, validators
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, NumberRange, Optional
from models import get_records  # Assuming you have database access

class BaseUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(min=2, max=50)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(min=2, max=50)
    ])
    email = EmailField('Email', validators=[
        DataRequired(), 
        Email(), 
        Length(max=100)
    ])


class RegistrationForm(BaseUserForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters"),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')
    user_type = SelectField(
    'Account Type',
    choices=[],  # Will be populated dynamically
    validators=[validators.DataRequired()],
    render_kw={"class": "form-select"}
)
    
    # Student fields
    university = StringField('University', validators=[Optional()])
    major = StringField('Major', validators=[Optional()])
    gpa = FloatField('GPA', validators=[
        Optional(),
        NumberRange(min=0.0, max=4.0, message="GPA must be between 0.0 and 4.0")
    ])
    expected_graduation = DateField('Expected Graduation', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    
    # Instructor fields
    department = StringField('Department', validators=[Optional()])
    specialization = StringField('Specialization', validators=[Optional()])
    experience = IntegerField('Experience (years)', validators=[
        Optional(),
        NumberRange(min=0, max=50, message="Experience must be between 0-50 years")
    ])
    
    # Company fields
    company_name = StringField('Company Name', validators=[Optional()])
    industry = StringField('Industry', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    company_size = SelectField('Company Size', 
        choices=[],  # Populated dynamically in _init_
        validators=[Optional()]
    )
    founded_date = DateField('Founded Date', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        # Dynamic choices from database
        self.user_type.choices = [(t['Name'], t['Name'].title()) 
                                for t in get_records("SELECT Name FROM user_types")]
        self.company_size.choices = [(s['SizeID'], s['Name']) 
                                   for s in get_records("SELECT SizeID, Name FROM company_sizes")]

    def validate(self, **kwargs):
        # Initial validation
        if not super().validate():
            return False

        # Conditional validation based on user type
        user_type = self.user_type.data.lower()
        valid = True

        if user_type == 'student':
            if not self.university.data:
                self.university.errors.append('University is required for students')
                valid = False
            if not self.major.data:
                self.major.errors.append('Major is required for students')
                valid = False
            if self.gpa.data is None:
                self.gpa.errors.append('GPA is required for students')
                valid = False

        elif user_type == 'instructor':
            if not self.department.data:
                self.department.errors.append('Department is required for instructors')
                valid = False
            if not self.specialization.data:
                self.specialization.errors.append('Specialization is required for instructors')
                valid = False
            if self.experience.data is None:
                self.experience.errors.append('Experience is required for instructors')
                valid = False

        elif user_type == 'company':
            if not self.company_name.data:
                self.company_name.errors.append('Company name is required')
                valid = False
            if not self.industry.data:
                self.industry.errors.append('Industry is required')
                valid = False
            if not self.location.data:
                self.location.errors.append('Location is required')
                valid = False
            if not self.company_size.data:
                self.company_size.errors.append('Company size is required')
                valid = False

        return valid

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Sign In')

class ProfileForm(BaseUserForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired()
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8),
        EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm New Password')
    submit = SubmitField('Change Password')
    
