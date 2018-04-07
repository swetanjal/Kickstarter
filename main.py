from flask import Flask, render_template

#create the application.
app = Flask(__name__)

@app.route('/')
def home():

    return render_template('index.html', msg  = "Display something")


if __name__ == '__main__':
    app.debug = True
    app.run()
