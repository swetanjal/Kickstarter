from flask import Flask, render_template, request
import models as dbHandler
#create the application.
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', msg  = "Display something")

@app.route('/Signup' , methods = ['POST' , 'GET'])
def signup():
	if request.method == 'POST':
		return render_template('welcome_user.html', msg = dbHandler.insertUser(request))
	else:
		return render_template('signup.html')

@app.route('/Signin' , methods = ['POST' , 'GET'])
def signin():
	if request.method == 'POST':
		return render_template('logged_in.html', msg = dbHandler.authenticateUser(request))
	else:
		return render_template('signin.html')

if __name__ == '__main__':
    app.debug = True
    app.run()