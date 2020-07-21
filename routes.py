from flask import Flask, render_template, redirect, url_for, request, flash
import flask #added to make flask.redirect work
import sqlite3
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

def get_db_connection():
    conn = sqlite3.connect('Cake/Cake.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/blog/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/blog')
def blog():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM Posts').fetchall()
    conn.close()
    return render_template('blog.html', posts=posts)

@app.route('/blog/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('blog'))
    return render_template('create.html')

@app.route('/')
def home():
    return render_template('home.html', title="home")

@app.route('/all_cakes')
def all_cakes():
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM Cake;')
    results = cur.fetchall()
    conn.close
    #cur.execute('SELECT id FROM Cake;')
    #num = cur.fetchall()
    return render_template('all_cakes.html', cakes=results) #, var=num

@app.route('/cake/<int:id>') #can optimize the queries?
def cake_name(id):
    #print("DEBUG: I got cake id {}".format(id)) #TODO DEBUG
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute("SELECT name, id, description FROM Cake WHERE id={}".format(id))
    results = cur.fetchall()
    cur.execute("SELECT name, description FROM Ingredient WHERE id IN (SELECT iid FROM CakeIngredient WHERE cid={})".format(id))
    details = cur.fetchall()
    if id - 1 == 0:
        print("DEBUG: 0!!!")
        cur.execute("SELECT COUNT(*) FROM Cake")
        previous = cur.fetchone()
    else:
        print("DEBUG: NOT 0!!!")
        minusone = id - 1
        cur.execute("SELECT id FROM Cake WHERE id={}".format(minusone))
        previous = cur.fetchone()
    plusone = id + 1
    cur.execute("SELECT id FROM Cake WHERE id={}".format(plusone))
    nextup = cur.fetchone()
    return render_template('cake.html', cakes = results, ingredients = details, previousnum = previous, nextnum = nextup)

@app.route('/about')
def about():
    return render_template('about.html', title="about")

@app.route('/contact')
def contact():
    return render_template('contact.html', title="contact")

#@app.errorhandler(404) #if a 404 error occurs
#def not_found_error(error):
#    return flask.redirect("/cake/1")

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')