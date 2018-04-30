import os
import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, session
import models as dbHandler
from flask_mail import Mail
from flask_mail import Message
import smtplib
import random
import string
from passlib.hash import sha256_crypt
#create the application.
UPLOAD_FOLDER = './static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.update(
	DEBUG = True,
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465, 
	MAIL_USE_SSL = True,
	MAIL_USERNAME = 'swetanjaldatta@gmail.com',
	MAIL_PASSWORD = 'swetanjaldattaMartinian123')
mail = Mail(app)

def find_user():
	if 'username' in session:
		user = dbHandler.getUserInfo(session['username'])
		return session['username'];
	return ""

@app.route('/')
def home():
	#Some backend to be added to do the following:
	#1. Get some stats to be displayed on top.
	#2. Get the top 5 projects of each category.
	#The above function needs to be written both in models.py

	#Debugger code to get all posts and backers
	posts = dbHandler.getPost()
	backers = dbHandler.getBackers()
	no_of_posts = dbHandler.getPostCount()
	no_of_backings = dbHandler.getBackingCount()
	tot_backing_funds = dbHandler.getBackingFunds()
	no_of_users = dbHandler.getUserCount()
	if 'username' in session:
		user = dbHandler.getUserInfo(session['username'])
		return render_template('index.html', no_of_users = no_of_users, profile_pic = user['photo'], 
			                  logged_user = session['username'], posts=posts, backers=backers, no_of_posts = no_of_posts, no_of_backings = no_of_backings, tot_backing_funds = tot_backing_funds)
	else:
		return render_template('index.html', profile_pic = "default.png", no_of_users = no_of_users,
		                       logged_user = "", posts=posts, backers=backers, no_of_backings = no_of_backings, no_of_posts = no_of_posts, tot_backing_funds = tot_backing_funds)

def verify(password, verify_password, username, verify_username):
	#Put some code to do this. Can include regex
	#Username is basically Email!
	#By default NULL, else appropriate message: password too short or invalid email id or emails don't match etc.
	status_message = ""
	return status_message

@app.route('/Signup' , methods = ['POST' , 'GET'])
def signup():
	invalid_credential = ""
	if request.method == 'POST':
		invalid_credential = verify(request.form['password'], request.form['verify_password'], 
			request.form['username'], request.form['verify_username'])
		if invalid_credential == "":
			success = dbHandler.insertUser(request)
			
			if success:
				msg = Message("Email Verification Kickstarter",
                  sender="swetanjaldatta@gmail.com",
                  recipients=[request.form['username']])
				token2 = sha256_crypt.encrypt(request.form['username'])
				token = ""
				for c in token2:
					if c == "/" or c==".":
						continue
					else:
						token = token + c
				msg.html = 'Please verify your email by following this <a href="http://127.0.0.1:5000/verify/'+token+'">link</a>'
				dbHandler.email_confirmation(request.form['username'], token, False)
				invalid_credential = "Your Email-ID seems to be Invalid!"
				try:
					mail.send(msg)
				except:
					return render_template('signup.html' , invalid_credential = invalid_credential, logged_user = find_user())
				#status = dbHandler.authenticateUser(request)
				#if status:
				#	session['username'] = request.form['username']
				return redirect(url_for('home'))
			else:
				invalid_credential = "Email-ID has already been taken!"
		return render_template('signup.html' , invalid_credential = invalid_credential, logged_user = find_user())
	else:
		return render_template('signup.html' , invalid_credential = invalid_credential, logged_user = find_user())

@app.route('/verify/<key>')
def verify_email(key):
	dbHandler.email_confirmation_update(key)
	return render_template('signin.html')

@app.route('/Signin' , methods = ['POST' , 'GET'])
def signin():
	invalid_credential = "Invalid Password or username!"
	if request.method == 'POST':
		status = dbHandler.authenticateUser(request)
		if status:
			session['username'] = request.form['username']
			return redirect(url_for('home'))
		return render_template('signin.html', invalid_credential = invalid_credential, logged_user = find_user())
	else:
		return render_template('signin.html', invalid_credential = "", logged_user = find_user())

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('home'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/settings', methods = ['POST' , 'GET'])
def settings():
	if 'username' not in session:
		return redirect(url_for('signin'))
	user = dbHandler.getUserInfo(session['username'])
	url = user['photo'] 
	if request.method == 'POST':
		#Logic to verify if password and verify password are same to be added
		user = dbHandler.getUserInfo(session['username'])
		try:
			img = request.files['photo']
			if img and allowed_file(img.filename):
				filename = session['username'] + "." + img.filename.rsplit('.', 1)[1].lower()
				#Feature can be added to remove old photo
				url = filename
				img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			dbHandler.updateUser(request , session['username'], img = url)
			return render_template('editProfile.html', msg = "Changes Saved", user = dbHandler.getUserInfo(session['username']), logged_user = find_user())
		except:
			dbHandler.updateUser(request , session['username'], img = url)
			return render_template('editProfile.html', msg = "Changes Saved", user = dbHandler.getUserInfo(session['username']), logged_user = find_user())
	return render_template('editProfile.html', msg = "", user = user, logged_user = find_user())	

@app.route('/createpost', methods = ['POST', 'GET'])
def createpost():
	if 'username' not in session:
		return redirect(url_for('signin'))
	url = 'default.png'
	if request.method == 'POST':
		postID = dbHandler.insertPost(request, session['username'], 'default.png')
		try:
			img = request.files['project_photo']
			if img and allowed_file(img.filename):
				filename = str(postID) + "." + img.filename.rsplit('.', 1)[1].lower()
				#Feature can be added to remove old photo
				url = filename
				img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			dbHandler.updatePostImg(id = postID, img = url)
			tags = request.form.getlist('tags')
			for tag in tags:
				dbHandler.insertTag(postID, tag)
			return redirect(url_for('dashboard'))
		except:
			dbHandler.updatePostImg(id = postID, img = url)
			tags = request.form.getlist('tags')
			for tag in tags:
				dbHandler.insertTag(postID, tag)
			return redirect(url_for('dashboard'))
	else:
		return render_template('postIt.html', logged_user = find_user())

@app.route('/dashboard')
def dashboard():
	if 'username' not in session:
		return redirect(url_for('signin'))
	else:
		user = dbHandler.getUserInfo(session['username'])
		user_full_name = user['fullname']
		created_posts = dbHandler.getMyCreatedPosts(session['username'])
		backed_posts = dbHandler.getBackedPosts(session['username'])
		return render_template('dashboard.html', img = user['photo'], fullname = user_full_name, created_posts = created_posts, backed_posts = backed_posts, logged_user = find_user())

@app.route('/deletePost/<int:id>', methods = ['POST','GET'])
def deletePost(id):
	post = dbHandler.getPostInfo(id)
	if not post:
		return redirect(url_for('dashboard'))
	if 'username' in session:
		if not session['username'] == post['username']:
			return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
	dbHandler.deletePost(id)
	return redirect(url_for('dashboard'))

@app.route('/editPost/<int:id>', methods = ['POST','GET'])
def editPost(id):
	post = dbHandler.getPostInfo(id)
	if not post:
		return "Invalid Project Id to edit"
	if 'username' in session:
		if not session['username'] == post['username']:
			return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
	if 'username' not in session:
		return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
	if request.method == 'POST':
		dbHandler.removeTag(post['id'])
		url = post['img']
		################################
		try:
			img = request.files['project_photo']
			if img and allowed_file(img.filename):
				filename = str(post['id']) + "." + img.filename.rsplit('.', 1)[1].lower()
				#Feature can be added to remove old photo
				url = filename
				img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			dbHandler.editPost(post['id'], url, request)
			tags = request.form.getlist('tags')
			for tag in tags:
				dbHandler.insertTag(post['id'], tag)
			return redirect(url_for('dashboard'))
		except:
			dbHandler.editPost(post['id'], url, request)
			tags = request.form.getlist('tags')
			for tag in tags:
				dbHandler.insertTag(post['id'], tag)
			return redirect(url_for('dashboard'))
		################################
		#dbHandler.editPost(id, url, request)
		return redirect(url_for('dashboard'))
	else:
		tags = dbHandler.getTags(post['id'])
		return render_template('editPost.html', id = post['id'], tagTuple = tags , title = post['title'], des = post['about'], fund = post['fund'], video = post['video'], duration = (datetime.datetime.strptime(str(post['duration']), '%Y-%m-%d').date() - datetime.date.today()).days, logged_user = find_user())

#@app.route('/hack')
#def hack():
#	r=dbHandler.isEmailConfirmed('RR')
#	return ""+str(r)


@app.route('/project/<int:id>', methods = ['GET'])
def project(id):
	post = dbHandler.getPostInfo(id)
	backers = dbHandler.getTopBackers(id)
	funds_collected = dbHandler.getFunds(id)
	percentage_collected = (funds_collected*100)/post['fund']
	tags = dbHandler.getTags(id)
	if post:
		return render_template('project_display.html', tags = tags, percentage_collected = percentage_collected, funds_collected = funds_collected, backers = backers, post=post, id = post['id'], title = post['title'], about = post['about'], fund = post['fund'], duration = post['duration'], video = post['video'], img = post['img'], usr = post['username'], logged_user = find_user())
	else:
		return render_template('invalid_project_display.html', logged_user = find_user())

@app.route('/project/<int:id>/back', methods = ['POST' , 'GET'])
def back(id):
	post = dbHandler.getPostInfo(id)
	if post:
		if request.method == 'GET':
			if 'username' not in session:
				return redirect(url_for('signin'))
			return render_template('back_project.html', id = post['id'] , title = post['title'], logged_user = find_user())
		else:
			dbHandler.backPost(id , session['username'], request)
			return redirect(url_for('project', id = id))
	else:
		return render_template('invlaid_backing.html', msg = "You are attempting to back a project with invalid id!", logged_user = find_user())

@app.route('/search')
def search():
	results_posts_tag=dbHandler.searching_post_tag(request.args.get('pattern').strip())
	results = results_posts_tag
	results_posts_name = dbHandler.searching_post_name(request.args.get('pattern').strip())
	users = dbHandler.searching_user(request.args.get('pattern').strip())
	return render_template('search_page.html', search_results=results, users = users, results_posts_name = results_posts_name, results_posts_tag = results_posts_tag)

@app.route('/user/<name>')
def getUserPage(name):
	flag = 0
	try:
		flag = request.args['flag']
		flag = 1
	except:
		flag = 0
	user = dbHandler.getUserInfo(name)
	created_posts = dbHandler.getMyCreatedPosts(name)
	backed_posts = dbHandler.getBackedPosts(name)
	return render_template('view_user.html', flag=flag, user = user, img = user['photo'], fullname = user['fullname'], created_posts = created_posts, backed_posts = backed_posts, logged_user = find_user())

@app.route('/mailto/<recipient>' , methods = ['POST', 'GET'])
def mailto(recipient):
	#Form contains field subject, message
	if 'username' not in session:
		return redirect(url_for('signin'))
	if not dbHandler.checkRecipient(recipient):
		return redirect(url_for('home'))
	if request.method == 'POST':
		msg = Message(request.form['subject'],
              sender="swetanjaldatta@gmail.com",
              recipients=[recipient])
		message = request.form['message']
		msg.html = message + "<br>" + '<a href="http://127.0.0.1:5000/user/' + session['username'] +'">' + "View sender profile</a>" 
		try:
			mail.send(msg)
		except:
			return redirect(url_for('home'))
		return redirect(url_for('getUserPage', name = recipient, flag=True))
	else:
		return render_template("mailto.html", recipient = recipient)

if __name__ == '__main__':
    app.debug = True
    app.run()
