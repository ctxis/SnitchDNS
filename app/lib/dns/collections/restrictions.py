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

    def gather(self, type):
        data = []
        for restriction in self.__restrictions:
            if restriction.type == type:
                data.append(restriction)

        return data

    def get_enabled(self):
        restrictions = []
        for restriction in self.__restrictions:
            if restriction.enabled:
                restrictions.append(restriction)

        return restrictions
