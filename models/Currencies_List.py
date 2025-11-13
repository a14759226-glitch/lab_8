
class Currencies_List:
    def __init__(self, *id):
        self.__id = list(id)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, *id: str):
        if len(id) >= 1:
            self.__id = list(id)

main_id = Currencies_List('USD')