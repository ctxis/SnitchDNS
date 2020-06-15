class RestrictionCollection:
    def __init__(self):
        self.__restrictions = []

    def add(self, restriction):
        self.__restrictions.append(restriction)

    def all(self):
        return self.__restrictions

    def count(self):
        return len(self.__restrictions)

    def get(self, id):
        for restriction in self.__restrictions:
            if restriction.id == id:
                return restriction
        return None
