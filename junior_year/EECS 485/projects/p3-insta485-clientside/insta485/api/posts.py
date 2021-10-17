"""REST API for posts."""
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

def check_password(password, password_db_string):
    [algorithm, salt, password_hash] = password_db_string.split("$")
    hash_obj = hashlib.new(algorithm)
    password_salted = salt + password
    hash_obj.update(password_salted.encode('utf-8'))
    return hash_obj.hexdigest() == password_hash

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		connection = insta485.model.get_db()
		if 'logged_user' not in flask.session:
			try:
				username = flask.request.authorization['username']
				password = flask.request.authorization['password']
			except:
				return flask.jsonify({"message": "No credentials.", "status_code": 403}), 403

			if username == "" or password == "":
				abort(400)

			cur = connection.execute(
				'''SELECT username, password
				FROM users
				WHERE username = ?''',
				(username, )
			)

			user = cur.fetchone()

			if user == None or not check_password(password, user["password"]):
				return flask.jsonify({"message": "Invalid credentials.", "status_code": 403}), 403
			
			flask.session["logged_user"] = username

		return f(*args, **kwargs)
	return decorated_function

@insta485.app.route('/api/v1/')
def list_of_services():
	"""List of services provided by this API"""

	context = {
		"comments": "/api/v1/comments/",
		"likes": "/api/v1/likes/",
		"posts": "/api/v1/posts/",
		"url": "/api/v1/"
	}

	return flask.jsonify(**context)


@insta485.app.route('/api/v1/posts/')
@login_required
def ten_posts():
	"""Return first ten posts for a Logged User."""

	db = insta485.model.get_db()

	cur = db.execute("""SELECT * FROM posts 
						WHERE owner in (SELECT username2 FROM following WHERE username1 = ?)
						or owner = ? ORDER BY postid DESC""", (flask.session["logged_user"], flask.session["logged_user"]))
	top = cur.fetchone()["postid"]		

	page = flask.request.args.get("page", default=0, type=int)
	size = flask.request.args.get("size", default=10, type=int)
	max = flask.request.args.get("postid_lte", default=top, type=int)

	if size < 0 or page < 0:
		return flask.jsonify({"message": "Bad Request", "status_code": 400}), 400

	results = []
	cur = db.execute("""SELECT * FROM posts 
							WHERE owner in (SELECT username2 FROM following WHERE username1 = ?)
							or owner = ?
							AND postid <= ?
							ORDER BY postid DESC
							LIMIT ? OFFSET ?;""", 
							(flask.session["logged_user"], flask.session["logged_user"], max, size, page*size))
	posts = cur.fetchall()

	for post in posts:
		added_post = {}
		comments_list = []
		cur = db.execute("""SELECT * FROM comments
							WHERE postid = ?""", (post["postid"],))
		comments = cur.fetchall()
		for comment in comments:
			ind_comment = {}
			ind_comment["commentid"] = comment["commentid"]
			ind_comment["lognameOwnsThis"] = comment["owner"] == flask.session["logged_user"]
			ind_comment["owner"] = comment["owner"]
			ind_comment["ownerShowUrl"] = "/users/" + ind_comment["owner"] + "/"
			ind_comment["text"] = comment["text"]
			ind_comment["url"] = "/api/v1/comments/" + str(ind_comment["commentid"]) + "/"
			comments_list.append(ind_comment)
		added_post["comments"] = comments_list
		added_post["created"] = post["created"]
		added_post["imgUrl"] = "/uploads/" + post["filename"]

		cur = db.execute("""SELECT * FROM likes
							WHERE postid = ?""", (post["postid"],))
		likes = cur.fetchall()
		likes_dict = {}
		try:
			i_like = [x for x in likes if x["owner"] == flask.session["logged_user"]]
			likes_dict["lognameLikesThis"] = flask.session["logged_user"] == i_like[0]["owner"]
		except:
			likes_dict["lognameLikesThis"] = False

		likes_dict["numLikes"] = len(likes)
		if likes_dict["lognameLikesThis"]:
			likes_dict["url"] = "/api/v1/likes/" + str(i_like[0]["likeid"]) + "/"
		else:
			likes_dict["url"] = None

		added_post["likes"] = likes_dict
		added_post["owner"] = post["owner"]
	
		cur = db.execute("""SELECT * FROM users WHERE username = ?""", (added_post["owner"],))
		added_post["ownerImgUrl"] = "/uploads/" + cur.fetchone()["filename"]
		added_post["ownerShowUrl"] = "/users/" + added_post["owner"] + "/"
		added_post["postShowUrl"] = "/posts/" + str(post["postid"]) + "/"
		added_post["postid"] = post["postid"]
		added_post["url"] = "/api/v1" + added_post["postShowUrl"]

		results.append(added_post)

	if len(posts) < size:
		next = ""
	else:
		max1 = posts[0]["postid"]
		next = "/api/v1/posts/?size=" + str(size) + "&page=" + str(page+1) + "&postid_lte=" + str(max1)

	context = {
		"next": next,
		"results": results,
		"url": flask.request.url[(flask.request.url.find("/api")):]
	}

	return flask.jsonify(**context)



@insta485.app.route('/api/v1/posts/<int:postid_url_slug>/')
@login_required
def get_post(postid_url_slug):
	"""Return post on post id."""

	db = insta485.model.get_db()

	cur = db.execute("""SELECT * FROM posts""")
	ps = cur.fetchall()
	if postid_url_slug < 1 or postid_url_slug > len(ps):
		return flask.jsonify({"message":"Not Found", "status_code": 404}), 404

	cur = db.execute("""SELECT * FROM posts 
							WHERE postid=?;""", 
							(postid_url_slug,))
	post = cur.fetchone()

	added_post = {}
	comments_list = []
	cur = db.execute("""SELECT * FROM comments
						WHERE postid = ?""", (post["postid"],))
	comments = cur.fetchall()
	for comment in comments:
		ind_comment = {}
		ind_comment["commentid"] = comment["commentid"]
		ind_comment["lognameOwnsThis"] = comment["owner"] == flask.session["logged_user"]
		ind_comment["owner"] = comment["owner"]
		ind_comment["ownerShowUrl"] = "/users/" + ind_comment["owner"] + "/"
		ind_comment["text"] = comment["text"]
		ind_comment["url"] = "/api/v1/comments/" + str(ind_comment["commentid"]) + "/"
		comments_list.append(ind_comment)
	added_post["comments"] = comments_list
	added_post["created"] = post["created"]
	added_post["imgUrl"] = "/uploads/" + post["filename"]

	cur = db.execute("""SELECT * FROM likes
						WHERE postid = ?""", (post["postid"],))
	likes = cur.fetchall()
	likes_dict = {}
	try:
		i_like = [x for x in likes if x["owner"] == flask.session["logged_user"]]
		likes_dict["lognameLikesThis"] = flask.session["logged_user"] == i_like[0]["owner"]
	except:
		likes_dict["lognameLikesThis"] = False
	likes_dict["numLikes"] = len(likes)
	if likes_dict["lognameLikesThis"]:
		likes_dict["url"] = "/api/v1/likes/" + str(i_like[0]["likeid"]) + "/"
	else:
		likes_dict["url"] = None
	added_post["likes"] = likes_dict
	added_post["owner"] = post["owner"]

	cur = db.execute("""SELECT * FROM users WHERE username = ?""", (added_post["owner"],))
	added_post["ownerImgUrl"] = "/uploads/" + cur.fetchone()["filename"]
	added_post["ownerShowUrl"] = "/users/" + added_post["owner"] + "/"
	added_post["postShowUrl"] = "/posts/" + str(post["postid"]) + "/"
	added_post["postid"] = post["postid"]
	added_post["url"] = "/api/v1" + added_post["postShowUrl"]

	return flask.jsonify(**added_post)


@insta485.app.route('/api/v1/likes/', methods=['POST'])
@login_required
def post_liker():
	"""Like a post."""

	if flask.request.method == "POST":
		postid = flask.request.args.get("postid")
		db = insta485.model.get_db()
		cur = db.execute("""SELECT * FROM likes WHERE owner = ? AND postid = ?""",
						(flask.session["logged_user"], postid))
		if cur.fetchone() != None:
			return flask.jsonify({"message": "Conflict", "status_code": 409}), 409

		db.execute("""INSERT INTO likes (owner, postid) VALUES (?,?)""",
					(flask.session["logged_user"], postid))
		db.commit()

		cur = db.execute("""SELECT last_insert_rowid()""")
		likeid = cur.fetchone()["last_insert_rowid()"]
		context = {
			"likeid": likeid,
			"url": "/api/v1/likes/" + str(likeid) + "/"
		}

		return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
@login_required
def post_unliker(likeid):
	"""Unlike a post."""

	if flask.request.method == "DELETE":
		db = insta485.model.get_db()
		cur = db.execute("""SELECT * FROM likes WHERE likeid = ?""", (likeid,))
		if flask.session["logged_user"] != cur.fetchone()["owner"]:
			return flask.jsonify({"message": "User does not own this like.", "status_code": 403}), 403
		db.execute("""DELETE FROM likes WHERE likeid = ?""", (likeid,))
		db.commit()

		return '', 204


@insta485.app.route('/api/v1/comments/', methods=['POST'])
@login_required
def post_commenter():
	"""Comment on a post."""

	if flask.request.method == "POST":
		postid = flask.request.args.get("postid")
		text = flask.request.json["text"]
		db = insta485.model.get_db()
		db.execute("""INSERT INTO comments (owner, postid, text) VALUES (?,?,?)""",
				  (flask.session["logged_user"], postid, text))
		db.commit()
		cur = db.execute("""SELECT last_insert_rowid()""")
		commentid = cur.fetchone()["last_insert_rowid()"]
		context = {
			"commentid": commentid,
			"lognameOwnsThis": True,
			"owner": flask.session["logged_user"],
			"ownerShowUrl": "/users/" + flask.session["logged_user"] + "/",
			"text": text,
			"url": "/api/v1/comments/" + str(commentid) + "/"
		}

		return flask.jsonify(**context), 201


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
@login_required
def comment_deleter(commentid):
	"""Delete a comment from a post."""

	if flask.request.method == "DELETE":
		db = insta485.model.get_db()
		cur = db.execute("""SELECT * FROM comments WHERE commentid = ?""", (commentid,))
		if flask.session["logged_user"] != cur.fetchone()["owner"]:
			return flask.jsonify({"message": "User does not own this comment.", "status_code": 403}), 403
		db.execute("""DELETE FROM comments WHERE commentid = ?""", (commentid,))
		db.commit()

		return '', 204
