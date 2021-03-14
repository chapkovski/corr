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
import logging

logger = logging.getLogger(__name__)
author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Single donation app, that will later on merges into larger corrreg.
"""


def to_cents(v):
    # todo do something smart here but not now
    return f'{int(v * 100)} центов'


class Constants(BaseConstants):
    name_in_url = 'singledonat'
    max_cq_errors = 2
    players_per_group = None
    num_rounds = 1

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

    CQ2_CHOICES = [
        (1, 'Я не смогу никак узнать действительно ли деньги были переведены в благотворительный фонд.'),
        (2,
         'Я смогу узнать о том действительно ли деньги были переведены в благотворительный фонд  сразу после того, как отправлю задание в Толоке.'),
        (3,
         'Я смогу узнать действительно ли деньги были переведены в благотворительный фонд, когда исследование завершится и исследователи пришлют мне ссылку на отсканированную квитанцию.'),

    ]
    CQ3_CHOICES = [
        (1,
         'От моих действий не зависит финальная сумма, которую исследователи из Высшей школы экономики переведут в благотворительный фонд.'),
        (2,
         'В зависимости от того, что я решу, финальная сумма, которую исследователи из Высшей школы экономики переведут в  благотворительный фонд, может быть изменена.'),
        (3,
         'Будет ли мое решение влиять на то, какая сумма будет переведена в благотворительный фонд будет решено самими исследователями. '),

    ]


class Subsession(BaseSubsession):
    average_donation = models.FloatField()
    total_donation = models.FloatField()

    def nko_codes(self):
        ps = [p.participant.code for p in self.get_players() if p.donation]
        return ' '.join(ps)

    @property
    def donation_message(self):
        yes_ego = to_cents(self.session.config.get('yes_ego'))
        yes_nko = to_cents(self.session.config.get('yes_nko'))
        return mark_safe(
            f"Получить бонус <b>{yes_ego}</b> . "
            f"В этом случае мы увеличим сумму пожертвований в благотворительный фонд "
            f"на <b>{yes_nko}</b>.")

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
        logger.info(f'Payoffs for session {self.session.code} are set.')


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    donation = models.BooleanField()
    nko_payoff = models.CurrencyField(initial=0)
    direct_payoff = models.CurrencyField(initial=0)
    belief_payoff = models.CurrencyField(initial=0)
    belief = models.IntegerField(min=0, max=100)
    cq1 = models.IntegerField(label=Constants.cq_label, widget=widgets.RadioSelect)

    def cq1_choices(self):
        yes_ego = self.session.config.get('yes_ego')
        no_ego = self.session.config.get('no_ego')
        CQ1_CHOICES = [
            (1, f'Если я выберу “Получить бонус {to_cents(yes_ego)}”, я не получу своей оплаты за участие'),
            (2, f'Если я выберу “Получить бонус {to_cents(no_ego)}”, я не получу своей оплаты за участие'),
            (3, 'Вне зависимости от моего решения я получу оплату за участие'),

        ]
        return CQ1_CHOICES

    cq2 = models.IntegerField(label=Constants.cq_label, choices=Constants.CQ2_CHOICES, widget=widgets.RadioSelect)
    cq3 = models.IntegerField(label=Constants.cq_label, choices=Constants.CQ3_CHOICES, widget=widgets.RadioSelect)
    cq_counter = models.IntegerField(initial=0)
    attention_counter = models.IntegerField(initial=0)
    attention = models.BooleanField()
    attention_agreement = models.BooleanField(widget=widgets.CheckboxInput)
    useragent_is_mobile = models.BooleanField()
    useragent_is_bot = models.BooleanField()
    useragent_browser_family = models.StringField()
    useragent_os_family = models.StringField()
    useragent_device_family = models.StringField()

    def donation_choices(self):
        a = self.subsession.donation_message
        no_ego = to_cents(self.session.config.get('no_ego'))
        no_nko_val = self.session.config.get('no_nko')
        if not no_nko_val:
            no_nko_str = "мы <b>НЕ</b> увеличим сумму пожертвований в благотворительный фонд"
        else:
            no_nko_str = f"мы увеличим сумму пожертвований в благотворительный фонд  на <b>{to_cents(no_nko_val)}</b>"
        b = mark_safe(
            f"Получить бонус <b>{no_ego}</b>. В этом случае {no_nko_str}.")
        l = [(True, a), (False, b)]
        random.shuffle(l)
        return l

    def set_direct_payoff(self):
        c = self.session.config
        if self.donation is not None:
            if self.donation:
                self.direct_payoff = c.get('yes_ego')
                self.nko_payoff = c.get('yes_nko')
            else:
                self.direct_payoff = c.get('no_ego')
                self.nko_payoff = c.get('no_nko')

    def set_belief_payoff(self):
        if abs(self.belief - self.subsession.average_donation) <= Constants.precise_margin:
            self.belief_payoff = Constants.precise_belief_payoff
        elif abs(self.belief - self.subsession.average_donation) <= Constants.circa_margin:

            self.belief_payoff = Constants.circa_belief_payoff

    def set_final_payoff(self):
        self.payoff = self.direct_payoff + self.belief_payoff
