from django.core.management.base import BaseCommand
import logging
from otree.models import Session, Participant
from tolokaregister.toloka import TolokaClient

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    command_desc = 'It sets a session var of TolokaPoolId that links current session info ' \
                   'with Toloka pool for retrieving and updating info later'

    def process_single_session(self):
        # TODO: make sandbox based on toloka param
        client = TolokaClient(sandbox=False)
        if client.pool_exists(self.pool_id):
            logger.info(f'Pool {self.pool_id} exists')
        else:
            logger.warning(f'Pool {self.pool_id} *DOES NOT* exist')
            return

        try:
            s = Session.objects.get(code=self.session_code)
        except Session.DoesNotExist:
            logger.info(f'Session {self.session_code} is not found')
            return
        # TODO: do we need this check? with the link command we can link any session actually.
        # if not s.config.get('toloka'):
        #     logger.info(f'Session {code} is not toloka session')
        #     return

        if s.vars.get('toloka_pool_id'):
            logger.warning('Session was already linked. Going to override')
        s.vars['toloka_pool_id'] = self.pool_id
        s.save()
        logger.info(f'Session "{s.code}" and pool "{self.pool_id}" are linked now.')

    def add_arguments(self, parser):
        parser.add_argument('session_code', help='toloka session code to link to', type=str)
        parser.add_argument('pool_id', help='pool id to link to', type=str)

    def handle(self, session_code, pool_id, *args, **options):
        logger.info(f'this will link the session {session_code} with toloka pool {pool_id}')
        self.session_code = session_code
        self.pool_id = pool_id
        self.process_single_session()
