from flask import Flask, render_template, redirect, url_for, request, flash
import flask #added to make flask.redirect work
import sqlite3
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key' #used to secure sessions TODO change secret key to something else

def get_db_connection(): #use to connect to database
    conn = sqlite3.connect('Cake/Cake.db')
    conn.row_factory = sqlite3.Row #use to be able to return
    return conn

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

@app.route('/board/<int:post_id>', methods=('GET', 'POST'))
def post(post_id):
    post = get_post(post_id)
    comments = get_comments(post_id)
    if request.method == 'POST':
        content = request.form['content'] #gets data submitted by user
        if not content:
            flash('You must enter a comment')#TODO fix? supposed to flash this message
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO comments (pid, content) VALUES (?, ?)', (post_id, content,)) #gets where to put the comment and what's inside it
            conn.commit()
            conn.close()
            return redirect(request.referrer) #sends user back to page of post after commenting
    return render_template('post.html', post = post, comments = comments)

def get_post(post_id): #gets the post for the page
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone() #gets post with certain id, maybe can replace prev formats with ?
    conn.close()
    if post is None:
        abort(404) #if post doesnt exist, gives 404 error TODO make it redirect to somewhere else
    return post

def get_comments(post_id): #gets the comments for the page
    conn = get_db_connection()
    comments = conn.execute('SELECT * FROM comments WHERE pid = ?', (post_id,)).fetchall()
    conn.close()
    return comments

@app.route('/board')
def board():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM Posts ORDER BY id DESC').fetchall() #gets all posts
    conn.close()
    return render_template('board.html', posts=posts)

@app.route('/board/create', methods=('GET', 'POST')) #accepts GET (request) and POST (sent when submitting forms) requests
def create():
    if request.method == 'POST':
        title = request.form['title'] #gets data submitted by user
        content = request.form['content']
        if not title:
            flash('You must enter a title')#TODO fix? supposed to flash this message
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content)) #creates data for the post
            conn.commit()
            conn.close()
            return redirect(url_for('board'))
    return render_template('create.html')

@app.route('/board/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title'] #gets data submitted by user
        content = request.form['content']
        if not title:
            flash('You must enter a title')#TODO same as the same above
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?' ' WHERE id = ?', (title, content, id)) #changes data for post
            conn.commit()
            conn.close()
            return redirect(url_for('board'))
    return render_template('edit.html', post=post)

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