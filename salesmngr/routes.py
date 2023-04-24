from salesmngr.models import User
from flask import render_template, url_for, flash, redirect, request
from salesmngr.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
from salesmngr import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return "<H1>About page</h1>"


@app.route("/rekisteröidy", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        with app.app_context():
            user = User(first_and_lastname=form.first_and_lastname.data, email=form.email.data,
                        password=hashed_password)
            db.session.add(user)
            db.session.commit()
        flash(f"Tili luotu käyttäjälle {form.first_and_lastname.data}! Voit nyt kirjautua sisään.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Rekisteröidy", form=form)


@app.route("/kirjaudu", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('account'))
        else:
            flash("Kirjautuminen epäonnistunut. Tarkista sähköpostiosoite sekä salasana.", "danger")
    return render_template("login.html", title="Kirjaudu", form=form)


@app.route("/kirjaudu_ulos")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profiili")
@login_required
def account():
    return render_template("account.html", title="Profiili")

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Salasanan vaihto pyyntö', sender='mngr.integraatio@gmail.com', recipients=[user.email])
    msg.body = f'''Pääset vaihtamaan salasanasi tästä linkistä:
{url_for('reset_token', token= token, _external= True)}
    
Jos et tehnyt tätä pyyntöä, tästä sähköpostista ei tarvitse välittää. 
'''
    mail.send(msg)

@app.route("/vaihda_salasana", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Sähköposti on lähetetty, joka sisältää ohjeet salasanan vaihtamiseen.', 'info')
        return redirect(url_for('login'))
    return render_template("reset_request.html", title="Vaihda Salasana", form=form)


@app.route("/vaihda_salasana/<token>", methods=["GET", "POST"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Salasanan vaihdon aikaikkuna umpeutunut', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        with app.app_context():
            db.session.commit()
        flash(f"Salasanasi on päivitetty! Voit nyt kirjautua sisään.", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Vaihda Salasana", form=form)
