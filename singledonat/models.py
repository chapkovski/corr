from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
import random
from django.utils.html import mark_safe

author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Single donation app, that will later on merges into larger corrreg.
"""


class Constants(BaseConstants):
    name_in_url = 'singledonat'
    players_per_group = None
    num_rounds = 1
    yes_nko = dict(ego=.10, nko=.30)
    no_nko = dict(ego=.20, nko=.0)
    precise_belief_payoff = 0.20  # for being in -5/5 margin of the average subsession belief
    circa_belief_payoff = 0.10  # for being in -10/10 margin of the average subession belief
    precise_margin = 5
    circa_margin = 10
    correct_answers = dict(
        cq1=3,
        cq2=3,
        cq3=2,
    )
    cq_label = 'Выберите истинное высказывание:'
    donation_message = mark_safe(
        "Получить бонус <b>10 центов</b> . В этом случае мы увеличим сумму пожертвований в фонд “Подари жизнь” на <b>30 центов</b>.")
    CQ1_CHOICES = [
        (1, 'Если я выберу “Получить бонус 10 центов”, я не получу своей оплаты за участие'),
        (2, 'Если я выберу “Получить бонус 20 центов”, я не получу своей оплаты за участие'),
        (3, 'Вне зависимости от моего решения я получу оплату за участие'),

    ]
    CQ2_CHOICES = [
        (1, 'Я не смогу никак узнать действительно ли деньги были переведены в фонд “Подари Жизнь”.'),
        (2,
         'Я смогу узнать о том действительно ли деньги были переведены в фонд “Подари Жизнь” сразу после того, как отправлю задание в Толоке'),
        (3,
         'Я смогу узнать действительно ли деньги были переведены в фонд “Подари Жизнь”, когда исследование завершится и исследователи пришлют мне ссылку на отсканированную квитанцию.'),

    ]
    CQ3_CHOICES = [
        (1,
         'От моих действий не зависит финальная сумма, которую исследователи из Высшей школы экономики переведут в фонд “Подари жизнь”'),
        (2,
         'В зависимости от того, что я решу, финальная сумма, которую исследователи из Высшей школы экономики переведут в фонд “Подари жизнь”, может быть изменена.'),
        (3,
         'Будет ли мое решение влиять на то, какая сумма будет переведена в фонд “Подари жизнь” будет решено самими исследователями. '),

    ]


class Subsession(BaseSubsession):
    average_donation = models.FloatField()
    total_donation = models.FloatField()

    def set_payoffs(self):
        ps = [p for p in self.get_players() if p.donation is not None]
        for p in ps:
            p.set_direct_payoff()
            p.save()
        self.average_donation = (sum([p.donation for p in ps]) / len(ps)) * 100
        self.total_donation = sum([p.nko_payoff for p in ps])
        self.save()
        for p in ps:
            p.set_belief_payoff()
            p.set_final_payoff()
            p.save()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    donation = models.BooleanField()
    nko_payoff = models.CurrencyField(initial=0)
    direct_payoff = models.CurrencyField(initial=0)
    belief_payoff = models.CurrencyField(initial=0)
    belief = models.IntegerField(min=0, max=100)
    cq1 = models.IntegerField(label=Constants.cq_label, choices=Constants.CQ1_CHOICES, widget=widgets.RadioSelect)
    cq2 = models.IntegerField(label=Constants.cq_label, choices=Constants.CQ2_CHOICES, widget=widgets.RadioSelect)
    cq3 = models.IntegerField(label=Constants.cq_label, choices=Constants.CQ3_CHOICES, widget=widgets.RadioSelect)
    cq_counter = models.IntegerField(initial=0)

    def donation_choices(self):
        a = Constants.donation_message
        b = mark_safe(
            "Получить бонус <b>20 центов</b>. В этом случае мы <b>НЕ</b> увеличим сумму пожертвований в фонд “Подари жизнь”.")
        l = [(True, a), (False, b)]
        random.shuffle(l)
        return l

    def set_direct_payoff(self):
        if self.donation is not None:
            if self.donation:
                self.direct_payoff = Constants.yes_nko.get('ego')
                self.nko_payoff = Constants.yes_nko.get('nko')
            else:
                self.direct_payoff = Constants.no_nko.get('ego')
                self.nko_payoff = Constants.no_nko.get('nko')

    def set_belief_payoff(self):
        if abs(self.belief - self.subsession.average_donation) <= Constants.precise_margin:
            self.belief_payoff = Constants.precise_belief_payoff
        elif abs(self.belief - self.subsession.average_donation) <= Constants.circa_margin:

            self.belief_payoff = Constants.circa_belief_payoff

    def set_final_payoff(self):
        self.payoff = self.direct_payoff + self.belief_payoff
