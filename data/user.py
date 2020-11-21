import mongoengine

class User(mongoengine.Document):
    _id                 = mongoengine.IntField(required=True, unique=True, primary_key=True)
    is_clem             = mongoengine.BooleanField(default=False)
    is_xp_frozen        = mongoengine.BooleanField(default=False)
    was_warn_kicked     = mongoengine.BooleanField(default=False)
    xp                  = mongoengine.IntField(default=0)
    level               = mongoengine.IntField(default=0)
    offline_report_ping = mongoengine.BooleanField(default=False)

    meta {
        'db_alias': 'core',
        'collection': 'users'
    }