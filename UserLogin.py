from flask_login import UserMixin
from flask import url_for

# Создаем класс UserLogin, который наследуется от класса UserMixin
class UserLogin(UserMixin):

    # Метод, который получает данные пользователя из базы данных
    def fromDB(self, user_id, db):
        self.__user=db.getUser(user_id) # Получаем данные пользователя из базы данных
        return self

    # Метод, который создает объект пользователя
    def create(self, user):
        self.__user=user # Сохраняем данные пользователя в объекте
        return self

    # Метод, который возвращает идентификатор пользователя
    def get_id(self):
        return str(self.__user['id'])

    # Метод, который возвращает имя пользователя
    def getName(self):
        return self.__user["name"] if self.__user else "Без имени"

    # Метод, который возвращает email пользователя
    def getEmail(self):
        return self.__user["email"] if self.__user else "Без email"

    # Метод, который возвращает аватар пользователя
    def getAvatar(self, app):
        img=None
        if not self.__user["avatar"]: # Если у пользователя нет своего аватара
            try:
                with app.open_resource(app.root_path+url_for("static", filename="images/ava.png"), "rb") as f:
                    img=f.read() # Загружаем аватар по умолчанию
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию: ", str(e))
        else:
            with app.open_resource(app.root_path + self.__user['avatar'], "rb") as f:
                img = f.read()

        return img

    # Метод, который проверяет расширение файла
    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1].lower()  # Получаем расширение файла и приводим его к нижнему регистру
        if ext in ['png', 'jpg', 'jpeg', "PNG", "JPG", "JPEG"] :  # Если расширение файла png, jpg или jpeg
            return True  # Возвращаем True
        return False  # Иначе возвращаем False