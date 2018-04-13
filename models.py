import sqlite3 as sql
from flask import session
from passlib.hash import sha256_crypt

def userDict(user):
	dicts = {}
	dicts['username'] = user[0]
	dicts['password'] = user[1]
	dicts['fullname'] = user[2]
	dicts['photo'] = user[3]
	return dicts

def postDict(post):
	dicts = {}
	dicts['id'] = post[0]
	dicts['title'] = post[1]
	dicts['about'] = post[2]
	dicts['fund'] = post[3]
	dicts['username'] = post[4]
	dicts['duration'] = post[5]
	dicts['img'] = post[6]
	dicts['video'] = post[7]
	return dicts

def backerDict(backer):
	pass

def insertUser(request):
    con = sql.connect("database.db")
    username = request.form['username']
    password = request.form['password']
    fullname = request.form['fullname']
    password = sha256_crypt.encrypt(password)
    cursor = con.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT, photo TEXT)')
    sqlQuery = "select username from users where (username ='" + username + "')"
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    if row:
    	con.close()
    	return False
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, fullname, photo) VALUES (?,?,?,?)", (username, password, fullname, 'default.png'))
    con.commit()
    con.close()
    return True

def getUserInfo(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT, photo TEXT)')
	cursor.execute("select * from users where username='%s'" % username)
	user = cursor.fetchone()
	return userDict(user)

def updateUser(request, username, img):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT, photo TEXT)')
	password = request.form['password']
	if password == "":
		user = getUserInfo(username)
		password = user['password']
	else:
		password = sha256_crypt.encrypt(password)
	fullname = request.form['fullname']
	cursor.execute("""UPDATE users SET username=? ,password=? , fullname=? , photo=? WHERE username=?""",(username,password,fullname,img,username))
	con.commit()
	con.close()

def authenticateUser(request):
	con = sql.connect("database.db")
	username = request.form['username']
	password = request.form['password']
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT, fullname TEXT, photo TEXT)')
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

def insertPost(request, logged_user, img):
	con = sql.connect("database.db")
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	duration = request.form['duration']
	video = request.form['video_url']
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("INSERT INTO posts (id , title, about, fund, username, duration, img, video) VALUES (NULL,?,?,?,?,?,?,?)", (title , about, fund, logged_user, duration, img, video))
	con.commit()
	cursor.execute('SELECT max(id) FROM posts')
	post_id = cursor.fetchone()[0]
	con.close()
	return post_id

def updatePostImg(id , img):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("""UPDATE posts SET img=? WHERE id=?""",(img, id))
	con.commit()
	con.close()

def editPost(id_num, img, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	duration = request.form['duration']
	video = request.form['video_url']
	cursor.execute("""UPDATE posts SET title=? ,about=? , fund=?, duration=?, img=?, video=? WHERE id=?""",(title,about,fund,duration, img, video, id_num))
	con.commit()
	con.close()

def getMyCreatedPosts(logged_user):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("select * from posts where username='%s'" % logged_user)
	listIt = cursor.fetchall()
	ret = [] #Returns a list of dictionary objects
	for post in listIt:
		ret.append(postDict(post))
	return ret

def deletePost(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("delete from posts where id='%s'" % id)
	con.commit()
	con.close()

def getPostInfo(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("select * from posts where id='%s'" % id)
	post = cursor.fetchone()
	if post:
		return postDict(post)
	return {}


def backPost(id_num, logged_user, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS backers(project_id integer, username text, fund integer)')
	fund = request.form['fund']
	cursor.execute("INSERT INTO backers (project_id , username, fund) VALUES (?,?,?)" , (id_num, logged_user, fund))
	con.commit()
	con.close()
	return "Thanks for supporting us!"

def getPost():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS posts(id integer primary key autoincrement, title text, about text, fund integer, username text, duration integer, img text, video text)')
	cursor.execute("select * from posts")
	lis = cursor.fetchall()
	ret = [] #Returns a list of dictionary objects
	for post in lis:
		ret.append(postDict(post))
	return ret

def getBackers():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute('CREATE TABLE IF NOT EXISTS backers(project_id integer, username text, fund integer)')
	cursor.execute("select * from backers")
	lis = cursor.fetchall()
	return lis	
#############