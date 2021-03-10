from django.core.management.base import BaseCommand
import logging
from otree.models import Session
from singledonat.models import Subsession

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Set payoffs in subsession'

    def process_single_session(self):
        try:
            s = Session.objects.get(code=self.session_code)
        except Session.DoesNotExist:
            logger.info(f'Session {self.session_code} is not found')
            return
        ss = Subsession.objects.filter(session=s)
        for i in ss:
            i.set_payoffs()

    def add_arguments(self, parser):
        parser.add_argument('session_code', help='session code to calculate payoffs', type=str)

    def handle(self, session_code, *args, **options):
        self.session_code = session_code
        self.process_single_session()
