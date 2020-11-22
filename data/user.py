import mongoengine

class User(mongoengine.Document):
    _id                 = mongoengine.IntField(required=True)
    is_clem             = mongoengine.BooleanField(default=lambda:False)
    is_xp_frozen        = mongoengine.BooleanField(default=lambda:False)
    was_warn_kicked     = mongoengine.BooleanField(default=lambda:False)
    xp                  = mongoengine.IntField(default=lambda:0)
    level               = mongoengine.IntField(default=lambda:0)
    offline_report_ping = mongoengine.BooleanField(default=lambda:False)
    warn_points = mongoengine.IntField(default=0)
    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }