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

author = 'Philip Chapkovski'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'experimental_toloka'
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

    chronic1 = models.IntegerField(
        label='Как часто за последний месяц вы испытывали беспокойство из-за непредвиденных событий?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic2 = models.IntegerField(
        label='Как часто за последний месяц Вам казалось сложным контролировать важные события Вашей жизни?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic3 = models.IntegerField(label='Как часто за последний месяц Вы испытывали нервное напряжение или стресс?',
                                   choices=Constants.CHRONIC_CHOICES,
                                   widget=widgets.RadioSelect)
    chronic4 = models.IntegerField(
        label=' Как часто за последний месяц Вы чувствовали уверенность в том, что справитесь с решением ваших личных проблем?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic5 = models.IntegerField(
        label='Как часто за последний месяц Вы чувствовали, что все идет так, как Вы этого хотели?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic6 = models.IntegerField(
        label='Как часто за последний месяц Вы думали, что не можете справиться с тем, что вам нужно сделать?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic7 = models.IntegerField(
        label='Как часто за последний месяц Вы были в состоянии справиться с вашей раздражительностью?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic8 = models.IntegerField(label='Как часто за последний месяц Вы чувствовали, что владеете ситуацией?',
                                   choices=Constants.CHRONIC_CHOICES,
                                   widget=widgets.RadioSelect)
    chronic9 = models.IntegerField(
        label='Как часто за последний месяц Вы чувствовали раздражение из-за того, что происходящие события выходили из-под вашего контроля?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic10 = models.IntegerField(
        label='Как часто за последний месяц вам казалось, что накопившиеся трудности достигли такого предела, что Вы не могли их контролировать?',
        choices=Constants.CHRONIC_CHOICES,
        widget=widgets.RadioSelect)
    chronic_index = models.IntegerField()

    def set_chronic_index(self):
        inversed = [4, 5, 7, 8]
        fields = [f'chronic{i}' for i in range(1, 11)]
        result = []
        for i, j in enumerate(fields):
            v = getattr(self, j)
            if i in inversed:
                v = 4 - v
            result.append(v)
        self.chronic_index = sum(result)

    def set_payoff(self):
        self.payoff = random.randint(1, 10)
    def set_acceptable_for_toloka(self):
        self.participant.vars['toloka_acceptable'] = True