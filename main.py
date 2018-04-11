from flask import Flask, render_template, request, redirect, url_for, session
import models as dbHandler
#create the application.
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
	#Some backend to be added to do the following:
	#1. Get some stats to be displayed on top.
	#2. Get the top 5 projects of each category.
	#The above function needs to be written both in models.py
	
	#Debugger code to get all posts and backers
	posts = dbHandler.getPost()
	backers = dbHandler.getBackers()
	
	if 'username' in session:
		return render_template('index.html', profile_pic = "https://www.freepnglogos.com/uploads/googlem-old-google-logo-png-5.png", 
			                  logged_user = session['username'], posts=posts, backers=backers)
	else:
		return render_template('index.html', profile_pic = "https://www.freepnglogos.com/uploads/googlem-old-google-logo-png-5.png",
		                       logged_user = "", posts=posts, backers=backers)

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
				status = dbHandler.authenticateUser(request)
				if status:
					session['username'] = request.form['username']
					return redirect(url_for('home'))
			else:
				invalid_credential = "Email has already been taken!"
		return render_template('signup.html' , invalid_credential = invalid_credential)
	else:
		return render_template('signup.html' , invalid_credential = invalid_credential)

@app.route('/Signin' , methods = ['POST' , 'GET'])
def signin():
	invalid_credential = "Invalid Password or username!"
	if request.method == 'POST':
		status = dbHandler.authenticateUser(request)
		if status:
			session['username'] = request.form['username']
			return redirect(url_for('home'))
		return render_template('signin.html', invalid_credential = invalid_credential)
	else:
		return render_template('signin.html', invalid_credential = "")

@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('home'))

@app.route('/settings', methods = ['POST' , 'GET'])
def settings():
	if 'username' not in session:
		return redirect(url_for('signin'))
	user = dbHandler.getUserInfo(session['username'])
	if request.method == 'POST':
		dbHandler.updateUser(request , session['username'])
		user = dbHandler.getUserInfo(session['username'])
		return render_template('editProfile.html', msg = "Changes Saved", user = user)
	return render_template('editProfile.html', msg = "", user = user)

@app.route('/createpost', methods = ['POST', 'GET'])
def createpost():
	if 'username' not in session:
		return redirect(url_for('signin'))
	if request.method == 'POST':
		return render_template('post_created.html' , msg = dbHandler.insertPost(request, session['username']))
	else:
		return render_template('postIt.html')

@app.route('/dashboard')
def dashboard():
	if 'username' not in session:
		return redirect(url_for('signin'))
	else:
		user = dbHandler.getUserInfo(session['username'])
		user_full_name = user['fullname']
		created_posts = dbHandler.getMyCreatedPosts(session['username'])
		backed_posts = []
		return render_template('dashboard.html', fullname = user_full_name, created_posts = created_posts, backed_posts = backed_posts)

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

@app.route('/editPostCaller/<int:id>', methods = ['POST','GET'])
def editPostCall(id):
	post = dbHandler.getPostInfo(id)
	if post:
		if 'username' in session:
			if not session['username'] == post['username']:
				return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
		if 'username' not in session:
			return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
		return render_template('editIt.html', id = post['id'], title = post['title'], des = post['about'], fund = post['fund'])
	else:
		return "Invalid Project Id to edit"

@app.route('/editFinalize/<int:id>', methods = ['POST','GET'])
def editFinal(id):
	if request.method == 'POST':
		dbHandler.editPost(id, request)
		return redirect(url_for('dashboard'))

@app.route('/project/<int:id>', methods = ['GET'])
def project(id):
	post = dbHandler.getPostInfo(id)
	if post:
		return render_template('project_display.html', id = post['id'], title = post['title'], about = post['about'], fund = post['fund'])
	else:
		return render_template('invalid_project_display.html')

@app.route('/project/<int:id>/back', methods = ['POST' , 'GET'])
def back(id):
	post = dbHandler.getPostInfo(id)
	if post:
		if request.method == 'GET':
			if 'username' not in session:
				return redirect(url_for('signin'))
			return render_template('back_project.html', id = post['id'] , title = post['title'])
		else:
			return render_template('acknowledge_backing.html', msg = dbHandler.backPost(id , session['username'], request))
	else:
		return render_template('invlaid_backing.html', msg = "You are attempting to back a project with invalid id!")

if __name__ == '__main__':
    app.debug = True
    app.run()
