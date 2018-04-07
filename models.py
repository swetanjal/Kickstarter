import sqlite3 as sql
from flask import session
from passlib.hash import sha256_crypt

logged_in = False
logged_user = ''

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

def authenticateUser(request):
	con = sql.connect("database.db")
	username = request.form['username']
	password = request.form['password']
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)')
	sqlQuery = "select password from users where (username = '"+ username + "')"
	cursor.execute(sqlQuery)
	row = cursor.fetchone()
	if row:
		logged_in = sha256_crypt.verify(password, row[0])
		if logged_in == True:
		#logged_in = True
			logged_user = username
			con.close()
			return ("Successfully Logged in. Welcome back " + username + "!")
	con.close()
	return ("Invalid password or username!")
