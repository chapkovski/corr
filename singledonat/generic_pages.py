from otree.api import Currency as c, currency_range
from ._builtin import Page as oTreePage, WaitPage
from .models import Constants


class Page(oTreePage):
    def is_displayed(self):
        return self.player.attention and self.player.cq_counter <= Constants.max_cq_errors
