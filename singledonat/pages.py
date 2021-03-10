from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Intro(Page):
    pass


class NKOExplained(Page):
    pass


class Instructions(Page):
    pass


class CQ(Page):
    form_model = 'player'
    form_fields = ['cq1', 'cq2', 'cq3']
    def error_message(self, values):
        for k,v in values.items():
            if v != Constants.correct_answers[k]:
                self.player.cq_counter+=1
                return 'Пожалуйста, проверьте правильность ваших ответов!'

class Decision(Page):
    form_model = 'player'
    form_fields = ['donation']


class BeliefExplained(Page):
    pass


class Belief(Page):
    form_model = 'player'
    form_fields = ['belief']


class EndlineAnnounced(Page):
    pass


page_sequence = [
    # Intro,
    # NKOExplained,
    # Instructions,
    # CQ,
    Decision,
    # BeliefExplained,
    Belief,
    # EndlineAnnounced
]
