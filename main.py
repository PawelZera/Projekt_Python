# import the Flask class from the flask module
from flask import Flask, render_template, redirect, \
    url_for, request, session, flash, g
from functools import wraps
import sqlite3
import pandas as pd

# create the application object
app = Flask(__name__)

# config
app.secret_key = 'my precious'
app.database = 'sample.db'


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Najperw musisz się zalogować.')
            return redirect(url_for('login'))
    return wrap


# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    data = pd.read_excel('Polska.xls', sheet_name='zmiany stanów ludności', skipfooter=6, header=None)
    # przygotowanie danych
    data = data.drop(data.index[[0, 1]])
    data.index = data.iloc[:, 0]
    del data[data.columns[0]]
    data = data.astype('int64')
    data.columns = data.iloc[0]
    data = data.drop(data.index[[0]])
    data.index.name = None
    data.columns.name = None
    return render_template("index.html", tables=[data.to_html(classes='table table-striped')], titles=[''], labels=data.columns.to_list(), values=data.iloc[0].to_list())

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if (request.form['username'] != 'admin') \
                or request.form['password'] != 'admin':
            error = 'Błędne dane. Spróbuj ponownie.'
        else:
            session['logged_in'] = True
            flash('Zostałeś zalogowany.')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('Zostałeś wylogowany.')
    return redirect(url_for('welcome'))

# connect to database
def connect_db():
    return sqlite3.connect(app.database)


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=False)