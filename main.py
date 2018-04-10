from flask import Flask, render_template, request, redirect, url_for, session
import models as dbHandler
#create the application.
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route('/')
def home():
	posts = dbHandler.getPost()
	backers = dbHandler.getBackers()
	if 'username' in session:
		return render_template('index.html', msg  = "Display something", logged_user = session['username'], posts=posts, backers=backers)
	else:
		return render_template('index.html', msg  = "Display something", logged_user = "", posts=posts, backers=backers)

@app.route('/Signup' , methods = ['POST' , 'GET'])
def signup():
	if request.method == 'POST':
		return render_template('welcome_user.html', msg = dbHandler.insertUser(request))
	else:
		return render_template('signup.html')

@app.route('/Signin' , methods = ['POST' , 'GET'])
def signin():
	if request.method == 'POST':
		status = dbHandler.authenticateUser(request)
		if status:
			session['username'] = request.form['username']
			return redirect(url_for('display_dash'))
		return render_template('logged_in.html', msg = "Invalid username or Password!")
	else:
		return render_template('signin.html')

@app.route('/logout')
def logout():
	session.pop('username', None)
	return render_template('logged_out.html')

@app.route('/createpost', methods = ['POST', 'GET'])
def createpost():
	if 'username' not in session:
		return redirect(url_for('signin'))
	if request.method == 'POST':
		return render_template('post_created.html' , msg = dbHandler.insertPost(request, session['username']))
	else:
		return render_template('postIt.html')

@app.route('/dashboard')
def display_dash():
	if 'username' not in session:
		return redirect(url_for('signin'))
	else:
		posts=dbHandler.getMyPosts(session['username'])
		return render_template('dash.html', posts=posts)

@app.route('/deletePost/<int:id>', methods = ['POST','GET'])
def deletePost(id):
	post = dbHandler.getPostInfo(id)
	if not post:
		return redirect(url_for('display_dash'))
	if 'username' in session:
		if not session['username'] == post['username']:
			return "<!DOCTYPE html><h1>NOT PERMITTED</h1>"
	dbHandler.deletePost(id)
	return redirect(url_for('display_dash'))

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
		return redirect(url_for('display_dash'))

@app.route('/project/<int:id>', methods = ['GET'])
def project(id):
	post = dbHandler.getPostInfo(id)
	if post:
		return render_template('project_display.html', id = post['id'], title = post['title'], about = post['about'], fund = post['fund'])
	else:
		return "Invalid project ID"

@app.route('/project/<int:id>/back', methods = ['POST' , 'GET'])
def back(id):
	post = dbHandler.getPostInfo(id)
	if post:
		if request.method == 'GET':
			if 'username' not in session:
				return redirect(url_for('signin'))
			return render_template('back_project.html', id = post['id'] , title = post['title'])
		else:
			return dbHandler.backPost(id , session['username'], request)
	else:
		return "You are attempting to back a project with invalid id!"

if __name__ == '__main__':
    app.debug = True
    app.run()
