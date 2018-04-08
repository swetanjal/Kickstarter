from flask import Flask, render_template, request, redirect, url_for
import models as dbHandler
#create the application.
app = Flask(__name__)

@app.route('/')
def home():
	x = dbHandler.getPost()
	return render_template('index.html', msg  = "Display something", logged_user = dbHandler.logged_user, l=x)

@app.route('/Signup' , methods = ['POST' , 'GET'])
def signup():
	if request.method == 'POST':
		return render_template('welcome_user.html', msg = dbHandler.insertUser(request))
	else:
		return render_template('signup.html')

@app.route('/Signin' , methods = ['POST' , 'GET'])
def signin():
	if request.method == 'POST':
		ret = dbHandler.authenticateUser(request)
		if dbHandler.logged_user:
			return redirect(url_for('dashboard'))
		return render_template('logged_in.html', msg = ret)
	else:
		return render_template('signin.html')

@app.route('/logout')
def logout():
	dbHandler.logged_user = ''
	dbHandler.logged_in = False
	return render_template('logged_out.html')

@app.route('/createpost', methods = ['POST', 'GET'])
def createpost():
	if dbHandler.logged_user == "":
		return redirect(url_for('signin'))
	if request.method == 'POST':
		return render_template('post_created.html' , msg = dbHandler.insertPost(request))
	else:
		return render_template('postIt.html')

@app.route('/dashboard')
def display_dash():
	if dbHandler.logged_user == "":
		return redirect(url_for('signin'))
	else:
		posts=dbHandler.getMyPosts()
		return render_template('dash.html', posts=posts)

@app.route('/deletePost/<int:id>', methods = ['POST','GET'])
def deletePost(id):
	dbHandler.deletePost(id)
	return redirect(url_for('display_dash'))

@app.route('/editPost/<int:id>', methods = ['POST','GET'])
def editPost(id):
	x=dbHandler.editPost(id)
	return render_template('editIt.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
