from tolokaregister.models import TolokaParticipant
from otree.models import Participant
import json
import logging
from tolokaregister.toloka import TolokaClient, AssignmentDoesNotExist

logger = logging.getLogger(__name__)


def set_tp(label, player):
    """What we do here:
    1. we try to create a TP,
    2. Get his user id
    3. Assign it to player attribut toloka_user_id
    4. save

    """
    if label is None:
        logger.warning(f'No label provide for participant {player.participant.code}')
        return
    sandbox = player.session.config.get('toloka_sandbox', False)
    client = TolokaClient(sandbox=sandbox)
    try:
        assignment = client.get_assignment_info(label)
    except AssignmentDoesNotExist:
        logger.warning(f'Assignment for label {label} is not found!')
        return

    try:
        p = player.participant
        tp = p.tolokaparticipant


        owner = tp.owner
    except TolokaParticipant.DoesNotExist:
        owner = player.participant

    tp, _ = TolokaParticipant.objects.update_or_create(owner=owner,
                                                       assignment=label,
                                                       defaults=dict(
                                                           status=assignment.get('status'),
                                                           info=json.dumps(assignment),
                                                           toloka_user_id=assignment.get('user_id'),
                                                           sandbox=sandbox
                                                       )
                                                       )
    logger.info(f'participant {tp.owner.code}: status {tp.status}; assignment: {tp.assignment}')
    player.toloka_user_id = assignment.get('user_id')
    player.toloka_pool_id = assignment.get('pool_id')
    player.save()
def assign_skill(self, user_id, skill_id, value, reason):
    pass
def block_user_in_project(self, user_id, project_id, session_code):
    pass