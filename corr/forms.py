import django.forms as forms
from .models import Player, Tradeoff
from django.forms import inlineformset_factory
import logging


class TradeoffForm(forms.ModelForm):
    class Meta:
        model = Tradeoff
        fields = ['answer']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answer'].widget.attrs['required'] = True

    # def clean_answer(self):
    #     if self.cleaned_data.get('answer') not in [True, False]:
    #         raise forms.ValidationError('Необходимо ответить на все вопросы')


TradeoffFormset = inlineformset_factory(Player, Tradeoff,
                                        fields=['answer'],
                                        extra=0,
                                        can_delete=False,
                                        form=TradeoffForm
                                        )
