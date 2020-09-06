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

@app.route('/') #Home page
def home():
    return render_template('home.html', title="home")

@app.route('/all_cakes') #page displaying all cakes
def all_cakes():
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM Cake;')
    results = cur.fetchall()
    conn.close
    return render_template('all_cakes.html', cakes=results) #, var=num

@app.route('/cake/<int:id>') #page showing cakes individually
def cake_name(id):
    conn = sqlite3.connect('Cake/Cake.db')
    cur = conn.cursor()
    cur.execute("SELECT name, id, description FROM Cake WHERE id={}".format(id))
    results = cur.fetchall()
    print(results)
    if results == []:
        abort(404)
    else:
        cur.execute("SELECT name, description FROM Ingredient WHERE id IN (SELECT iid FROM CakeIngredient WHERE cid={})".format(id))
        details = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM Cake") #gets the number of cakes in database
        limit = cur.fetchone()
        if id == 1: #if on id=1
            previous = limit #goes to last cake id in database
        else:
            minus_one = id - 1
            cur.execute("SELECT id FROM Cake WHERE id={}".format(minus_one)) 
            previous = cur.fetchone()
        if id >= limit[0]: #if on last cake id in database
            plus_one = 1 #goes to cake id 1
        else:
            plus_one = id + 1
        cur.execute("SELECT id FROM Cake WHERE id={}".format(plus_one))
        nextup = cur.fetchone()
        return render_template('cake.html', cakes = results, ingredients = details, previousnum = previous, nextnum = nextup)

@app.route('/board/<int:post_id>', methods=('GET', 'POST')) #page displaying individual posts, accepts GET (request) and POST (sent when submitting forms) requests
def post(post_id):
    post = get_post(post_id)
    comments = get_comments(post_id)
    comment_counter = get_comment_number(post_id)
    check = "<" #Save this so the site can check for it
    if request.method == 'POST':
        content = request.form['content'] #gets data submitted by user
        if not content:
            flash('You must enter a comment')#TODO fix? supposed to flash this message
        elif check in content:#stops comment from being made if the string in the check variable is found
            print("< character detected")
            flash("The character '<' is not allowed")
        else:
            print("< character not detected")
            conn = get_db_connection()
            conn.execute('INSERT INTO comments (pid, content) VALUES (?, ?)', (post_id, content,)) #gets where to put the comment and what's inside it
            conn.commit()
            conn.close()
            return redirect(request.referrer) #sends user back to page of post after commenting
    return render_template('post.html', post = post, comments = comments, comment_counter = comment_counter)

def get_post(post_id): #gets the post for the page
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone() #gets post with certain id
    conn.close()
    if post is None:
        abort(404) #if post doesnt exist, gives 404 error TODO make it redirect to somewhere else
    return post

def get_comments(post_id): #gets the comments for the page
    conn = get_db_connection()
    comments = conn.execute('SELECT * FROM comments WHERE pid = ? AND reported=0' , (post_id,)).fetchall()
    conn.close()
    return comments

def get_comment_number(post_id): #gets the comments for the page
    conn = get_db_connection()
    comment_counter = conn.execute('SELECT COUNT(*) FROM comments WHERE pid = ? AND reported=0' , (post_id,)).fetchone()
    conn.close()
    return comment_counter

@app.route('/board') #message board, shows all post titles
def board():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM Posts WHERE reported=0 ORDER BY id DESC').fetchall() #gets all posts which havent been reported
    conn.close()
    return render_template('board.html', posts=posts)

@app.route('/board/create', methods=('GET', 'POST')) #page for creating posts, accepts GET (request) and POST (sent when submitting forms) requests
def create():
    check = "<" #Save this so the site can check for it
    if request.method == 'POST':
        title = request.form['title'] #gets data submitted by user
        content = request.form['content']
        if not title:
            flash('You must enter a title')#TODO fix? supposed to flash this message
        elif check in content: #stops post from being made if the string in the check variable is found
            print("< character detected")
            flash("The character '<' is not allowed")
        elif check in title:
            print("< character detected")
            flash("The character '<' is not allowed")
        else:
            print("< character not detected")
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content)) #creates data for the post
            conn.commit()
            conn.close()
            return redirect(url_for('board'))
    return render_template('create.html')

@app.route('/board/<int:id>/edit', methods=('GET', 'POST')) #page for editing posts
def edit(id):
    post = get_post(id)
    check = "<" #Save this so the site can check for it
    if request.method == 'POST':
        title = request.form['title'] #gets data submitted by user
        content = request.form['content']
        if not title:
            flash('You must enter a title')#TODO same as the same above
        elif check in content:#stops post from being made if the string in the check variable is found
            print("< character detected")
            flash("The character '<' is not allowed")
        elif check in title:
            print("< character detected")
            flash("The character '<' is not allowed")
        else:
            print("< character not detected")
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?' ' WHERE id = ?', (title, content, id)) #changes data for post
            conn.commit()
            conn.close()
            return redirect(url_for('board'))
    return render_template('edit.html', post=post)

@app.route('/board/<int:id>/report/post') #report the post
def report_post(id):
    conn = get_db_connection()
    conn.execute('UPDATE posts SET reported = ?' ' WHERE id = ?', (1, id)) #lets the database know the post has been reported
    conn.commit()
    conn.close()
    return redirect(url_for('board'))

#@app.route('/board/<int:id>/report/comment') #report a comment
#def report_comment(id):
#    conn = get_db_connection()
#    conn.execute('UPDATE comments SET reported = ?' ' WHERE pid = ?', (1, id)) #lets the database know the comment has been reported
#    conn.commit()
#    conn.close()
#    return redirect(url_for('board'))

@app.route('/about') #About Us page
def about():
    return render_template('about.html', title="about")

@app.route('/404') #error page
def page_not_found():
    return render_template('404.html', title="error 404")

@app.errorhandler(404) #if a 404 error occurs
def not_found_error(error):
    return flask.redirect('/404') #sends user to 404 page

if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')