from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class SocialEconomic(Page):
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'education', 'education1',  'occupation', 'birth', 'game',
        'money',

    ]


class ChronicStress(Page):
    form_model = 'player'
    form_fields = ['chronic1', 'chronic2', 'chronic3', 'chronic4', 'chronic5', 'chronic6', 'chronic7',
                   'chronic8', 'chronic9', 'chronic10']

    def before_next_page(self):
        self.player.set_chronic_index()
        self.player.set_payoff()
        self.player.set_acceptable_for_toloka()
class Last(Page):
    pass

page_sequence = [
    SocialEconomic,
    ChronicStress,
    Last
]
