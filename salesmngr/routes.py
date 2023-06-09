from salesmngr.models import User, UserData
from flask import render_template, url_for, flash, redirect, request
from salesmngr.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, GoalsForm
from salesmngr import app, db, bcrypt, mail
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route("/")
@app.route("/home")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    return render_template("index.html")


@app.route("/about")
def about():
    return "<H1>About page</h1>"


@app.route("/rekisteröidy", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
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
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            user = UserData.query.filter_by(user=form.email.data).first()
            return redirect(url_for('account'))
        else:
            flash("Kirjautuminen epäonnistunut. Tarkista sähköpostiosoite sekä salasana.", "danger")
    return render_template("login.html", title="Kirjaudu", form=form)


@app.route("/kirjaudu_ulos")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/profiili", methods=["GET", "POST"])
@login_required
def account():
    if current_user.is_authenticated:
        user = db.session.query(UserData).filter_by(user=current_user.email).first()
        form = GoalsForm()
        if form.validate_on_submit():
            user.goal = form.goal_num.data
            db.session.commit()
            flash(f"Päivitetty tavoite on {user.goal} €! Huom. Puhelutavoite sekä tarjoustavoite päivittyy 10 minuutin sisällä.", "success")
            return redirect(url_for("account"))
        else:
            print(user)
            return render_template("account_full.html", title="Profiili", calls=user.calls,
                                   required_calls=user.required_calls, offers=user.offers,
                                   required_offers=user.required_offers,
                                   sales=user.sales, required_sales=user.required_sales,
                                   mngr_bot_text=user.mngr_bot_text,
                                   offer_to_sale=user.offer_to_sale, call_to_offer=user.call_to_offer,
                                   user=user.user, ch_offer_to_sale=user.ch_offer_to_sale,
                                   ch_call_to_offer=user.ch_call_to_offer, to_bonus=user.to_bonus,
                                   coming_sales=user.coming_sales, two_week_calls=user.two_week_calls,
                                   required_two_week_calls=user.required_two_week_calls,
                                   good_days=user.good_days,
                                   bad_days=user.bad_days,
                                   good_percent=user.good_percent,
                                   goal=user.goal,
                                   calls_to_goal=user.calls_to_goal,
                                   offers_to_goal=user.offers_to_goal,
                                   my_sales_avg=user.my_sales_avg,
                                   my_sales_3_month_avg=user.my_sales_3_month_avg,
                                   three_avg_change_front=user.three_avg_change_front,
                                   avg_change_front=user.avg_change_front,
                                   good_percent_change_front=user.good_percent_change_front,
                                   form=form)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Salasanan vaihto pyyntö', sender='mngr.integraatio@gmail.com', recipients=[user.email])
    msg.body = f'''Pääset vaihtamaan salasanasi tästä linkistä:
{url_for('reset_token', token=token, _external=True)}
    
Jos et tehnyt tätä pyyntöä, tästä sähköpostista ei tarvitse välittää. 
'''
    mail.send(msg)


@app.route("/vaihda_salasana", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('account'))
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
        return redirect(url_for('account'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Salasanan vaihdon aikaikkuna umpeutunut', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f"Salasanasi on päivitetty! Voit nyt kirjautua sisään.", "success")
        return redirect(url_for("login"))
    return render_template("reset_token.html", title="Vaihda Salasana", form=form)
