from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from .forms import TradeoffFormset

class Decision(Page):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = TradeoffFormset(instance=self.player)
        return context

    def post(self):
        self.object = self.get_object()
        self.form = self.get_form(
            data=self.request.POST, files=self.request.FILES, instance=self.object)

        formset = TradeoffFormset(self.request.POST, instance=self.player)
        context = self.get_context_data()
        context['form'] = self.form
        if not formset.is_valid():
            self.form.add_error(None, 'all fields are required!')
            return self.render_to_response(context)
        formset.save()
        return super().post()

    def before_next_page(self):
        self.player.set_payoff()




class Results(Page):
    pass


page_sequence = [Decision]
