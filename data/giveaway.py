import mongoengine

class Giveaway(mongoengine.Document):
    _id             = mongoengine.IntField(required=True)
    channel         = mongoengine.IntField()
    name            = mongoengine.StringField()
    entries         = mongoengine.ListField(mongoengine.IntField())
    winners         = mongoengine.IntField()

    meta = {
        'db_alias': 'core',
        'collection': 'giveaways'
    }