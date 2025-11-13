class Users:
    def __init__(self, name, age, email):
        # конструктор

        self.__name = name
        self.__age = age
        self.__email = email
        self.subscriptions = []

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name: str):
        if len(name) >= 2:
            self.__name = name

    @property
    def age(self):
        return self.__age

    @age.setter
    def age(self, age: int):
        if age >= 16 and type(age) is int:
            self.__name = age

        else:
            raise ValueError('Для пользователей не младше 16 лет')

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email: str):
        if len(email) >= 1  and type(email) is str and '@' in email:
            self.__name = email

        else:
            raise ValueError('Email не может быть короче 1 символа и должен содержать @')

main_user = Users('Chikomazova Alice',17, 'a1is.1@yandex.ru')

