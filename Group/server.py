





# "Jokes"
# Richard Kim
# Neil Denning


from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL  
from flask_bcrypt import Bcrypt
from datetime import datetime
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

'''
C - create - INSERT
R - read - SELECT
U - update - UPDATE
D - delete - DELETE
'''

app = Flask(__name__)
app.secret_key = "mystery_key"
bcrypt = Bcrypt(app)
database = "jokes"


@app.route("/")
def index():
    return render_template("main.html")


@app.route("/register", methods=["POST"])
def register_user():
    is_valid = True
    
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("First name must be at least 2 characters long")
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("First name must be at least 2 characters long")
    if len(request.form['alias']) < 2:
        is_valid = False
        flash("Last name must be at least 2 characters long")
    if len(request.form['password']) < 3:
        is_valid = False
        flash("Password must be at least 3 characters long")
        
    if request.form['c_password'] != request.form['password']:
        is_valid = False
        flash("Passwords must match")

    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please use a valid email address")
    
    if is_valid:
        pass_hash = bcrypt.generate_password_hash(request.form['password'])
        mysql = connectToMySQL(database)

        query = "INSERT INTO users (first_name, last_name, alias, email, password_hash, created_at, updated_at) VALUES (%(first_name)s, %(last_name)s, %(alias)s, %(email)s, %(pass_hash)s, NOW(), NOW())"
       
        data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'alias': request.form['alias'],            
            'email': request.form['email'],
            'pass_hash': pass_hash,
        }
      
        user_id = mysql.query_db(query, data)
        session['user_id'] = user_id

        return redirect("/landing")
    else:
        return redirect("/")


@app.route("/login", methods=["POST"])
def login_user():
    is_valid = True

    if len(request.form['email']) < 1:
        is_valid = False
        flash("Please enter your email")

    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please use a valid email address")

    if len(request.form['password']) < 1:
        is_valid = False
        flash("Please enter your password")
    
        
    if is_valid:
        mysql = connectToMySQL(database)
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            'email': request.form['email']
        }
        user = mysql.query_db(query, data)
        if user:
            hashed_password = user[0]['password_hash']
            if bcrypt.check_password_hash(hashed_password, request.form['password']):
                session['user_id'] = user[0]['id']
                return redirect("/landing")
            else:
                flash("Password is invalid")
                return redirect("/")
        else:
            flash("Please use a valid email address")
            return redirect("/")
    else:
        return redirect("/")
            

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/landing")
def landing():
    if 'user_id' not in session:
        return redirect("/")

    mysql = connectToMySQL(database)
    query = "SELECT * FROM users WHERE id = %(user_id)s"
    data = {'user_id': session['user_id']}
    user = mysql.query_db(query, data)
    print("*"*20)
    print(user)

    mysql = connectToMySQL(database)
    query = "SELECT jokes.user_id, jokes.id, users.first_name, users.last_name, users.alias, jokes.joke, jokes.punchline, jokes.created_at, COUNT(likes.joke_id) as times_liked FROM likes RIGHT JOIN jokes ON jokes.id = likes.joke_id LEFT JOIN users ON jokes.user_id = users.id GROUP BY jokes.user_id, jokes.id, users.first_name, users.last_name, users.alias, jokes.joke, jokes.punchline, jokes.created_at ORDER BY jokes.created_at DESC"
    jokes = mysql.query_db(query)



    mysql = connectToMySQL(database)
    query = "select * from likes WHERE user_id = %(user_id)s"
    is_liked = mysql.query_db(query, data)
    print(is_liked)

    mysql = connectToMySQL(database)
    query = "select * from jokes WHERE user_id = %(user_id)s"
    data = {'user_id': session['user_id']}
    my_jokes = mysql.query_db(query, data)
    print(str(jokes))
    print(str(session['user_id']))

    liked_jokes = []
    for liked in is_liked:
        liked_jokes.append(liked['joke_id'])    
    print(liked_jokes)


    print("*"*20)
    print(jokes)
    return render_template("/landing.html", user=user[0], jokes=jokes, liked_jokes=liked_jokes, my_jokes=my_jokes, my_id=session['user_id'])




@app.route("/save_joke", methods=["POST"])
def save_joke():
    if 'user_id' not in session:
        return redirect("/")

    is_valid = True
    if len(request.form['joke']) < 10:
        is_valid = False
        flash("Joke Please") 
    if len(request.form['joke']) > 255:
        is_valid = False
        flash("Joke too long") 
    if len(request.form['punchline']) < 10:
        is_valid = False
        flash("Punchline Please")
    if len(request.form['punchline']) > 255:
        is_valid = False
        flash("Punchline too long") 
    if is_valid:
        mysql = connectToMySQL(database)
        query = "INSERT INTO jokes (user_id, joke, punchline, created_at, updated_at) VALUES (%(user_id)s, %(joke)s, %(punchline)s, NOW(), NOW())"
        data = {'user_id': session['user_id'],
                'joke': request.form['joke'],
                'punchline': request.form['punchline']
        }
        joke_id = mysql.query_db(query, data)
        return redirect("/landing")  
    else:
        return redirect("/landing")


@app.route("/delete_joke/<joke_id>")
def delete_joke(joke_id):
    if 'user_id' not in session:
        return redirect("/")
    mysql = connectToMySQL(database)
    query = "DELETE FROM jokes WHERE jokes.id = %(joke_id)s"
    data = {
        'joke_id': joke_id
    }    
    mysql.query_db(query, data)

    return redirect("/landing")

@app.route("/details/<joke_id>")
def joke_details(joke_id):
    user = {}
    mysql = connectToMySQL(database)
    query = "SELECT * from likes JOIN users ON users.id = likes.user_id where joke_id = %(joke_id)s"
    data = {
        'joke_id': joke_id
    }
    likes = mysql.query_db(query, data)
    mysql = connectToMySQL(database)
    query = "SELECT * FROM jokes where id = %(joke_id)s"
    data = {
        'joke_id': joke_id
    }
    jokes = mysql.query_db(query, data)
    print(jokes)
    if len(jokes) > 0:
        print('has more')
        jokes = jokes[0]
        user_id = jokes['user_id']
        print(user_id)
        mysql = connectToMySQL(database)
        query = "SELECT * from users where id = %(user_id)s"
        print(query)
        data = {
            'user_id': user_id
        } 
        user = mysql.query_db(query, data)
        if len(user) > 0:
            user = user[0]

    return render_template("/details.html", likes=likes, jokes=jokes, user=user)


@app.route("/edit/1")
def edit_user():
    query = "SELECT * FROM users WHERE id = %(id)s"
    data = {
        'id': session['user_id']
    }
    mysql = connectToMySQL(database)
    user = mysql.query_db(query, data)
    return render_template("/edit.html", user=user[0])

@app.route("/edit/1", methods=['POST'])
def update_user():
    query = "UPDATE users SET first_name=%(fn)s, last_name=%(ln)s, email=%(email)s, updated_at=NOW() WHERE id=%(id)s"
    data = {
        'fn': request.form['first_name'],
        'ln': request.form['last_name'],
        'email': request.form['email'],
        'id': session['user_id']
    }
    mysql = connectToMySQL(database)
    mysql.query_db(query, data)
    return redirect("/landing")

@app.route('/back')
def back():
    return redirect('/landing')

@app.route("/unlike/<joke_id>")
def unlike_joke(joke_id):
    query = "DELETE FROM likes WHERE user_id= %(user_id)s AND joke_id = %(joke_id)s"
    data = {
        'user_id': session['user_id'],
        'joke_id': joke_id
    }
    mysql = connectToMySQL(database)
    mysql.query_db(query, data)
    return redirect ("/landing")

@app.route("/like/<joke_id>")
def like_joke(joke_id):
    mysql = connectToMySQL(database)
    query = "INSERT INTO likes (user_id, joke_id, created_at, updated_at) VALUES (%(user_id)s, %(joke_id)s, NOW(), NOW())"
    data = {
            'user_id': session ['user_id'],
            'joke_id': joke_id
        }
    user = mysql.query_db(query, data)
    return redirect("/landing")


if __name__=="__main__":
    app.run(debug=True)



'''<<<<<

these are notes I've been keeping with my template..

Flask.redirect(location, statuscode, response)

"location" = URL where response should be directed.

"statuscode" = statuscode sent to browser's header.

"response" = response parametwer used to instantiate response.

"Statuscodes"

STATUS CODES

HTTP_300_MULTIPLR_CHOICES
HTTP_301_MOVED_PERMANENTLY
HTTP_302_FOUND
HTTP_303_SEE_OTHER
HTTP_304_NOT_MODIFIED
HTTP_305_USE_PROXY
HTTP_306_RESERVED

FLASK.ABORT(CODE)

400_BAD_REQUEST
401_UNATHENTICATED
403_FORBIDDEN
404_NOT_FOUND
406_NOT_ACCEPTABLE
415_UNSOPPORTED_MEDIA_TYPE
429_TOO_MANY_REQUESTS



"host" = hostname to listen to. Defaults to 127.0..0.1 (localhost).
Set to '0.0.0.0' to have server available externally.

"port" = defaults to 5000. this can be changed as well.

"debug" = defaults to false. if set to true, provides debug information.

"options" = to be forwarded to underlying Werkzeug server,

"HTTP Protocol Methods" <<<<<

"GET" = Sends data in unencrypted form to server

"HEAD" = Same as GET, but without response body

"POST" = Used to send HTML form data to server.

"PUT" = Replaces all current representations of target resource with uploaded content.

"DELETE" = Removes all current representations of target resource given by URL.



"additional parameters" <<<<<

"int" = accepts integer

"float" = for floating point value

"path" = accepts slashes uswed as directory separator

"JINJA template engine uses the following delimiters for escaping from HTML"

{%...%} for Statements

{{...}} for Expressions to print to the template output

{#...#} for Comments not included in the template output

#...## for Line Statements


"REQUEST OBJECT"

"Form" = Dictionary object containing key-value pairs of form parameters and values.

"args" = Parsed contents of query string which i spart of URL after question mark(?)

"Cookies" = Dictionary object holding Cookie names and values. Helps with tracking data.

"files" = Data pertaining to the upload file.

"Method" = Current request method.



'''
