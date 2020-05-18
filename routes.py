from flask import Flask, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'

@app.route('/')
def home():
    return render_template('home.html', title="boop")

@app.route('/donut')
def donut():
    return render_template('donut.html', title="bipbip")

@app.route('/all_cakes')
def all_cakes():
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Cake;')
    results = cur.fetchall()
    #cur.execute('SELECT id FROM Cake;')
    #num = cur.fetchall()
    return render_template('all_cakes.html', cakes=results) #, var=num

@app.route('/cake/<int:id>')
def cake_name(id):
    print("DEBUG: I got cake id {}".format(id)) #TODO DEBUG
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Cake WHERE id={}".format(id))
    results = cur.fetchone()
    cur.execute("SELECT name FROM Topping WHERE id IN (SELECT tid FROM CakeTopping WHERE pid={})".format(id))
    details = cur.fetchall()
    return render_template('cake.html', cakes = results, toppings = details)

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')