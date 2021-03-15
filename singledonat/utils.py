from tolokaregister.models import  TolokaParticipant
def set_tp(label, player):
    """What we do here:
    1. we try to create a TP,
    2. Get his user id
    3. Assign it to player attribut toloka_user_id
    4. save

    """
    # Getting TP

    try:
        assignment = get_assignment(label)
    except AssignmentDoesNotExist:
        logger.warning(f'Assignment for label {label} is not found!')
        return

    try:
        tp = TolokaParticipant.objects.get(assignment=label)
        owner = tp.owner
    except TolokaParticipant.DoesNotExist:
        try:
            owner = Participant.objects.get(label=label)
        except Participant.DoesNotExist:
            logger.warning(f'Participant for assignment {i.get("id")} hasnt been found')
            return
    tp, _ = TolokaParticipant.objects.update_or_create(owner=owner,
                                                       assignment=label,
                                                       defaults=dict(
                                                           status=assignment.get('status'),
                                                           info=json.dumps(assignment),
                                                           toloka_user_id=assignment.get('user_id'),
                                                           sandbox=False
                                                       )
                                                       )
    logger.info(f'participant {tp.owner.code}: status {tp.status}; assignment: {tp.assignment}')

