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

@app.route('/all_pizzas')
def all_pizzas():
    conn = sqlite3.connect('\Pizza\Pizzadb.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM Pizza;')
    results = cur.fetchall()
    #cur.execute('SELECT id FROM Pizza;')
    #num = cur.fetchall()
    return render_template('all_pizzas.html', pizzas=results) #, var=num

@app.route('/pizza/<int:id>')
def pizza_name(id):
    print("DEBUG: I got pizza id {}".format(id)) #TODO DEBUG
    conn = sqlite3.connect('c:\\Users\\17238\\Desktop\\Flask\\Pizza\\Pizzadb.db') #'H:/12DTP/Pizza/Pizzadb.db'
    cur = conn.cursor()
    cur.execute("SELECT * FROM Pizza WHERE id={}".format(id))
    results = cur.fetchone()
    cur.execute("SELECT name FROM Topping WHERE id IN (SELECT tid FROM PizzaTopping WHERE pid={})".format(id))
    details = cur.fetchall()
    return render_template('pizza.html', pizzas = results, toppings = details)

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')