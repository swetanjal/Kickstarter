import sqlite3 as sql
from flask import session
from passlib.hash import sha256_crypt


def insertUser(request):
    con = sql.connect("database.db")
    username = request.form['username']
    password = request.form['password']
    password = sha256_crypt.encrypt(password)
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
    sqlQuery = "select username from users where (username ='" + username + "')"
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    if row:
    	con.close()
    	return "Username already registered"
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?,?)", (username,password))
    con.commit()
    con.close()
    return ("Welcome "+username+"!")