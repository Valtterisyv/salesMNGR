from salesmngr.mngr_engine_functions import MngrFunctions
from salesmngr.models import UserData
from salesmngr import app, db
import os
import random
import pandas as pd
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse



CH_AVG_PRICE = 5203  # tämä päivitetään, kun saadaan aikaikkunat kuntoon tietojen noutamisessa
CH_OS_HIT_RATE = 18  # tämä päivitetään, kun saadaan aikaikkunat kuntoon tietojen noutamisessa
CH_CO_HIT_RATE = 13  # tämä päivitetään, kun saadaan aikaikkunat kuntoon tietojen noutamisessa

REQUIRED_ACTIVITIES_DAY = 50
REQUIRED_OFFERS_DAY = 4
REQUIRED_SALES_MONTH = 15000

BONUS_LINE = 20000
BONUS_GAP = 10000
BONUS_1 = 400
BONUS_2 = 600
BONUS_3 = 1000

myynti_tavoite = REQUIRED_SALES_MONTH * 2

AMBER = "#FFCE66"
ORANGE = "#F9AB40"
MINT = "#A9E5D5"
DARK_BLUE = "#44455B"
RED = "#D0312D"

# Time
now = datetime.now().date()

time_now = now.strftime("%H"":""%M")

date_now = int(now.strftime("%d"))

weekday_now = now.strftime("%a")

year_ago_date = now - timedelta(days=365)

six_months_ago_date = now - timedelta(days=182)

month_num_now = now.month

week_num_now = now.isocalendar().week

token_endpoint = "https://contenthouse.crmservice.fi/api/v1/auth"

body = {
    "username": os.environ.get("CRM_USERNAME"),
    "password": os.environ.get("CRM_PASSWORD"),
}

r = requests.post(url=token_endpoint, json=body)

TOKEN = r.text
TOKEN = TOKEN.strip('"')

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

USER_NAME_LIST = []
USER_ID_LIST = []
USER_NAME_LIST_EXCLUDE = []
endpoint_1 = 'https://contenthouse.crmservice.fi/api/v1/users?page[size]=2000&page[number]=1'
r_2 = requests.get(url=endpoint_1, headers=headers)
data = r_2.json()

for p in data["data"]:
    if p["attributes"]["last_name"] != None:
        USER_NAME_LIST.append(p["attributes"]["email"])
for p in data["data"]:
    USER_ID_LIST.append(p["id"])

for name in USER_NAME_LIST:
    if name in USER_NAME_LIST_EXCLUDE:
        pass
    else:
        user_name = name
        name_index = USER_NAME_LIST.index(user_name)
        user_id = USER_ID_LIST[name_index]

        try:
            # QUOTES
            endpoint_2 = f'https://contenthouse.crmservice.fi/api/v1/quotes?page[size]=3000&page[number]=1&filter=[%7B"owner_id":"{user_id}"%7D]'

            r_2 = requests.get(url=endpoint_2, headers=headers)
            data = r_2.json()

            offers_pvm_list = []
            active_offers_pvm_list = []
            sales_pvm_list = []
            sales_list = []
            for p in data["data"]:
                if p["attributes"]["cf_tarjouksen_pvm"] != None:
                    offers_pvm_list.append(p["attributes"]["cf_tarjouksen_pvm"])

            for p in data["data"]:
                if p["attributes"]["stage"] == "Tarjous" or p["attributes"]["stage"] == "Tarjous_2":
                    active_offers_pvm_list.append(p["attributes"]["cf_tarjouksen_pvm"])
            my_active_offers = len(active_offers_pvm_list)

            for p in data["data"]:
                if p["attributes"]["cf_muokattu"] != None:
                    if p["attributes"]["stage"] == "Voitettu":
                        sales_pvm_list.append(p["attributes"]["cf_muokattu"])
                        sales_list.append(p["attributes"]["cf_muokattu"])
                        sales_list.append(p["attributes"]["sub_total"])

            six_m_offers_list = [item for item in offers_pvm_list if
                                 datetime.strftime(pd.to_datetime(item), '%Y-%m-%d') > datetime.strftime(
                                     six_months_ago_date, '%Y-%m-%d')]
            my_offers_six_month = len(six_m_offers_list)

            m_offers_list = [item for item in six_m_offers_list if pd.to_datetime(item).month == month_num_now]
            my_offers_month = len(m_offers_list)

            six_m_sales_list = [item for item in sales_pvm_list if
                                datetime.strftime(pd.to_datetime(item), '%Y-%m-%d') > datetime.strftime(
                                    six_months_ago_date, '%Y-%m-%d')]
            my_sales_six_month = len(six_m_sales_list)

            my_sales_six_month_2 = []
            my_sales_six_month_for_iteration = []
            for num in range(0, len(sales_list), 2):
                if datetime.strftime(pd.to_datetime(sales_list[num]), '%Y-%m-%d') > datetime.strftime(
                        six_months_ago_date, '%Y-%m-%d'):
                    my_sales_six_month_2.append(float(sales_list[num + 1]))
                    my_sales_six_month_for_iteration.append(sales_list[num])
                    my_sales_six_month_for_iteration.append(float(sales_list[num + 1]))
            my_sales_six_month_3 = sum(my_sales_six_month_2)

            m_sales_list = [item for item in six_m_sales_list if pd.to_datetime(item).month == month_num_now]
            my_sales_month = len(m_sales_list)

            my_sales_month_2 = []
            for num in range(0, len(my_sales_six_month_for_iteration), 2):
                if pd.to_datetime(my_sales_six_month_for_iteration[num]).date() > now - timedelta(days=30):
                    my_sales_month_2.append(float(my_sales_six_month_for_iteration[num + 1]))
            my_sales_month_3 = sum(my_sales_month_2)

            today_offers_list = [item for item in six_m_offers_list if
                                 datetime.strftime(pd.to_datetime(item), '%Y-%m-%d') == datetime.strftime(now,
                                                                                                          '%Y-%m-%d')]
            my_offers_day = len(today_offers_list)

            current_two_week_offers_list = [item for item in six_m_offers_list if
                                            datetime.date(pd.to_datetime(
                                                item)).isocalendar().week == week_num_now or datetime.date(
                                                pd.to_datetime(item)).isocalendar().week == (week_num_now - 1)]
            my_offers_two_weeks = len(current_two_week_offers_list)

            current_week_sales_list = [item for item in six_m_sales_list if
                                       datetime.date(pd.to_datetime(item)).isocalendar().week == week_num_now]
            my_sales_week = len(current_week_sales_list)

            # ACTIVITIES

            endpoint_2 = f'https://contenthouse.crmservice.fi/api/v1/activities?page[size]=10000&page[number]=1&filter=[%7B"owner_id":"{user_id}"%7D]&fields[activities]=activity_type,updated_at'

            r_2 = requests.get(url=endpoint_2, headers=headers)
            data = r_2.json()

            activities_pvm_list = []
            new_activities_pvm_list = []
            activities_not_include_ev_list = []
            new_activities_not_include_ev_list = []

            for p in data["data"]:
                if p["attributes"]["activity_type"] == "Soitto" or p["attributes"][
                    "activity_type"] == "Ei vastannut" or p["attributes"][
                    "activity_type"] == "Suorapuhelu - hävitty" or p["attributes"][
                    "activity_type"] == "Follow-up":
                    activities_pvm_list.append(p["attributes"]["updated_at"])

            for p in data["data"]:
                if p["attributes"]["activity_type"] == "Soitto" or p["attributes"][
                    "activity_type"] == "Suorapuhelu - hävitty" or p["attributes"][
                    "activity_type"] == "Follow-up":
                    activities_not_include_ev_list.append(p["attributes"]["updated_at"])

            for item in activities_pvm_list:
                new_item = str(item[:10])
                new_activities_pvm_list.append(new_item)

            for item in activities_not_include_ev_list:
                new_item = str(item[:10])
                new_activities_not_include_ev_list.append(new_item)

            six_m_activities_list = [item for item in new_activities_pvm_list if
                                     parse(item) > parse(str(six_months_ago_date))]
            my_activities_six_month = len(six_m_activities_list)

            month_activities_list = [item for item in new_activities_pvm_list if
                                     pd.to_datetime(item).month == month_num_now]
            my_activities_current_month = len(month_activities_list)

            six_m_activities_n_ev_list = [item for item in new_activities_not_include_ev_list if
                                          parse(item) > parse(str(six_months_ago_date))]
            my_activities_not_include_ev_six_month = len(six_m_activities_n_ev_list)

            today_activities_list = [item for item in new_activities_pvm_list if
                                     parse(item) == parse(str(now)[:10])]
            my_activities_today = len(today_activities_list)

            two_week_activities_list = [item for item in new_activities_pvm_list if
                                        pd.to_datetime(item) >= datetime.today() - timedelta(days=14)]
            my_two_week_activities = len(two_week_activities_list)

            person_1 = MngrFunctions(my_activities_today, my_offers_day, my_sales_month_3, my_offers_six_month,
                                     my_sales_six_month, REQUIRED_ACTIVITIES_DAY, REQUIRED_OFFERS_DAY,
                                     REQUIRED_SALES_MONTH, BONUS_LINE, BONUS_GAP, my_activities_six_month,
                                     my_active_offers, CH_AVG_PRICE)

            if weekday_now != "Sat" or weekday_now != "Sun":
                # days 1 - 8
                if date_now < 8:
                    if time_now < "10:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Huh mikä tsemppi! Lähdetäänkö rikkomaan ennätyksiä?",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita!",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Vaikuttaa, että olet valmis rikkomaan ennätyksiä!",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita! ",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                    elif "10:00" < time_now < "14:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                    else:
                        if person_1.co_hit_rate < (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate < (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate > (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate > (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate < (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate < (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate < (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.co_hit_rate > (CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (
                                CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Uusi kuukausi lähtenyt käytniin. Eiköhän rikota ennätyksiä! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Pienillä hengitysharjoituksilla fokus uuden kuukauden tavoitteisiin! Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Nyt on vielä hyvin aikaa fokusoida tekeminen oikeisiin asioihin, jotta saadaan tehtyä erinomainen kuukausi. Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan."
                            ]
                            mngr_bot = random.choice(quotes)

                # days 8 - 21
                if 7 < date_now < 22:
                    if time_now < "10:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Huh mikä tsemppi! Lähdetäänkö rikkomaan ennätyksiä?",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita!",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Huh mikä aloitus! Lähdetäänkö rikkomaan ennätyksiä?",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita! ",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                    elif "10:00" < time_now < "14:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                    else:
                        if my_activities_current_month > 250 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Hit-ratiollasi tarvitset keskimäärin {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                f"Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa!",
                                f"Nyt vaan pidetään sama hönkä päällä! Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 250 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa, eli soittomääriä kannattaa vielä nostaa!",
                                "Soittomääriä nostamalla vaan taivas on rajana!",
                                "Lähdetään rikkomaan ennätyksiä nostamalla soittomääriä!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 250 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa, eli soittomääriä kannattaa vielä nostaa!",
                                "Soitto/kauppa hit-ration mukaan kannattaa nyt keskittyä pitsiin ja soittomääriin!!",
                                "Lähdetään rikkomaan ennätyksiä nostamalla soittomääriä!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 250 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Millanen on fiilis? Suosittelen pyytämään esihenkilöltä sparrauskaveria, niin saadaan tekeminen oikealle tasolle.",
                                f"Keskittyminen vain perusasioihin niin saadaan homma taas luistamaan!",
                                f"Vielä on hyvin aikaa polkasta isompi vaihde päälle tälle kuulle. Jos soittaminen tuntuu takkuavan, pyydä jeesiä esihenkilöltäsi."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 250 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Hyvä meno päällä! Jatketaan samaaan malliin! Näillä tarjousmäärillä ja sun hit-ratiolla sulla pitäisi olla tulossa jo {person_1.coming_sales}€ kauppaa.",
                                "Sama tsemppi päällä vaan eteenpäin! Nyt kannattaa keskittyä klousauksen hiomiseen. Apuja saat esihenkilöltäsi.",
                                f"Hyvää duunia {user_name}! Näillä tarjousmäärillä ja sun hit-ratiolla sulla pitäisi olla tulossa jo {person_1.coming_sales} € kauppaa."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 250 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Soittomäärät on kohdillaan! Hyvä meininki! Ettei mene turhaan hyviä soittoja hukkaan, suosittelen käymään pitsiä läpi esihenkilön kanssa, niin maksimoidaan tarjousmäärät!",
                                "Pitsiä kun vielä hiot hieman, että saadaan maksimoitua tarjousmäärät, niin sinun soittomäärillä päästään rikkomaan ennätyksiä! ",
                                "Keskitytään pitsiin ja sen viilaukseen, niin sinun soittomäärillä pääsee helposti bonarirajoja rikkomaan! Hyvä tsemppi päällä!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 250 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Jos hiotaan pitsiä vielä hieman, saadaan sun hit-ratiolla rikottua ennätyksiä!!",
                                "Tosi hyvä meininki! Nyt kun vielä pitsiä hieman viilataan, saadaan maksimoitua sinun potentiaalisi!! Ennätykset on tehty rikottaviksi!",
                                "Hiotaan hieman vielä pitsiä, niin sitä kauppaa tulee ovista ja ikkunoista!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 250 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Nyt vain aktivisuustasot kuntoon, niin kauppa kyllä seuraa perässä! Tarvitset {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                "Nostamalla puhelinta enemmän, maksimoit tarjousmäärät sekä tulevat kauppamäärät! Onko tarvetta klosaamisen viilaukselle?",
                                "Muista ottaa pieni taukojumppa johonkin väliin, niin jaksaa taas soittaa. Soittamalla ne kaupat tulee."
                            ]
                            mngr_bot = random.choice(quotes)

                # days 22 -
                if 21 < date_now:
                    if time_now < "10:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Huh mikä tsemppi! Lähdetäänkö rikkomaan ennätyksiä?",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita!",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                "Nopea taukojumppa ja taas langat laulamaan! Anna mennä!",
                                "Soittamalla ne tarjoukset ja kaupat tulevat. Nyt vaa fokus tekemiseen, niin hyvä tulee!",
                                "Kahvia koneeseen ja puhelinta korvalle. Kyllä ne kaupat sieltä tulevat."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Nyt on hyvä meno! Nyt vaa samalla tsempillä eteenpäin!",
                                "Huh mikä aloitus! Lähdetäänkö rikkomaan ennätyksiä?",
                                "Todella kova meininki! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                f"Hyvää duunia! Kyllä niitä tarjouksia tulee kun jaksaa soittaa. Tarvitset arviolta {person_1.co_hit_rate} keskustelua yhteen tarjoukseen.",
                                "Nyt on aktiivisuustasot hyvällä mallilla! Samlla höngällä vaan eteenpäin!",
                                f"GO {user_name}! Hyvä meno!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                f"Nyt ei kannata alkaa himmailemaan. Tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen. Nostamalla soittomääriä maksimoit kauppamäärän!",
                                "Ehkä pieni kahvitauko auttaa mieltä virkistymään. Sit vaa kovalla tsempillä puheluita! ",
                                f"Sinun hit-ratiolla tarvitset {person_1.co_hit_rate} keskustelua tarjoukseen ja {person_1.os_hit_rate} tarjousta kauppaan. Painetaan aktivisuus kattoon ja maksimoidaan kaupat!"
                            ]
                            mngr_bot = random.choice(quotes)

                    elif "10:00" < time_now < "14:00":
                        if person_1.cok_ook_sok:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sok:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sok:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ono_sno:
                            quotes = [
                                f"Vielä jaksaa painaa, niin saadaan tarvittavat soitot ja tarjoukset reppuun! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Ota nopea taukojumppa ja sit painetaan loppupäivä täysillä! Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua jotta, saat tarjouksen.",
                                f"Tarvitset vain keskimäärin {person_1.co_hit_rate} keskustelua, jotta saat tarjouksen. Eiköhän hoideta homma pakettiin nyt iltapäivän aikana!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ook_sno:
                            quotes = [
                                "Hyvä meininki! Bonarirajoja kohti!",
                                "Nyt on hyvä meno! Kannattaa takoa kun rauta on kuumaa!",
                                "Erittäin hyvä päivä ollut tähän asti! Pusketaan vielä se extra matka!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sno:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cok_ono_sok:
                            quotes = [
                                "Hyvällä tsempillä painat! Kyllä ne tarjoukset sieltä tulee!",
                                f"Soittomäärät on kohdillaan! Hyvä {user_name}! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen.",
                                f"Hyvä tsemppi ollut päällä! Jaksaa, jaksaa! Tarvitset keskimäärin {person_1.co_hit_rate} keskustelua tarjoukseen."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif person_1.cno_ook_sno:
                            quotes = [
                                "Hyvää duunia! Päivän tarjoukset jo paketissa!",
                                "Tarjouksia vaan tulee. Taotaan vielä kun rauta on kuumaa!",
                                f"Kamoon {user_name}! Hyvää duunia!"
                            ]
                            mngr_bot = random.choice(quotes)

                    else:
                        if my_activities_current_month > 600 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Nyt ei hidasteta vaan painetaan loppuun täysillä! Hieno työtä {user_name}!",
                                "Kuukausi lähenee loppuaan ja upea kuukasi ollut tähän mennessä!! Hienoa työtä!",
                                f"Nyt samalla höngällä loppuun! Seuraava bonariraja häämöttää {person_1.to_next_bonus}€:n päässä!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 600 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa, eli soittomääriä kannattaa vielä nostaa!",
                                "Soittomääriä nostamalla vaan taivas on rajana!",
                                "Nostetaan soittomäärät vielä kuntoon niin kauppaa tulee ovista ja ikkunoista!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 600 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Seuraavaan bonarirajaan on {person_1.to_next_bonus}€ matkaa, eli soittomääriä kannattaa vielä nostaa!",
                                "Soittomääriä nostamalla vaan taivas on rajana!",
                                "Nostetaan soittomäärät vielä kuntoon niin kauppaa tulee ovista ja ikkunoista!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 600 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Millanen on fiilis? Suosittelen pyytämään esihenkilöltä sparrauskaveria, niin saadaan tekeminen oikealle tasolle.",
                                f"Painetaan loppukuukausi kovaa ja pedataan jo tulevaa kuukautta samalla! Jeesiä saat aina esihenkilöltäsi.",
                                "Nyt on hyvä hetki alkaa keskittymään tekemiseen ja aktiivisuustasojen nostamiseen oikealle tasolle. Suosittelen pyytämään jeesiä esihenkilöltäsi. Tsemppiä!."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 600 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Soittomäärät ja tarjoukset ovat linjassa, mutta kauppa tuntuu taistelun takana? Meininkisi on erittäin hyvä, sinun pitää vain keskittyä klousaamiseen sekä mahdollisesti viilata tarjousmailia hieman. Esihenkilö on hyvä apu tässä.",
                                "Sama tsemppi päällä vaan eteenpäin! Nyt kannattaa keskittyä klousauksen hiomiseen. Apuja saat esihenkilöltäsi.",
                                f"Hyvää duunia {user_name}! Näillä tarjousmäärillä ja sun hit-ratiolla sulla pitäisi olla tulossa jo {person_1.coming_sales} € kauppaa."
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 600 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Soittomäärät on kohdillaan! Hyvä meininki! Ettei mene turhaan hyviä soittoja hukkaan, suosittelen käymään pitsiä läpi esihenkilön kanssa, niin maksimoidaan tarjousmäärät!",
                                "Pitsiä kun vielä hiot hieman, että saadaan maksimoitua tarjousmäärät, niin sinun soittomäärillä päästään rikkomaan ennätyksiä! ",
                                "Keskitytään pitsiin ja sen viilaukseen, niin sinun soittomäärillä pääsee helposti bonarirajoja rikkomaan! Hyvä tsemppi päällä!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month > 600 and person_1.co_hit_rate > (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate < (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                "Jos hiotaan pitsiä vielä hieman, saadaan sun hit-ratiolla rikottua ennätyksiä!!",
                                "Tosi hyvä meininki! Nyt kun vielä pitsiä hieman viilataan, saadaan maksimoitua sinun potentiaalisi!! Ennätykset on tehty rikottaviksi!",
                                "Hiotaan hieman vielä pitsiä, niin sitä kauppaa tulee ovista ja ikkunoista!"
                            ]
                            mngr_bot = random.choice(quotes)

                        elif my_activities_current_month < 600 and person_1.co_hit_rate < (
                                CH_CO_HIT_RATE * 1.3) and person_1.os_hit_rate > (CH_OS_HIT_RATE * 1.3):
                            quotes = [
                                f"Nyt vain aktivisuustasot kuntoon, niin kauppa kyllä seuraa perässä! Tarvitset {person_1.os_hit_rate} tarjousta yhteen kauppaan.",
                                "Nostamalla puhelinta enemmän, maksimoit tarjousmäärät sekä tulevat kauppamäärät! Onko tarvetta klosaamisen viilaukselle?",
                                "Muista ottaa pieni taukojumppa johonkin väliin, niin jaksaa taas soittaa. Soittamalla ne kaupat tulee."
                            ]
                            mngr_bot = random.choice(quotes)

            with app.app_context():
                user = UserData.query.filter_by(user=user_name).first()
                if user:
                    user.user = user_name
                    user.calls = my_activities_today
                    user.required_calls = person_1.required_daily_calls
                    user.offers = my_offers_two_weeks
                    user.required_offers = person_1.required_two_week_running_offers
                    user.sales = my_sales_month_3
                    user.required_sales = REQUIRED_SALES_MONTH
                    user.mngr_bot_text = mngr_bot
                    user.offer_to_sale = person_1.os_hit_rate
                    user.call_to_offer = person_1.co_hit_rate
                    user.ch_offer_to_sale = CH_OS_HIT_RATE
                    user.ch_call_to_offer = CH_CO_HIT_RATE
                    user.to_bonus = person_1.to_next_bonus
                    user.coming_sales = person_1.coming_sales
                    user.two_week_calls = my_two_week_activities
                    user.required_two_week_calls = person_1.required_two_week_running_calls

                    db.session.commit()
                else:
                    user_data = UserData(user=user_name,
                                         calls=my_activities_today,
                                         required_calls=person_1.required_daily_calls,
                                         offers=my_offers_two_weeks,
                                         required_offers=person_1.required_two_week_running_offers,
                                         sales=my_sales_month_3,
                                         required_sales=REQUIRED_SALES_MONTH,
                                         mngr_bot_text=mngr_bot,
                                         offer_to_sale=person_1.os_hit_rate,
                                         call_to_offer=person_1.co_hit_rate,
                                         ch_offer_to_sale=CH_OS_HIT_RATE,
                                         ch_call_to_offer=CH_CO_HIT_RATE,
                                         to_bonus=person_1.to_next_bonus,
                                         coming_sales=person_1.coming_sales,
                                         two_week_calls=my_two_week_activities,
                                         required_two_week_calls=person_1.required_two_week_running_calls)
                    db.session.add(user_data)
                    db.session.commit()
            print(f"{user_name} - success!")

        except:
            print(f"{user_name} - data not found")

