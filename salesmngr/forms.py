from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import email_validator
from salesmngr.models import User

class RegistrationForm(FlaskForm):
    first_and_lastname = StringField("Etu- ja Sukunimi",
                                     validators=[DataRequired()])
    email = StringField("Sähköpostiosoite",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Salasana",
                             validators=[DataRequired()])
    confirm_password = PasswordField("Salasana uudestaan",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Kirjaudu sisään")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Kyseinen sähköposti on jo käytössä.')


class LoginForm(FlaskForm):
    email = StringField("Sähköpostiosoite",
                        validators=[DataRequired(), Email()])
    password = PasswordField("Salasana",
                             validators=[DataRequired()])
    remember = BooleanField("Muista minut")
    submit = SubmitField("Kirjaudu sisään")

class RequestResetForm(FlaskForm):
    email = StringField("Sähköpostiosoite",
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Vaihda salasana")
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Kyseisellä sähköpostilla ei löytynyt tiliä. Rekisteröidy ensin.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Salasana",
                             validators=[DataRequired()])
    confirm_password = PasswordField("Salasana uudestaan",
                                     validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Päivitä salasana")