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
import random, csv, json

author = 'Philipp Chapkovski'

doc = """
Regional corruption project
"""


class Constants(BaseConstants):
    name_in_url = 'corr'
    players_per_group = None
    num_rounds = 1
    with open("data/tradeoffs.csv") as csvfile:
        tradeoffs = list(csv.DictReader(csvfile))


class Subsession(BaseSubsession):
    def creating_session(self):
        ts = []

        for p in self.get_players():
            for t in Constants.tradeoffs:
                ts.append(Tradeoff(owner=p, **t))
        Tradeoff.objects.bulk_create(ts)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    selected_tradeoff = models.IntegerField()
    nko_payoff = models.CurrencyField()

    def start(self):
        self.set_random_tradeoff()

    @property
    def outcome(self):
        return Tradeoff.objects.get(pk=self.selected_tradeoff)

    def set_random_tradeoff(self):
        tradeoffs = self.tradeoffs.all()
        rtr = random.choice(tradeoffs)
        self.selected_tradeoff = rtr.pk

    def set_payoff(self):
        tradeoff = self.outcome
        if tradeoff.answer:
            self.payoff = tradeoff.b_ego
            self.nko_payoff = tradeoff.b_nko
        else:
            self.payoff = tradeoff.a_ego
            self.nko_payoff = tradeoff.a_nko


from django.db import models as djmodels


class Tradeoff(djmodels.Model):
    owner = djmodels.ForeignKey(to=Player, on_delete=djmodels.CASCADE, related_name="tradeoffs")
    a_ego = models.IntegerField()
    a_nko = models.IntegerField()
    b_ego = models.IntegerField()
    b_nko = models.IntegerField()
    answer = models.BooleanField()
