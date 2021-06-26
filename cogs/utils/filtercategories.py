class FilterCategory:
    def __init__(self, name, _id, color, description, delete_after, dm_only):
        self.name = name
        self._id = _id
        self.color = color
        self.description = description
        self.delete_after = delete_after
        self.dm_only = dm_only

class FilterCategories:
    def __init__(self):
        self.categories = {
            0: FilterCategory(
                    name = "default",
                    _id = 0,
                    color = None,
                    description = "asdf",
                    delete_after = True,
                    dm_only = True
                ),
            1: FilterCategory(
                    name = "piracy",
                    _id = 1,
                    color = None,
                    description = "asdf",
                    delete_after = True,
                    dm_only = True
                ),
        }
        
    def get(self, name: str):
        for category in self.categories:
            category = self.categories[category]
            if category.name == name:
                return category
            
        return None