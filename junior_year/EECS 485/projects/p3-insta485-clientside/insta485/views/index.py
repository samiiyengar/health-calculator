"""
Insta485 index (main) view.
URLs include:
/
"""
import flask
import insta485
import pathlib
import uuid
import hashlib
import os
import shutil
import io
import arrow

import sys

from functools import wraps
from flask import *

@insta485.app.errorhandler(400)
def error_400(error):
    return flask.render_template("400_error.html"), 400

@insta485.app.errorhandler(401)
def error_401(error):
    return flask.render_template("401_error.html"), 401

@insta485.app.errorhandler(403)
def error_403(error):
    return flask.render_template("403_error.html"), 403

@insta485.app.errorhandler(409)
def error_409(error):
    return flask.render_template("409_error.html"), 409

# make sure this is right
def read_file(filename):
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'static', 'uploads', filename)
   
def check_password(password, password_db_string):
    [algorithm, salt, password_hash] = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    return hash_obj.hexdigest() == password_hash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("decorated_function")
        if 'logged_user' not in flask.session:
            print("Not logged in")
            return flask.redirect(flask.url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
   
def generate_password(password):
    algorithm = 'sha512'
    salt = uuid.uuid4().hex
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    password_hash = hash_obj.hexdigest()
    password_db_string = "$".join([algorithm, salt, password_hash])
    return password_db_string

# make sure this is right
def file_uploader(fileobj):
    filename = fileobj.filename

    uuid_basename = "{stem}{suffix}".format(
    stem=uuid.uuid4().hex,
    suffix=pathlib.Path(filename).suffix
    )

    path = insta485.app.config["UPLOAD_FOLDER"]/uuid_basename
    fileobj.save(path)
    return uuid_basename

# make sure this is right
def profpic_deleter(filename):
    path = insta485.app.config["UPLOAD_FOLDER"]/filename
    os.remove(path)

# make sure this is right
@insta485.app.route('/sql/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(insta485.app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# make sure this is right
@insta485.app.route('/', methods=['GET', 'POST'])
@login_required
def show_index():
    """Display / route."""

    print("ShowIndex")
    logged_in_user = flask.session["logged_user"]

    # Connect to database
    connection = insta485.model.get_db()

    cur = connection.execute(
        "SELECT * FROM following WHERE username1=? ",
        (logged_in_user,)
    )
    following = cur.fetchall()

    cur = connection.execute(
        "SELECT * FROM posts WHERE owner=? ", (logged_in_user,)
    )
    posts_on_feed = cur.fetchall()

    # iterate through each dictionary of following entries
    for follow in following:
        cur = connection.execute(
            "SELECT * FROM posts WHERE owner=? ORDER BY postid ASC ", (follow['username2'],)
        )
        # posts_by_following = cur.fetchall()
        # posts_on_feed.append(posts_by_following)
        posts_on_feed += cur.fetchall()
    # posts_on_feed = sorted(posts_on_feed.items(), key = lambda i: i['postid'],reverse=True)

    post_info = []
    # iterate through whole post entry
    for post in posts_on_feed:
        # getting post owner
#        cur = connection.execute(
#            "SELECT owner FROM posts WHERE postid=? ", (id)
#        )
#        post_owner = cur.fetchone()
        post_owner = post['owner']

        # getting post owner profile pic
        cur = connection.execute(
            "SELECT filename FROM users WHERE username=? ", (post_owner,)
        )
        owner_dict = cur.fetchone()
        owner_img_url = owner_dict['filename']

        # getting post pic
#        cur = connection.execute(
#            "SELECT filename FROM posts WHERE postid=?", (id)
#        )
#        img_url = cur.fetchone()
        img_url = post['filename']

        # timestamp
#        cur = connection.execute(
#            "SELECT created FROM posts WHERE postid=? ", (id)
#        )
#        timestamp = arrow.get(cur.fetchone()).humanize()
        timestamp = arrow.get(post['created']).humanize()

        # getting post likes
        cur = connection.execute(
            "SELECT COUNT(owner) FROM likes WHERE postid=? ", (post['postid'],)
        )
        # double check this
        likes_dict = cur.fetchone()
        likes = likes_dict['COUNT(owner)']

        # getting if post is liked by logged in user
        cur = connection.execute(
            "SELECT * FROM likes WHERE postid=? ", (post['postid'],)
        )
        likers = cur.fetchall()

        liked_by_logname = False
        for i in likers:
            if i['owner'] == logged_in_user:
                liked_by_logname = True

        comment_info = []
        # getting post comments
        cur = connection.execute(
            "SELECT * FROM comments WHERE postid=? ", (post['postid'],)
        )
        comment_ids = cur.fetchall()
       
       
        for j in comment_ids:
#            cur = connection.execute(
#                "SELECT owner FROM comments WHERE commentid=? ", (j)
#            )
#            comment_owner = cur.fetchone()
#            cur = connection.execute(
#                "SELECT text FROM comments WHERE commentid=? ", (j)
#            )
#            comment_text = cur.fetchone()
           
            comment = {
            "owner": j['owner'],
            "text": j['text']
            }
            comment_info.append(comment)

        post_dict = {
            "postid": post['postid'],
            "owner": post_owner,
            "owner_img_url": owner_img_url,
            "img_url": img_url,
            "timestamp": timestamp,
            "likes": likes,
            "liked_by_logname": liked_by_logname,
            "comments": comment_info
        }
        post_info.append(post_dict)

    # Add database info to context
    context = {"logname": flask.session["logged_user"], "posts": post_info}
    return flask.render_template("index.html", **context)

# make sure this is right
@insta485.app.route('/posts/<postid>/', methods=['GET', 'POST'])
@login_required
def post(postid):
    """Individual post page"""

    connection = insta485.model.get_db()
    cur = connection.execute("SELECT * FROM posts WHERE postid = ?",(postid, ))
    post = cur.fetchone()

    if flask.request.method == "POST":

        if flask.request.form["operation"] == "create":
            filename = file_uploader(flask.request.files["file"])
            connection.execute("""INSERT INTO posts (filename, owner) VALUES (?, ?)""", (filename, flask.session["logged_user"]))
            connection.commit()

        target = None
        if "target" in flask.request.args:
            target = flask.request.args.get("target")

        if target == None:
            p_owner = post['owner']
            if p_owner == flask.session['logged_user'] and "delete" in flask.request.form:
                connection.execute("""DELETE FROM posts WHERE postid = ?""", (postid,))
                connection.commit()
                profpic_deleter(post['filename'])

            return flask.redirect(flask.url_for('show_users', username=p_owner))

        else:
            if "uncomment" in flask.request.form:
                commentid = flask.request.form['commentid']

                cur = connection.execute("""SELECT * FROM posts WHERE postid = ?""", (postid,))
                owner = cur.fetchone()["owner"]
                cur = connection.execute("""SELECT * FROM comments WHERE commentid = ?""", (commentid,))
                c_owner = cur.fetchone()["owner"]

                if flask.request.form['operation'] == "delete" and (owner == flask.session['logged_user'] or c_owner == flask.session['logged_user']):

                    connection.execute("""DELETE FROM comments WHERE commentid = ?""", (commentid,))
                    connection.commit()

            target = flask.request.args.get("target")
            return flask.redirect(flask.url_for('post', postid=postid))


    else:

        context = {}
        context['owner'] = post['owner']
        context['postid'] = post['postid']
       
        created = arrow.get(post['created'])
        context['created'] = created.humanize()
        context['filename'] = post['filename']

        read_file(context['filename'])

        cur = connection.execute("SELECT filename FROM users WHERE username=?",(post["owner"],))
        context["owner_img_url"] = cur.fetchone()["filename"]

        read_file(context["owner_img_url"])

        cur = connection.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=?",(post["postid"],))
        context["likes"] = cur.fetchone()["num"]

        cur = connection.execute("SELECT * FROM comments WHERE postid=?",(post["postid"],))
        context["comments"] = list(cur.fetchall())

        cur = connection.execute("SELECT COUNT(*) AS num FROM likes WHERE postid=? AND owner=?",(post["postid"],flask.session["logged_user"],))
        context["like"] = cur.fetchone()["num"]>0

        return flask.render_template("post.html", **context)


@insta485.app.route('/likes/', methods=['POST'])
@login_required
def like():
    """Like/Unlike Endpoint"""

    connection = insta485.model.get_db()

    postid = flask.request.form['postid']

    if 'like' in flask.request.form:
        connection.execute("""INSERT INTO likes (owner, postid) VALUES (?, ?)""", (flask.session["logged_user"], postid))
        connection.commit()
    else:
        connection.execute("""DELETE FROM likes WHERE owner=? and postid=?""", (flask.session["logged_user"], postid))
        connection.commit()
   
    target = None
    if "target" in flask.request.args:
        target = flask.request.args.get("target")

    if target == None:
        target = "/"
    else:
        target = flask.url_for("post", postid=postid)

    return flask.redirect(target)
   

@insta485.app.route('/comments/', methods=['POST'])
@login_required
def comment():
    """Comment Endpoint"""

    connection = insta485.model.get_db()

    operation = flask.request.form['operation']
    postid = flask.request.form['postid']

    if operation == "delete":
        commentid = flask.request.form['commentid']
        cur = connection.execute("""SELECT owner FROM comments WHERE commentid = ? AND owner = ?""", (commentid, flask.session["logged_user"]))
        if cur.fetchone() == None:
            flask.flash("Cannot delete comment that is not your own.")
            abort(403)

        connection.execute("""DELETE FROM comments WHERE commentid = ? AND owner = ?""", (commentid, flask.session["logged_user"]))
        connection.commit()

    else:
        text = flask.request.form['text']
        if text == "":
            flask.flash("Empty comment.")
            abort(400)
       
        connection.execute("""INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)""", (flask.session["logged_user"], postid, text))
        connection.commit()

    target = None
    if "target" in flask.request.args:
        target = flask.request.args.get("target")

    if target == None:
        target = "/"
    else:
        target = flask.url_for("post", postid=postid)

    return flask.redirect(target)


@insta485.app.route('/explore/', methods=['GET', 'POST'])
@login_required
def show_explore():
    db = insta485.model.get_db()
    context = {"logname":flask.session['logged_user']}

    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            try:
                db.execute("INSERT INTO following(username1, username2) VALUES (?,?)",\
                    (flask.session["logged_user"],flask.request.form["target"],))
            except:
                #fixme
                pass

    cur = db.execute("""SELECT username, filename AS user_img_url FROM users
    WHERE username NOT IN (SELECT username2 FROM following WHERE username1=?) AND username!=?""",(flask.session["logged_user"],flask.session["logged_user"],))
   
    context["not_following"] = list(cur.fetchall())

    for user in context["not_following"]:
        read_file(user["user_img_url"])
   
    return flask.render_template("explore.html", **context)
   
@insta485.app.route('/users/<username>/', methods=['GET', 'POST'])
@login_required
def show_users(username):
    db = insta485.model.get_db()
    #context = {"logname":flask.session['logged_user']}
    context = {"logname":flask.session['logged_user'], "username":username}
   
    if flask.request.method == 'POST':
        if "follow" in flask.request.form:
            db.execute("INSERT INTO following (username1, username2) VALUES (?,?)", (flask.session["logged_user"], username))
            db.commit()
       
        elif "unfollow" in flask.request.form:
            db.execute("DELETE FROM following WHERE username1 = ? AND username2 = ?", (flask.session["logged_user"], username))
            db.commit()

        elif "create_post" in flask.request.form and username == flask.session["logged_user"]:
            new_post = flask.request.files["file"]
            filename = file_uploader(new_post)
            db.execute("""INSERT INTO posts (filename, owner) VALUES (?, ?)""", (filename, flask.session["logged_user"]))
            db.commit()

        return flask.redirect(flask.url_for('show_users', username = username))

    else:
        cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=? AND username2=?",\
            (flask.session["logged_user"],username,))
        context["logname_follows_username"] = cur.fetchall()[0]["num"]
       
        cur = db.execute("SELECT postid, filename AS img_url FROM posts WHERE owner=?",(username,))
        context["posts"] = list(cur.fetchall())
       
        for post in context["posts"]:
            read_file(post['img_url'])
           
        context["total_posts"] = len(context["posts"])
        cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username2=?",(username,))
        context["followers"] = cur.fetchall()[0]["num"]
        cur = db.execute("SELECT COUNT(*) AS num FROM following WHERE username1=?",(username,))
        context["following"] = cur.fetchall()[0]["num"]
        cur = db.execute("SELECT fullname, filename FROM users WHERE username=?",(username,))
        okay = cur.fetchone()
        context["fullname"] = okay["fullname"]
        context["filename"] = okay["filename"]

        if username != flask.session["logged_user"]:
            cur = db.execute("""SELECT * FROM following WHERE username1 = ? AND username2 = ?""", (flask.session["logged_user"], username))
            context["follows_user"] = cur.fetchone() != None
       
   
    return flask.render_template("user.html", **context)
   
@insta485.app.route('/users/<username>/following/', methods=['GET', 'POST'])
@login_required
def show_following(username):
    #print("following")
    #print(username)
    db = insta485.model.get_db()
    context = {"logname":flask.session['logged_user'], "username":username}
   
    if flask.request.method == 'POST':
        username_fol = flask.request.form["username"]
        if flask.request.form["operation"] == "unfollow":
            db.execute("DELETE FROM following WHERE username1 = ? AND username2 = ?", (flask.session["logged_user"], username_fol,))
           
        else:
            db.execute("""INSERT INTO following (username1, username2) VALUES (?, ?)""", (flask.session["logged_user"], username_fol,))

        db.commit()
        return flask.redirect(url_for("show_following", username = username))

    else:
        cur = db.execute("""SELECT username, filename AS user_img_url FROM users WHERE username IN (SELECT username2 FROM following WHERE username1=?) AND username!=?""", (username, username))
        context["following"] = list(cur.fetchall())

        cur = db.execute("""SELECT username2 FROM following WHERE username1 = ?""", (flask.session["logged_user"], ))
        un2 = list(cur.fetchall())
        context["i_follow"] = []
        for i in un2:
            context["i_follow"].append(i["username2"])

        for user in context["following"]:
            read_file(user["user_img_url"])
           
        return flask.render_template("following.html", **context)
   
@insta485.app.route('/users/<username>/followers/', methods=['GET', 'POST'])
@login_required
def show_followers(username):
    db = insta485.model.get_db()
    context = {"logname":flask.session['logged_user'], "username":username}
   
    if flask.request.method == 'POST':
        username_fol = flask.request.form["username"]
        if "unfollow" in flask.request.form:
            db.execute("DELETE FROM following WHERE username1 = ? AND username2 = ?", (flask.session["logged_user"], username_fol,))
           
        else:
            db.execute("""INSERT INTO following (username1, username2) VALUES (?, ?)""", (flask.session["logged_user"], username_fol,))

        db.commit()
        return flask.redirect(url_for("show_followers", username = username))

    else:
        cur = db.execute("""SELECT username, filename AS user_img_url FROM users WHERE username IN (SELECT username1 FROM following WHERE username2=?) AND username!=?""", (username, username))
        context["followers"] = list(cur.fetchall())

        cur = db.execute("""SELECT username2 FROM following WHERE username1 = ?""", (flask.session["logged_user"], ))
        un2 = list(cur.fetchall())
        context["i_follow"] = []
        for i in un2:
            context["i_follow"].append(i["username2"])
       
        print(context["i_follow"], sys.stderr)
   
        for user in context["followers"]:
            read_file(user["user_img_url"])
       
        return flask.render_template("followers.html", **context)

# make sure this works
@insta485.app.route('/accounts/', methods=['POST'])
def accounts():
    """Account Operation Redirector"""

    connection = insta485.model.get_db()

    data = flask.request.form
   
    target = None
    if "target" in flask.request.args:
        target = flask.request.args.get("target")
   
    if "operation" in data:
        operation = data['operation']

    if target == None:
        target = "/"

    if operation == "login":
        username = data['username']
        pw = data['password']
        if username == "" or pw == "":
            abort(400)

        cur = connection.execute(
            '''SELECT username, password
            FROM users
            WHERE username = ?''',
            (username, )
        )

        user = cur.fetchone()

        if user == None:
            abort(403)

        if check_password(pw, user['password']):
            flask.session['logged_user'] = username
        else:
            flask.flash('Login Failed')
            abort(403)

    elif operation == "create":
        profpic = data['file']
        fullname = data['fullname']
        username = data['username']
        email = data['email']
        password = data['password']
        password = generate_password(password)

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (username, )
        )

        user = cur.fetchone()

        if user != None:
            flask.flash("User already exists.")
            abort(409)

        connection.execute(
            '''INSERT INTO users (username, fullname, email, filename, password)
               VALUES (?, ?, ?, ?, ?);''',
            (username, fullname, email, profpic.filename, password)
        )
        connection.commit()

        flask.session['logged_user'] = username
   
    elif operation == "delete":
        if "logged_user" not in flask.session:
            abort(403)

        cur = connection.execute(
            '''DELETE FROM users
               WHERE username = ?''',
               (flask.session["logged_user"], ))

        connection.commit()
        flask.session.clear()
   
    elif operation == "edit_account":
        if "logged_user" not in flask.session:
            abort(403)

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()
        profPic = user["filename"]

        if "file" in flask.request.files:
            profpic_deleter(profPic)
            profPic = flask.request.files['file']
            filename = file_uploader(profPic)
            profPic = filename
        fullname = data['fullname']
        email = data['email']

        cur = connection.execute(
            '''UPDATE users
               SET filename = ?,
               fullname = ?,
               email = ?
               WHERE username = ?''',
               (profPic, fullname, email, flask.session["logged_user"])
        )

        connection.commit()

    elif operation == "update_password":
        old_password = data['password']
        new_password1 = data['new_password1']
        new_password2 = data['new_password2']

        if old_password == "" or new_password1 == "" or new_password2 == "":
            flask.flash("Empty field.")
            abort(400)

        if new_password1 != new_password2:
            flask.flash("New passwords do not match.")
            abort(401)

        if old_password == new_password1:
            flask.flash("Old and new passwords are the same.")
            return flask.redirect(flask.url_for("change_password"))

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()

        if not check_password(old_password, user["password"]):
            flask.flash("Incorrect current password.")
            abort(403)

        updated_password = generate_password(new_password1)
        cur = connection.execute(
            '''UPDATE users
               SET password = ?
               WHERE username = ?''',
               (updated_password, flask.session["logged_user"])
        )

        connection.commit()
    else:
        return flask.redirect(target)

    return flask.redirect(target)


# make sure this works
#@insta485.app.route('/accounts/login/', methods=['GET'])
#def login():
    """Login User"""
   
    #if flask.request.method == "POST":
        #Connect to database
     #   connection = insta485.model.get_db()

      #  username = flask.request.form.get("username")
       # pw = flask.request.form.get("password")

        #if username == "" or pw == "":
         #   abort(400)

       # cur = connection.execute(
        #    '''SELECT username, password
         #   FROM users
          #  WHERE username = ?''',
           # (username, )
        #)

        #user = cur.fetchone()

        #if user == None:
         #   abort(403)

       # if check_password(pw, user['password']):
        #    flask.session['logged_user'] = username
         #   return flask.redirect(flask.url_for("show_index"))
        #else:
         #   flask.flash('Login Failed')
          #  abort(403)
           
   # else:
   # if "logged_user" in flask.session:
   #     return flask.redirect(flask.url_for('show_index'))
   # return flask.render_template("login.html")

@insta485.app.route('/accounts/login/', methods=['GET', 'POST'])
def login():
    if flask.session.get('logged_user'):
        return flask.redirect(flask.url_for('show_index'))
    else:
        context = {}
        if flask.request.method == 'GET':
            return flask.render_template("login.html")
        else:
            db = insta485.model.get_db()
            cur = db.execute("SELECT password FROM users WHERE username=?",(flask.request.form["username"],))
            res = list(cur.fetchall())
            if res and check_password(flask.request.form["password"],res[0]['password']):
                flask.session['logged_in'] = True
                flask.session['logged_user'] = flask.request.form["username"]
                return flask.redirect(flask.url_for('show_index'))
            else:
                flask.flash('Fail to login!')
                # return flask.render_template("login.html")
                flask.abort(403)

# make sure this works
@insta485.app.route("/accounts/logout/", methods=['POST'])
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("login"))
   
def login_permission(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not flask.session.get('logged_user'):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
   
# insta485.app.view_functions['static'] = login_permission(insta485.app.send_static_file)

#make sure this works
@insta485.app.route("/accounts/create/", methods=['GET', 'POST'])
def signup():
    """Create User"""
   
    if flask.request.method == "POST":

        connection = insta485.model.get_db()

        profpic = flask.request.files["file"]
        fullname = flask.request.form.get("fullname")
        username = flask.request.form.get("username")
        email = flask.request.form.get("email")
        password = flask.request.form.get("password")
        password = generate_password(password)

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (username, )
        )

        user = cur.fetchone()

        if user != None:
            flask.flash("User already exists.")
            abort(409)

        filename = file_uploader(profpic)

        connection.execute(
            '''INSERT INTO users (username, fullname, email, filename, password)
               VALUES (?, ?, ?, ?, ?);''',
            (username, fullname, email, filename, password)
        )
        connection.commit()

        flask.session['logged_user'] = username
        return flask.redirect(flask.url_for("edit"))
       
    else:
        if "logged_user" in flask.session:
            return flask.redirect(flask.url_for("edit_account"))
        return flask.render_template("signup.html")


@insta485.app.route("/accounts/edit/", methods=['GET', 'POST'])
@login_required
def edit():
    """Edit User"""

    if flask.request.method == "POST":

        connection = insta485.model.get_db()

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()
        profPic = user["filename"]

        profpicChange = flask.request.files["file"]
        fullname = flask.request.form.get("fullname")
        email = flask.request.form.get("email")

        if profpicChange != None:
            filename = file_uploader(profpicChange)
            profpic_deleter(profPic)
            profPic = filename

        cur = connection.execute(
            '''UPDATE users
               SET filename = ?,
               fullname = ?,
               email = ?
               WHERE username = ?''',
               (profPic, fullname, email, flask.session["logged_user"])
        )

        connection.commit()

        return flask.redirect(flask.url_for("edit"))

    else:
        if "logged_user" not in flask.session:
            return flask.redirect(flask.url_for("login"))

        connection = insta485.model.get_db()

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()

        context = {
            "profilepic": user["filename"],
            "fullname": user["fullname"],
            "email": user["email"]
        }

        return flask.render_template("account_edit.html", **context)


@insta485.app.route("/accounts/delete/", methods=['GET', 'POST'])
def delete_account():
    """Delete Profile"""

    if flask.request.method == "POST":
        connection = insta485.model.get_db()

        if "logged_user" not in flask.session:
            abort(403)

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()
        profPic = user["filename"]

        #probably still need to delete posts right?

        profpic_deleter(profPic)

        cur = connection.execute(
            '''DELETE FROM users
               WHERE username = ?''',
               (flask.session["logged_user"], ))

        connection.commit()
        flask.session.clear()
        return flask.redirect(flask.url_for("login"))

    else:
        return flask.render_template("account_delete.html")


@insta485.app.route("/accounts/password/", methods=['GET', 'POST'])
def change_password():
    """Change Password"""

    if flask.request.method == "POST":
        connection = insta485.model.get_db()

        old_password = request.form.get("password")
        new_password1 = request.form.get("new_password1")
        new_password2 = request.form.get("new_password2")

        if old_password == "" or new_password1 == "" or new_password2 == "":
            flask.flash("Empty field.")
            abort(400)

        if new_password1 != new_password2:
            flask.flash("New passwords do not match.")
            abort(401)

        if old_password == new_password1:
            flask.flash("Old and new passwords are the same.")
            return flask.redirect(flask.url_for("change_password"))

        cur = connection.execute(
            '''SELECT *
            FROM users
            WHERE username = ?''',
            (flask.session["logged_user"], )
        )

        user = cur.fetchone()

        if not check_password(old_password, user["password"]):
            flask.flash("Incorrect current password.")
            abort(403)

        updated_password = generate_password(new_password1)
        cur = connection.execute(
            '''UPDATE users
               SET password = ?
               WHERE username = ?''',
               (updated_password, flask.session["logged_user"])
        )

        connection.commit()

        return flask.redirect(flask.url_for("edit"))

    else:
        return flask.render_template("account_password.html")

@insta485.app.route('/uploads/<filename>', methods=['GET'])
def get_static_file(filename):
    return flask.redirect(f'/static/uploads/{filename}')
