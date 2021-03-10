from django.db import models
from otree.models import Participant, Session
from enum import Enum
from .toloka import TolokaClient
import json
import logging

logger = logging.getLogger(__name__)
# Some constants - mostly temporarily
DEFAULT_BONUS_TITLE = 'Cпасибо за ваше участие!'
DEFAULT_BONUS_MESSAGE = 'Cпасибо за ваше участие! Надеемся, что вы сможете поучаствовать в других наших исследованиях'
MINIMUM_BONUS_AMOUNT = 0.01


class StatusEnum(str, Enum):
    unknown = 'UNKNOWN'
    submitted = 'SUBMITTED'
    accepted = 'ACCEPTED'
    rejected = 'REJECTED'
    active = 'ACTIVE'
    error = 'ERROR'


class UnAcceptedAnswer(Exception):
    pass


class UpdSession(Session):
    class Meta:
        proxy = True

    def is_linked(self):
        return bool(self.vars.get('toloka_pool_id'))

    def link_session(self, pool_id):

        if self.vars.get('toloka_pool_id'):
            logger.warning(f"session is already linked to pool {self.vars.get('toloka_pool_id')}")
            return
        sandbox = self.is_sandbox()
        client = TolokaClient(sandbox=sandbox)
        if client.pool_exists(pool_id):
            logger.info(f'Pool {pool_id} exists')
        else:
            logger.warning(f'Pool {pool_id} *DOES NOT* exist')
            # todo: should we raise custom exception here?
            return

        self.vars['toloka_pool_id'] = pool_id
        self.save()
        logger.info(f'Session "{self.code}" and pool "{pool_id}" are linked now.')

    def is_sandbox(self):
        return self.config.get('toloka_sandbox', False)

    def get_or_update_info(self, request_linkage=False):
        if not self.is_linked():
            if request_linkage:
                confirmation = input("session is not linked. Do you want to link it? ")
                if confirmation == 'yes':
                    pool_id = input('insert pool id: ')
                    self.link_session(pool_id)
                else:
                    return
            else:
                print(
                    'Apparently the session is not yet linked to the existing toloka pool. Do it with link_session command')
                return
        toloka_pool_id = self.vars.get('toloka_pool_id')
        client = TolokaClient(sandbox=self.is_sandbox())
        pool_data = client.get_assignments(toloka_pool_id)
        items = pool_data.get('items', [])
        for i in items:
            try:
                tp = TolokaParticipant.objects.get(assignment=i.get('id'))
                owner = tp.owner
            except TolokaParticipant.DoesNotExist:
                try:
                    owner = Participant.objects.get(label=i.get('id'), session=self)
                except Participant.DoesNotExist:
                    logger.warning(f'Participant for assignment {i.get("id")} hasnt been found')
                    continue
            tp, _ = TolokaParticipant.objects.update_or_create(owner=owner,
                                                               assignment=i.get('id'),
                                                               defaults=dict(
                                                                   status=i.get('status'),
                                                                   info=json.dumps(i),
                                                                   toloka_user_id=i.get('user_id'),
                                                                   sandbox=False
                                                               )
                                                               )
            logger.info(f'participant {tp.owner.code}: status {tp.status}; assignment: {tp.assignment}')
        return items  # we need this for acceptance

    def accept_toloka(self, request_linkage=False):
        records = self.get_or_update_info(request_linkage)
        submitted = [i for i in records if i.get('status') == StatusEnum.submitted]
        submitted_ids = [i.get('id') for i in submitted]
        acceptable = TolokaParticipant.objects.filter(assignment__in=submitted_ids)
        logger.info(f'I am planning to accept the following number of submissions: {acceptable.count()}')
        for i in acceptable:
            i.accept_assignment()


class UpdParticipant(Participant):
    class Meta:
        proxy = True

    def __str__(self):
        return self.code

    def get_tp(self):
        try:
            r = self.tolokaparticipant
            return r
        except  TolokaParticipant.DoesNotExist as e:
            return False


class TolokaParticipant(models.Model):
    """we don't need all these blank=true, only for debugging purposes so we can deal with this in admin"""
    owner = models.OneToOneField(to=UpdParticipant, on_delete=models.CASCADE,
                                 related_name='tolokaparticipant')
    status = models.CharField(max_length=1000, default=StatusEnum.unknown)
    """In info we write the whole response when we request the status"""
    info = models.TextField(null=True, blank=True)
    """The assginemnt is the only important thing here becuase it links otree and toloka together"""
    assignment = models.CharField(max_length=1000, unique=True)
    toloka_user_id = models.CharField(max_length=1000, null=True, blank=True)
    bonus_paid = models.BooleanField(null=True, blank=True)
    sandbox = models.BooleanField()

    def __str__(self):
        return f'Participant {self.owner.code}; assignment {self.assignment}'

    @property
    def payable(self):
        return self.status == StatusEnum.accepted and not self.bonus_paid

    @property
    def acceptable(self):
        """Check if assignment can be accepted. Theoretically rejected assignmentes can be accepted, but we'll
        be naive and accept only submitted assignments - everything else can be dealt with in toloka interface"""
        """Acceptability condition: under which condition we may accept the submission? In 
        previous versions we checked against the code they returned, and that created a bunch of problems because 
        they managed to type in the answer incorrectly. Right now, specifically in corrreg project I am only interested 
        that they ve reached the stage where they can be paid. For the simplicity, I'll set somewhere the participant'var
        'toloka_acceptable' to true.
        """
        acceptable = self.owner.vars.get('toloka_acceptable')
        return self.status == StatusEnum.submitted and acceptable

    def accept_assignment(self):
        """check if status is Submitted. and iif yes - send accept request to toloka, return positive response back.
        otherwise sends error=True back. use sandbox param to get info.
        Theoretically rejected assignments can be (re-) accepted, but I dont' want to deal with this mess.
        """
        if self.acceptable:
            client = TolokaClient(self.sandbox)
            # TODO error handling
            resp = client.accept_assignment(self.assignment)
            self.status = resp.status
            self.save()
            return dict(error=False, **resp)  # send toloka accept request here
        else:
            raise UnAcceptedAnswer('Answer is not marked for acceptance')

    def get_bonus_message(self):
        p = self.owner.singledonat_player.all().first()
        formatter = lambda x: f'{round(float(x), 2)} USD'
        totbonus = formatter(p.payoff)
        donationpart = formatter(p.direct_payoff)
        beliefpart = formatter(p.belief_payoff)
        msg = f'Ваш бонус составляет {totbonus} и состоит из {donationpart} за первую часть и {beliefpart} за вторую часть.' \
              f' Спасибо за участие!'
        return msg

    def pay_bonus(self):
        """iif status is accepted and bonus is paid is false then pay a bonus retrieved from bonus_to_pay"""
        # we need somehow to pay zero bonus. Let's add 0.01 for zero bonus
        if not self.bonus_paid:
            """send pay bonus request to toloka"""

            client = TolokaClient(self.sandbox)
            user_id = self.toloka_user_id
            bonus = float(self.owner.payoff_in_real_world_currency())
            if bonus == 0:
                bonus = MINIMUM_BONUS_AMOUNT
            title = DEFAULT_BONUS_TITLE
            message = DEFAULT_BONUS_MESSAGE

            resp = client.pay_bonus(user_id, bonus, title, message)
            self.bonus_paid = True
            self.save()
            return dict(error=False, **resp)
        else:
            logger.warning('Bonus already paid')
            return dict(error=True, errmsg='Bonus already paid')
