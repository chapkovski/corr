import logging
from tolokaregister.models import TolokaParticipant, StatusEnum, UnAcceptedAnswer
from ._uni_toloka_command import TolokaCommand

logger = logging.getLogger(__name__)


class Command(TolokaCommand):
    command_desc = 'accepting'

    def do_over_single(self, p, sandbox=False):
        try:
            tp = TolokaParticipant.objects.get(owner=p)
        except TolokaParticipant.DoesNotExist:
            logger.info(f'No status known for participant {p.code}')
            return
        if tp.status != StatusEnum.submitted:
            logger.info(f'Cant accept assignment {tp.assignment} for user {p.code}. Current status is {tp.status}')
            return

        try:
            tp.accept_assignment()
        except UnAcceptedAnswer:
            logger.warning(f'Submission failed. Current user status is {tp.status}. User {p.code},'
                        f' assignment {tp.assignment}')
        else:
            logger.info(f'User {p.code} is accepted')
