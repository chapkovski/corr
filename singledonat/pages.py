from otree.api import Currency as c, currency_range
from ._builtin import Page as oTreePage, WaitPage
from .models import Constants
from .generic_pages import Page
from django.shortcuts import redirect


class Intro(oTreePage):
    pass


class AttentionCheck(oTreePage):
    form_model = 'player'
    form_fields = ['attention_agreement', ]


class NKOExplained(oTreePage):
    form_model = 'player'
    form_fields = ['attention', ]

    def is_displayed(self):
        return self.player.attention_counter < 1

    def error_message(self, values):
        if self.player.attention_counter > 0:
            return
        if not values['attention']:
            self.player.attention_counter += 1
            return ('Вы не прошли проверку на внимание. Вам осталась одна попытка')


class AttentionFailed(Page):

    def is_displayed(self):
        return not self.player.attention or self.player.cq_counter >= Constants.max_cq_errors

    def post(self):
        return redirect('https://toloka.yandex.ru/')


class Instructions(Page):
    pass


class CQ(Page):
    form_model = 'player'
    form_fields = ['cq1', 'cq2', 'cq3']

    def error_message(self, values):

        if self.player.cq_counter >= Constants.max_cq_errors:
            return
        for k, v in values.items():
            if v != Constants.correct_answers[k]:
                self.player.cq_counter += 1
                trials = Constants.max_cq_errors - self.player.cq_counter
                return f'Пожалуйста, проверьте правильность ваших ответов! Вам осталось попыток: {trials}'


class BeforeDecision(Page):
    pass


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
    Intro,
    AttentionCheck,
    NKOExplained,
    Instructions,
    CQ,
    BeforeDecision,
    Decision,
    BeliefExplained,
    Belief,
    EndlineAnnounced,
    AttentionFailed,
]
