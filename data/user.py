import mongoengine

class User(mongoengine.Document):
    _id                 = mongoengine.IntField(required=True)
    is_clem             = mongoengine.BooleanField(default=False, required=True)
    is_xp_frozen        = mongoengine.BooleanField(default=False, required=True)
    was_warn_kicked     = mongoengine.BooleanField(default=False, required=True)
    xp                  = mongoengine.IntField(default=0, required=True)
    level               = mongoengine.IntField(default=0, required=True)
    offline_report_ping = mongoengine.BooleanField(default=False, required=True)
    warn_points         = mongoengine.IntField(default=0, required=True)
    
    meta = {
        'db_alias': 'core',
        'collection': 'users'
    }