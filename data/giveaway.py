import mongoengine

class Giveaway(mongoengine.Document):
    _id             = mongoengine.IntField(required=True)
    name            = mongoengine.StringField()
    entries         = mongoengine.ListField(mongoengine.IntField())

    meta = {
        'db_alias': 'core',
        'collection': 'giveaways'
    }