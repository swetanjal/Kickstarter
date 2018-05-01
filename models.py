import sqlite3 as sql
import datetime
from flask import session
from passlib.hash import sha256_crypt
import re

def regexp(expr, item):
    return re.search(expr, item) is not None
    reg = re.compile(expr)
    return reg.search(item) is not None

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
	dicts = {}
	dicts['project_id'] = backer[0]
	dicts['username'] = backer[1]
	dicts['fund'] = backer[2]
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select photo from users where username = '%s'" % dicts['username'])
	row = cursor.fetchall()
	dicts['photo'] = row[0][0]
	con.commit()
	con.close()
	return dicts

def insertUser(request):
    con = sql.connect("database.db")
    username = request.form['username']
    password = request.form['password']
    fullname = request.form['fullname']
    password = sha256_crypt.encrypt(password)
    cursor = con.cursor()
    sqlQuery = "select username from users where (username ='" + username + "')"
    cursor.execute(sqlQuery)
    row = cursor.fetchone()
    if row:
    	if isEmailConfirmed(username) == True:
    		con.close()
    		return False
    delEmailConfirmed(username)
    delUser(username)
    cur = con.cursor()
    cur.execute("INSERT INTO users (username, password, fullname, photo) VALUES (?,?,?,?)", (username, password, fullname, 'default.png'))
    con.commit()
    con.close()
    return True

def delUser(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("delete from users where username='%s'" % username)
	con.commit()
	con.close()	

def getUserInfo(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from users where username='%s'" % username)
	user = cursor.fetchone()
	return userDict(user)

def updateUser(request, username, img):
	con = sql.connect("database.db")
	cursor = con.cursor()
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
	sqlQuery = "select password from users where (username = '"+ username + "')"
	cursor.execute(sqlQuery)
	row = cursor.fetchone()
	logged_in = False
	if row:
		logged_in = sha256_crypt.verify(password, row[0])
		if logged_in == True:
			return (logged_in and isEmailConfirmed(username))
	con.close()
	return (logged_in and isEmailConfirmed(username))

def insertPost(request, logged_user, img):
	con = sql.connect("database.db")
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	duration = str(datetime.date.today() + datetime.timedelta(days = int(request.form['duration'])))
	video = request.form['video_url']
	cursor = con.cursor()
	cursor.execute("INSERT INTO posts (id , title, about, fund, username, duration, img, video) VALUES (NULL,?,?,?,?,?,?,?)", (title , about, fund, logged_user, duration, img, video))
	con.commit()
	cursor.execute('SELECT max(id) FROM posts')
	post_id = cursor.fetchone()[0]
	con.close()
	return post_id

def updatePostImg(id , img):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("""UPDATE posts SET img=? WHERE id=?""",(img, id))
	con.commit()
	con.close()

def editPost(id_num, img, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	title = request.form['title']
	about = request.form['about']
	fund = request.form['fund']
	duration = str(datetime.date.today() + datetime.timedelta(days = int(request.form['duration'])))
	video = request.form['video_url']
	cursor.execute("""UPDATE posts SET title=? ,about=? , fund=?, duration=?, img=?, video=? WHERE id=?""",(title,about,fund,duration, img, video, id_num))
	con.commit()
	con.close()

def getMyCreatedPosts(logged_user):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from posts where username='%s'" % logged_user)
	listIt = cursor.fetchall()
	ret = [] #Returns a list of dictionary objects
	for post in listIt:
		ret.append(postDict(post))
	return ret

def deletePost(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("delete from posts where id='%s'" % id)
	con.commit()
	con.close()

def getPostInfo(id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from posts where id='%s'" % id)
	post = cursor.fetchone()
	if post:
		return postDict(post)
	return {}


def backPost(id_num, logged_user, request):
	con = sql.connect("database.db")
	cursor = con.cursor()
	fund = request.form['fund']
	cursor.execute("INSERT INTO backers (project_id , username, fund) VALUES (?,?,?)" , (id_num, logged_user, fund))
	con.commit()
	con.close()
	return "Thanks for supporting us!"

def getBackedPosts(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select project_id from backers where username = '%s'" % username)
	lis=cursor.fetchall()
	post_list=[]
	for elem in lis:
		post_list.append(getPostInfo(elem[0]))
	return post_list

def getPost():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from posts")
	lis = cursor.fetchall()
	ret = [] #Returns a list of dictionary objects
	for post in lis:
		ret.append(postDict(post))
	return ret

def getBackers():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from backers")
	lis = cursor.fetchall()
	return lis	
def insertTag(postId, tag):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("INSERT INTO tags VALUES (?,?)", (postId, tag))
	con.commit()
	con.close()

def removeTag(postId):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("delete from tags where project_id='%s'" % postId)
	con.commit()
	con.close()

def getTags(postId):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select tag from tags where project_id='%s'" % postId)
	lis = cursor.fetchall()
	ret = {}
	for tag in lis:
		ret[tag[0]] = 1
	con.commit()
	con.close()	
	return ret

def searching_post_tag(pattern):
	con = sql.connect("database.db")
	con.create_function("REGEXP", 2, regexp)
	cursor = con.cursor()
	pattern = "(?i)" + pattern
	cursor.execute("select project_id from tags where tag REGEXP '%s'" % pattern)
	lis=cursor.fetchall()
	post_list=[]
	for elem in lis:
		post_list.append(getPostInfo(elem[0]))
	return post_list

def searching_post_name(pattern):
	con = sql.connect("database.db")
	con.create_function("REGEXP", 2, regexp)
	cursor = con.cursor()
	pattern = "(?i)" + pattern
	cursor.execute("select id from posts where title REGEXP '%s'" % pattern)
	lis=cursor.fetchall()
	post_list=[]
	for elem in lis:
		post_list.append(getPostInfo(elem[0]))
	return post_list

def searching_user(pattern):
	con = sql.connect("database.db")
	con.create_function("REGEXP", 2, regexp)
	cursor = con.cursor()
	pattern = "(?i)" + pattern
	cursor.execute("select username from users where username REGEXP '%s' or fullname REGEXP '%s'" % (pattern, pattern))
	lis=cursor.fetchall()
	user_list=[]
	for elem in lis:
		user_list.append(getUserInfo(elem[0]))
	return user_list

def email_confirmation(user, token, conf):
	con = sql.connect("database.db")
	cursor = con.cursor()
	confirm = 0
	cursor.execute("INSERT INTO confirm_table VALUES(?, ?, ?)", (user, token, confirm))
	con.commit()
	con.close()

def email_confirmation_update(token):
	con = sql.connect("database.db")
	cursor = con.cursor()
	confirm = 1
	cursor.execute("UPDATE confirm_table SET confirm= ? where token = ?", (True, token))
	con.commit()
	con.close()

def isEmailConfirmed(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select confirm from confirm_table where user = '"+ username+"'")
	r = cursor.fetchone()
	if r[0] == 1:
		return True
	con.commit()
	con.close()	
	return False

def delEmailConfirmed(username):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("delete from confirm_table where user='%s'" % username)
	con.commit()
	con.close()

def checkRecipient(recipient):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from users where username='%s'" % recipient)
	row = cursor.fetchall()
	if row == []:
		return False
	con.commit()
	con.close()
	return True

def getTopBackers(project_id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from backers where project_id='%s' ORDER BY fund DESC" % project_id)
	row = cursor.fetchall()
	backers = []
	c = 0
	for backer in row:
		if c == 5:
			break
		backers.append(backerDict(backer))
		c = c + 1
	con.commit()
	con.close()
	return backers

def getFunds(project_id):
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select fund from backers where project_id='%s' ORDER BY fund DESC" % project_id)
	row = cursor.fetchall()
	total = 0
	for amt in row:
		total = total + amt[0]
	con.commit()
	con.close()
	return total
def getBackingFunds():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select fund from backers")
	row = cursor.fetchall()
	total = 0
	for amt in row:
		total = total + amt[0]
	con.commit()
	con.close()
	return total

def getBackingCount():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from backers")
	row = cursor.fetchall()
	total = 0
	for amt in row:
		total = total + 1
	con.commit()
	con.close()
	return total

def getPostCount():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from posts")
	row = cursor.fetchall()
	total = 0
	for x in row:
		total = total + 1
	con.commit()
	con.close()
	return total

def getUserCount():
	con = sql.connect("database.db")
	cursor = con.cursor()
	cursor.execute("select * from users")
	row = cursor.fetchall()
	total = 0
	for x in row:
		if isEmailConfirmed(x[0]):
			total = total + 1
	con.commit()
	con.close()
	return total