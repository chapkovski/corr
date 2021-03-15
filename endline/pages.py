from otree.api import Currency as c, currency_range
from singledonat.generic_pages import UniPage
from .models import Constants


class SocialEconomic(UniPage):
    form_model = 'player'
    form_fields = [
        'age', 'gender', 'education', 'education1', 'occupation', 'birth', 'game',
        'money',
    ]

    def before_next_page(self):
        self.player.set_acceptable_for_toloka()


class Comments(UniPage):
    form_model = 'player'
    form_fields = [
        'general_comments',
    ]


class Last(UniPage):
    pass


page_sequence = [
    SocialEconomic,
    Comments,
    Last
]
