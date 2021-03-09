import logging
from tolokaregister.models import TolokaParticipant, StatusEnum
from otree.models import Session, Participant
from tolokaregister.toloka import TolokaClient
from django.core.management.base import BaseCommand
from pprint import pprint
import json

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
            s = Session.objects.get(code=self.session_code)
        except Session.DoesNotExist:
            logger.warning(f'Session {self.session_code} is not found')
            return
        return s

    def handle(self, session_code, *args, **options):
        logger.info(f'This command will update the info about available toloka assignments')
        self.session_code = session_code
        self.session = self.get_session()
        toloka_pool_id = self.session.vars.get('toloka_pool_id')
        if not toloka_pool_id:
            print(
                'Apparently the session is not yet linked to the existing toloka pool. Do it with link_session command')
            return
        # TODO: make sandbox based on toloka param
        client = TolokaClient(sandbox=False)
        pool_data = client.get_assignments(toloka_pool_id)
        items = pool_data.get('items', [])
        for i in items:
            try:
                tp = TolokaParticipant.objects.get(assignment=i.get('id'))
                owner = tp.owner
            except TolokaParticipant.DoesNotExist:
                try:
                    owner = Participant.objects.get(label=i.get('id'), session=self.session)
                except Participant.DoesNotExist:
                    logger.warning(f'Participant for assignment {i.get("id")} hasnt been found')
                    continue
            tp = TolokaParticipant.objects.update_or_create(owner=owner,
                                                            assignment=i.get('id'),
                                                            defaults=dict(
                                                                status=i.get('status'),
                                                                info=json.dumps(i),
                                                                toloka_user_id=i.get('user_id'),
                                                                sandbox=False
                                                            )
                                                            )
            print(tp)
