from django.core.management.base import BaseCommand
import logging
from otree.models import Session, Participant
from tolokaregister.toloka import TolokaClient
from tolokaregister.models import UpdSession

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'It sets a session var of TolokaPoolId that links current session info ' \
                   'with Toloka pool for retrieving and updating info later'

    def process_single_session(self):
        # TODO: make sandbox based on toloka param


        try:
            s = UpdSession.objects.get(code=self.session_code)
        except Session.DoesNotExist:
            logger.info(f'Session {self.session_code} is not found')
            return
        s.link_session(self.pool_id)


    def add_arguments(self, parser):
        parser.add_argument('session_code', help='toloka session code to link to', type=str)
        parser.add_argument('pool_id', help='pool id to link to', type=str)

    def handle(self, session_code, pool_id, *args, **options):
        logger.info(f'this will link the session {session_code} with toloka pool {pool_id}')
        self.session_code = session_code
        self.pool_id = pool_id
        self.process_single_session()
