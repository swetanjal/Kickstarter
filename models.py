import sqlite3 as sql
from flask import session
from passlib.hash import sha256_crypt

def insertUser(request):
    con = sql.connect("database.db")
    username = request.form['username']
    password = request.form['password']
    fullname = request.form['fullname']
    password = sha256_crypt.encrypt(password)
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT)')
    sqlQuery = "select username from users where (username ='" + username + "')"
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    #Add code to check for existing email id.
    if row:
    	con.close()
    	return False
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, fullname) VALUES (?,?,?)", (username, password, fullname))
    con.commit()
    con.close()
    return True

def authenticateUser(request):
	con = sql.connect("database.db")
	username = request.form['username']
	password = request.form['password']
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT)')
	sqlQuery = "select password from users where (username = '"+ username + "')"
	cursor.execute(sqlQuery)
	row = cursor.fetchone()
	logged_in = False
	if row:
		logged_in = sha256_crypt.verify(password, row[0])
		if logged_in == True:
			return logged_in
	con.close()
	return logged_in

def insertPost(request, logged_user):
	con = sql.connect("database.db")
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text)')
	cursor.execute("INSERT INTO posts (id , title, about, fund, username) VALUES (NULL,?,?,?,?)", (title , about, fund, logged_user))
	con.commit()
	con.close()
	return ("Post created successfully!")
#Debugger Code
def getPost():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text)')
	cursor.execute("select * from posts")
	lis = cursor.fetchall()
	return lis

def getBackers():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS backers(project_id integer, username text, fund integer)')
	cursor.execute("select * from backers")
	lis = cursor.fetchall()
	return lis	
#############
def getMyPosts(logged_user):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement,title text,about text, fund integer, username text)')
	cursor.execute("select * from posts where username='%s'" % logged_user)
	listIt = cursor.fetchall()
	return listIt

def deletePost(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement,title text,about text, fund integer, username text)')
	cursor.execute("delete from posts where id='%s'" % id)
	con.commit()
	con.close()

def getPostInfo(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement,title text,about text, fund integer, username text)')
	cursor.execute("select * from posts where id='%s'" % id)
	post = cursor.fetchone()
	dicts = {}
	if post:
		dicts['id'] = post[0]
		dicts['title'] = post[1]
		dicts['about'] = post[2]
		dicts['fund'] = post[3]
		dicts['username'] = post[4]
	return dicts

def editPost(id_num, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement,title text,about text, fund integer, username text)')
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	cursor.execute("""UPDATE posts SET title=? ,about=? , fund=? WHERE id=?""",(title,about,fund,id_num))
	con.commit()
	con.close()

##############
def backPost(id_num, logged_user, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS backers(project_id integer, username text, fund integer)')
	fund = request.form['fund']
	cursor.execute("INSERT INTO backers (project_id , username, fund) VALUES (?,?,?)" , (id_num, logged_user, fund))
	con.commit()
	con.close()
	return "Thanks for supporting us!"