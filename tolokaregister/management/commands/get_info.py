import logging
from tolokaregister.models import UpdSession, StatusEnum

from django.core.management.base import BaseCommand

UPDATABLE_STATUSES = [StatusEnum.unknown,
                      StatusEnum.submitted,
                      StatusEnum.active,
                      StatusEnum.error,
                      None
                      ]
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updating info about pool assignments if the session is linked to toloka pool'

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
        logger.info(f'This command will update the info about available toloka assignments')
        self.session_code = session_code
        self.session = self.get_session()
        if self.session:
            self.session.get_or_update_info(request_linkage=True)
