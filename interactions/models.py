from common.models import UserObjectRelation


class Pin(UserObjectRelation):
    user_related_name = 'pins'


class Save(UserObjectRelation):
    user_related_name = 'saves'

