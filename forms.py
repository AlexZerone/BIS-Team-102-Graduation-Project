from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, SelectField, DateField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo


# Auth Forms
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    user_type = SelectField('User Type', 
                          choices=[('student', 'Student'), 
                                 ('instructor', 'Instructor'), 
                                 ('company', 'Company')],
                          validators=[DataRequired()])
    
    # Student fields
    university = StringField('University')
    major = StringField('Major')
    gpa = FloatField('GPA')
    expected_graduation_date = DateField('Expected Graduation Date', format='%Y-%m-%d')
    
    # Instructor fields
    department = StringField('Department')
    specialization = StringField('Specialization')
    experience = IntegerField('Years of Experience')
    
    # Company fields
    company_name = StringField('Company Name')
    industry = StringField('Industry')
    location = StringField('Location')
    company_size = StringField('Company Size')
    founded_date = DateField('Founded Date', format='%Y-%m-%d')

    def validate(self, *args, **kwargs):
        initial_validation = super(RegistrationForm, self).validate(*args, **kwargs)
        if not initial_validation:
            return False

        if self.user_type.data == 'student':
            if not self.university.data:
                self.university.errors.append('University is required for students')
                return False
            if not self.major.data:
                self.major.errors.append('Major is required for students')
                return False
            if not self.gpa.data:
                self.gpa.errors.append('GPA is required for students')
                return False
            if not self.expected_graduation_date.data:
                self.expected_graduation_date.errors.append('Expected graduation date is required for students')
                return False

        elif self.user_type.data == 'instructor':
            if not self.department.data:
                self.department.errors.append('Department is required for instructors')
                return False
            if not self.specialization.data:
                self.specialization.errors.append('Specialization is required for instructors')
                return False
            if not self.experience.data:
                self.experience.errors.append('Years of experience is required for instructors')
                return False

        elif self.user_type.data == 'company':
            if not self.company_name.data:
                self.company_name.errors.append('Company name is required')
                return False
            if not self.industry.data:
                self.industry.errors.append('Industry is required')
                return False
            if not self.location.data:
                self.location.errors.append('Location is required')
                return False
            if not self.company_size.data:
                self.company_size.errors.append('Company size is required')
                return False
            if not self.founded_date.data:
                self.founded_date.errors.append('Founded date is required')
                return False

        return True


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
    new_password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('new_password')])
