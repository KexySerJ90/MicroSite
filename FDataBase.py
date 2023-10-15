import sqlite3
import time
from math import floor
import re
from flask import url_for, flash



class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False
            base = url_for('static', filename='images_html')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)[\"'](?P<url>.+?)[\"']>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?,?,?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД" + str(e))
            return False
        return True

    def getPost(self, alias):
        try:
            self.__cur.execute("SELECT title, text FROM posts WHERE url LIKE ? LIMIT 1", (alias,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))

        return (False, False)

    def getPostsAnounce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД" + str(e))
        return []

    def checkUserExists(self, field, value):
        self.__cur.execute(f"SELECT COUNT() as count FROM users WHERE {field} LIKE '{value}'")
        res = self.__cur.fetchone()
        if res['count'] > 0:
            return True
        else:
            return False

    def addUser(self, name, email, hpsw):
        try:
            if self.checkUserExists('email', email):
                flash("Пользователь с таким email уже существует", "error")
                return False
            if self.checkUserExists('name', name):
                flash("Пользователь с таким именем уже существует", "error")
                return False
            tm = floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL,?,?,?,NULL,?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД" + str(e))
            return False
        return True


    def getUser(self, user_id):
        try:
            self.__cur.execute("SELECT * FROM users WHERE id = ?", user_id)
            res=self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ощибка получения данных из БД"+str(e))
        return False


    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email='{email}'")
            res=self.__cur.fetchone()
            if not res:
                flash("Пользователь не найден", "error")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД"+str(e))
        return False


    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False

        try:
            self.__cur.execute(f"UPDATE users SET avatar =? WHERE id=?",(avatar, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True