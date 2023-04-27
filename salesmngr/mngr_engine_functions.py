import math


class MngrFunctions:
    def __init__(self, my_activities_day, my_offers_day, my_sales_month, my_offers_year, my_sales_year_nr,
                 required_activities_day, required_offers_day, required_sales_month, bonus_line, bonus_gap,
                 my_activities_year, my_active_offers, my_sales_six_m_avg):
        self.cok_ook_sok = self.cok_ook_sok(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cno_ook_sok = self.cno_ook_sok(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cno_ono_sok = self.cno_ono_sok(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cno_ono_sno = self.cno_ono_sno(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cok_ook_sno = self.cok_ook_sno(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cok_ono_sno = self.cok_ono_sno(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cok_ono_sok = self.cok_ono_sok(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.cno_ook_sno = self.cno_ook_sno(my_activities_day, my_offers_day, my_sales_month, required_activities_day,
                                            required_offers_day, required_sales_month)
        self.os_hit_rate = self.os_hit_rate(my_offers_year, my_sales_year_nr)
        self.co_hit_rate = self.co_hit_rate(my_activities_year, my_offers_year)
        self.to_next_bonus = self.to_next_bonus(my_sales_month, bonus_line, bonus_gap)
        self.coming_sales = self.coming_sales(my_active_offers, my_sales_six_m_avg)
        self.required_two_week_running_calls = self.required_two_week_running_calls(self.co_hit_rate, self.os_hit_rate,
                                                                                    my_sales_six_m_avg,
                                                                                    required_sales_month)
        self.required_daily_calls = self.required_daily_calls(self.co_hit_rate, self.os_hit_rate, my_sales_six_m_avg,
                                                              required_sales_month)
        self.required_two_week_running_offers = self.required_two_week_running_offers(self.os_hit_rate,
                                                                                      my_sales_six_m_avg,
                                                                                      required_sales_month)

    def cok_ook_sok(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day >= required_activities_day and offers_day >= required_offers_day and sales >= required_sales_month:
            return True

    def cno_ook_sok(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day < required_activities_day and offers_day >= required_offers_day and sales >= required_sales_month:
            return True

    def cno_ono_sok(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day < required_activities_day and offers_day < required_offers_day and sales >= required_sales_month:
            return True

    def cno_ono_sno(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day < required_activities_day and offers_day < required_offers_day and sales < required_sales_month:
            return True

    def cok_ook_sno(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day >= required_activities_day and offers_day >= required_offers_day and sales < required_sales_month:
            return True

    def cok_ono_sno(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day >= required_activities_day and offers_day < required_offers_day and sales < required_sales_month:
            return True

    def cok_ono_sok(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day >= required_activities_day and offers_day < required_offers_day and sales >= required_sales_month:
            return True

    def cno_ook_sno(self, activities_day, offers_day, sales, required_activities_day, required_offers_day,
                    required_sales_month) -> bool:
        if activities_day < required_activities_day and offers_day >= required_offers_day and sales < required_sales_month:
            return True

    def os_hit_rate(self, offers, sales_nr) -> int:
        hit_rate = round(offers / sales_nr)
        return hit_rate

    def co_hit_rate(self, activities, offers):
        hit_rate = round(activities / offers)
        return hit_rate

    def to_next_bonus(self, sales_month, bonus_line, bonus_gap) -> float:
        bonus = bonus_line
        if sales_month < bonus:
            amount = bonus - sales_month
            return amount
        while sales_month > bonus:
            bonus += bonus_gap
        amount = bonus - sales_month
        return amount

    def coming_sales(self, my_active_offers, ch_avg_price):
        sales = int(my_active_offers / self.os_hit_rate)
        result = sales * ch_avg_price
        return result

    def required_two_week_running_calls(self, co_hit_rate, os_hit_rate, my_sales_six_m_avg, required_sales_month):
        sales_num = math.ceil(required_sales_month / my_sales_six_m_avg)
        x = sales_num * os_hit_rate * co_hit_rate
        r = x / 30
        result = r * 14
        return result

    def required_daily_calls(self, co_hit_rate, os_hit_rate, my_sales_six_m_avg, required_sales_month):
        sales_num = math.ceil(required_sales_month / my_sales_six_m_avg)
        x = sales_num * os_hit_rate * co_hit_rate
        r = math.ceil(x / 21)
        return r

    def required_two_week_running_offers(self, os_hit_rate, my_sales_six_m_avg, required_sales_month):
        sales_num = math.ceil(required_sales_month / my_sales_six_m_avg)
        x = (sales_num / 2) * os_hit_rate
        return x
