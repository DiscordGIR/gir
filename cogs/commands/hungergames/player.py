class Player:
    def __init__(self, name, district, is_male: bool = True):
        self.name = name
        self.district = district
        self.is_male = is_male
        self.alive = True
        self.kills = 0
        self.cause_of_death = ""

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.district == other.district and self.is_male == other.is_male
        return False

    def __ne__(self, other):
        return self.name != other.name or self.district != other.district or self.is_male != other.is_male

    def __lt__(self, other):
        return (self.district, not self.is_male, self.name) < (other.district, not other.is_male, other.name)

    def __le__(self, other):
        return (self.district, not self.is_male, self.name) <= (other.district, not other.is_male, other.name)

    def __gt__(self, other):
        return (self.district, not self.is_male, self.name) > (other.district, not other.is_male, other.name)

    def __ge__(self, other):
        return (self.district, not self.is_male, self.name) >= (other.district, not other.is_male, other.name)

    def __hash__(self):
        return hash((self.district, self.is_male, self.name))

    @property
    def he_she(self):
        if self.is_male:
            return "he"
        return "she"

    @property
    def he_she_cap(self):
        if self.is_male:
            return "He"
        return "She"

    @property
    def him_her(self):
        if self.is_male:
            return "him"
        return "her"

    @property
    def him_her_cap(self):
        if self.is_male:
            return "Him"
        return "Her"

    @property
    def himself_herself(self):
        if self.is_male:
            return "himself"
        return "herself"

    @property
    def himself_herself_cap(self):
        if self.is_male:
            return "Himself"
        return "Herself"

    @property
    def his_her(self):
        if self.is_male:
            return "his"
        return "her"

    @property
    def his_her_cap(self):
        if self.is_male:
            return "His"
        return "Her"
