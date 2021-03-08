import django.forms as forms
from .models import Player, Tradeoff
from django.forms import inlineformset_factory
import logging


class TradeoffForm(forms.ModelForm):
    class Meta:
        model = Tradeoff
        fields = ['answer']


TradeoffFormset = inlineformset_factory(Player, Tradeoff,
                                        fields=['answer'],
                                        extra=0,
                                        can_delete=False,
                                        )
