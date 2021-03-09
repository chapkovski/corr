import logging
from tolokaregister.models import TolokaParticipant, StatusEnum
from ._uni_toloka_command import TolokaCommand

UPDATABLE_STATUSES = [StatusEnum.unknown.value,
                      StatusEnum.submitted.value,
                      StatusEnum.active.value,
                      StatusEnum.error.value,
                      None
                      ]
logger = logging.getLogger(__name__)


class Command(TolokaCommand):
    command_desc = 'updating info'

    def do_over_single(self, p, sandbox=False):
        defaults = dict(assignment=p.label, sandbox=sandbox)
        tp, created = TolokaParticipant.objects.get_or_create(owner=p, defaults=defaults)
        if created:
            logger.info(f'tparticipant was created for participant {p.code}')
        else:
            logger.info(f'tparticipant {tp.id} is already created for participant {p.code}')
        if tp.status not in UPDATABLE_STATUSES:
            logger.info(f'participant {p.code} has non-updateable status {tp.status}')
            return
        tp.get_info()
        logger.info(f'participant {p.code}: status: {tp.status} ')
