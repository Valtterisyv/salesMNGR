from salesmngr import db, app, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_and_lastname = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.first_and_lastname}', '{self.email}')"


class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    calls = db.Column(db.Integer, nullable=False)
    required_calls = db.Column(db.Integer, nullable=False)
    offers = db.Column(db.Integer, nullable=False)
    required_offers = db.Column(db.Integer, nullable=False)
    sales = db.Column(db.Float, nullable=False)
    required_sales = db.Column(db.Float, nullable=False)
    mngr_bot_text = db.Column(db.String(250), nullable=False)
    offer_to_sale = db.Column(db.Integer, nullable=False)
    call_to_offer = db.Column(db.Integer, nullable=False)
    ch_offer_to_sale = db.Column(db.Integer, nullable=False)
    ch_call_to_offer = db.Column(db.Integer, nullable=False)
    to_bonus = db.Column(db.Float, nullable=False)
    coming_sales = db.Column(db.Float, nullable=False)
    two_week_calls = db.Column(db.Integer, nullable=False)
    required_two_week_calls = db.Column(db.Integer, nullable=False)
    good_days = db.Column(db.Integer, nullable=True)
    bad_days = db.Column(db.Integer, nullable=True)
    good_percent = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"User_data('{self.calls}', '{self.required_calls}', '{self.offers}', '{self.required_offers}', '{self.sales}', '{self.required_sales}', '{self.mngr_bot_text}', '{self.offer_to_sale}', '{self.call_to_offer}', '{self.to_bonus}', '{self.coming_sales}', '{self.two_week_calls}', '{self.required_two_week_calls}')"


with app.app_context():
    db.create_all()
