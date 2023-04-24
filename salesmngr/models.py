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


# class Data(db.Model):
#    calls = int(my_activities_today),
#    required_calls = int(person_1.required_daily_calls),
#    offers = int(my_offers_two_weeks),
#    required_offers = int(person_1.required_two_week_running_offers),
#    sales = my_sales_month_3,
#    required_sales = REQUIRED_SALES_MONTH,
#    mngr_bot_text = mngr_bot,
#    offer_to_sale = person_1.os_hit_rate,
#    call_to_offer = person_1.co_hit_rate,
#    user = login_form.name.data,
#    ch_offer_to_sale = CH_OS_HIT_RATE,
#    ch_call_to_offer = CH_CO_HIT_RATE,
#    to_bonus = person_1.to_next_bonus,
#    coming_sales = person_1.coming_sales,
#    two_week_calls = my_two_week_activities,
#    required_two_week_calls = person_1.required_two_week_running_calls

with app.app_context():
    db.create_all()
