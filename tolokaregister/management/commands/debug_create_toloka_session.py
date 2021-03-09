from django.core.management.base import BaseCommand
import logging
from otree.models import Session, Participant
from tolokaregister.toloka import TolokaClient
from otree.session import create_session
import random

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'For testing purposes only! Creating session to link to toloka and test the functionality'

    def create_session(self):

        client = TolokaClient(sandbox=False)
        if client.pool_exists(self.pool_id):
            logger.info(f'Pool {self.pool_id} exists')
        else:
            logger.warning(f'Pool {self.pool_id} *DOES NOT* exist')
            return
        pool_data = client.get_assignments(self.pool_id)
        items = pool_data.get('items', [])
        s = create_session('corr', num_participants=len(items))
        logger.info(f'Session "{s.code}" was created for {len(items)} participants')
        ps = s.get_participants()
        for i, p in enumerate(ps):
            p.label = items[i].get('id')
            p.payoff = random.randint(1, 10)/100
            print(f'gonna pay them {p.payoff}')
        Participant.objects.bulk_update(ps, fields=['label', 'payoff'])

        if s.vars.get('toloka_pool_id'):
            logger.warning('Session was already linked. Going to override')
        s.vars['toloka_pool_id'] = self.pool_id
        s.save()
        logger.info(f'Session "{s.code}" and pool "{self.pool_id}" are linked now.')

    def add_arguments(self, parser):
        parser.add_argument('pool_id', help='toloka pool id', type=str)

    def handle(self, pool_id, *args, **options):
        logger.info(
            f'this will create the session  for specific toloka pool {pool_id}. FOR DEBUG PURPOSES ONLY')
        self.pool_id = pool_id
        self.create_session()
