class Player:
    def __init__(self, name, _id, district):
        self.name = name
        self.district = district
        self.alive = True
        self.kills = 0
        self.cause_of_death = ""
        self.id = _id

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id and self.district == other.district
        return False

    def __ne__(self, other):
        return self.id != other.id or self.district != other.district 

    def __lt__(self, other):
        return (self.district, self.id) < (other.district, other.id)

    def __le__(self, other):
        return (self.district, self.id) <= (other.district, other.id)

    def __gt__(self, other):
        return (self.district, self.id) > (other.district, other.id)

    def __ge__(self, other):
        return (self.district, self.id) >= (other.district,other.id)

    def __hash__(self):
        return hash((self.district, self.id))

    @property
    def he_she(self):
        return "they"

    @property
    def he_she_cap(self):
        return "They"

    @property
    def him_her(self):
        return "their"

    @property
    def him_her_cap(self):
        return "Their"

    @property
    def himself_herself(self):
       return "themself"

    @property
    def himself_herself_cap(self):
       return "Themself"

    @property
    def his_her(self):
       return "their"

    @property
    def his_her_cap(self):
       return "Their"