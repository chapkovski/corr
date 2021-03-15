from otree.api import Currency as c, currency_range
from ._builtin import Page as oTreePage, WaitPage
from .models import Constants


class UniPage(oTreePage):
    def get_progress(self):

        totpages = self.participant._max_page_index
        curpage = self.participant._index_in_pages
        return f"{curpage / totpages * 100:.0f}"

class Page(UniPage):

    def is_displayed(self):
        return self.player.attention and self.player.cq_counter <= Constants.max_cq_errors
