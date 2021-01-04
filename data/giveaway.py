import mongoengine

class Giveaway(mongoengine.Document):
    _id              = mongoengine.IntField(required=True)
    is_ended         = mongoengine.BooleanField(default=False)
    end_time         = mongoengine.DateTimeField()
    channel          = mongoengine.IntField()
    name             = mongoengine.StringField()
    entries          = mongoengine.ListField(mongoengine.IntField(), default=[])
    previous_winners = mongoengine.ListField(mongoengine.IntField(), default=[])
    winners          = mongoengine.IntField()

    meta = {
        'db_alias': 'core',
        'collection': 'giveaways'
    }