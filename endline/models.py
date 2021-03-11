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
import random

author = 'Philip Chapkovski, HSE-Moscow'

doc = """
Endline for corrreg
"""


class Constants(BaseConstants):
    name_in_url = 'endline'
    players_per_group = None
    num_rounds = 1
    chronic_choices_texts = ['никогда', 'почти никогда', 'иногда', 'довольно часто', 'часто']
    CHRONIC_CHOICES = [(i, j) for i, j in enumerate(chronic_choices_texts)]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(min=18, max=101, label=' Сколько Вам лет?')
    gender = models.StringField(label='Укажите Ваш пол?',
                                widget=widgets.RadioSelect,
                                choices=['Мужской', 'Женский'],
                                )
    education = models.StringField(label='Какой у вас уровень образования?',
                                   choices=['Неполное среднее (8-9 классов)', 'Среднее общее (10-11 классов)',
                                            'Среднее профессиональное (училище)',
                                            'Среднее специальное - техническое (техникум)',
                                            'Неполное высшее образование (не менее 3-х лет обучения)',
                                            'Высшее образование', 'Аспирантура'],
                                   widget=widgets.RadioSelect
                                   )
    education1 = models.StringField(
        label='В случае если у Вас имеется высшее образование, отметьте, пожалуйста, по какой специальности (направлению подготовки) Вы обучались?',
        choices=['экономика или бизнес', 'математика или инженерия', 'естественные науки',
                 'медицина', 'общественные науки', 'гуманитарные науки', 'искусство',
                 'другое'],
        blank=True
    )
    birth = models.StringField(label='В какой стране и каком городе Вы родились?')
    occupation = models.StringField(
        label='Пожалуйста, укажите, по какой профессии/специальности вы работаете. Если Вы не работаете или самозаняты, то тоже укажите это')

    game = models.StringField(
        label='Если я вовлечен в какую-либо игру, мне всегда хочется победить. Насколько Вы согласны с данным утверждением? '
              '(Oтвет: шкала от 1 до 5, где 1 – полностью не согласен, а 5 – полностью согласен)',
        choices=['1', '2', '3', '4', '5'],
        widget=widgets.RadioSelectHorizontal)
    money = models.StringField(
        label='Какое из описаний точнее всего соответствует материальному положению Вашей семьи?',
        choices=['денег не хватает даже на питание',
                 'на питание денег хватает, но не хватает на покупку одежды и обуви',
                 'на покупку одежды и обуви денег хватает, но не хватает на покупку крупной бытовой техники',
                 'денег хватает на покупку крупной бытовой техники, но мы не можем купить новую машину',
                 'на новую машину денег хватает, но мы не можем позволить себе покупку  квартиры или дома',
                 'материальных затруднений не испытываем, при необходимости могли бы приобрести квартиру, дом',
                 'затрудняюсь ответить'],
        widget=widgets.RadioSelect)

    general_comments = models.LongStringField(blank=True,
                                              label="")



    def set_acceptable_for_toloka(self):
        self.participant.vars['toloka_acceptable'] = True
