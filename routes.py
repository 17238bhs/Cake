from flask import Flask, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', title="home")

@app.route('/all_cakes')
def all_cakes():
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute('SELECT name FROM Cake;')
    results = cur.fetchall()
    cur.execute('SELECT id FROM Cake;')
    number = cur.fetchall()
    conn.close
    #cur.execute('SELECT id FROM Cake;')
    #num = cur.fetchall()
    return render_template('all_cakes.html', cakes=results, numbers=number) #, var=num

@app.route('/cake/<int:id>')
def cake_name(id):
    print("DEBUG: I got cake id {}".format(id)) #TODO DEBUG
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM Cake WHERE id={}".format(id))
    results = cur.fetchone()
    cur.execute("SELECT name FROM Ingredient WHERE id IN (SELECT iid FROM CakeIngredient WHERE cid={})".format(id))
    details = cur.fetchall()
    return render_template('cake.html', cakes = results, ingredients = details)

@app.route('/about')
def about():
    return render_template('about.html', title="about")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="contact")

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')