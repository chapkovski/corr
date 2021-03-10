import logging
from tolokaregister.models import UpdSession
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'accepting a bunch of toloka submissions based on their statuses; requires session code'

    def add_arguments(self, parser):
        parser.add_argument('session_code', help='toloka session code ', type=str)

    def get_session(self):
        try:
            s = UpdSession.objects.get(code=self.session_code)
        except UpdSession.DoesNotExist:
            logger.warning(f'Session {self.session_code} is not found')
            return
        return s

    def handle(self, session_code, *args, **options):
        logger.info(f'This command will accept all the acceptable toloka submissions')
        self.session_code = session_code
        self.session = self.get_session()
        if self.session:
            self.session.accept_toloka(request_linkage=True)
