import os
import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (int(post_id),)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route('/')
@app.route('/<string:slug>')
def index(slug=None):
    if not slug:
        return render_template('index.html')
    else:
        return render_template(slug + '.html')


@app.route('/posts/', methods=('GET', 'POST', 'DELETE', 'PATCH'))
@app.route('/posts/<int:post_id>')
def posts_api(post_id=None):
    conn = get_db_connection()
    if request.method == 'GET':
        if post_id:
            post = get_post(post_id)
            return render_template('posts-detail.html', post=post)
        else:
            posts = conn.execute('SELECT * FROM posts').fetchall()
            return render_template('posts-list.html', posts=posts)

    elif request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    elif request.method == 'DELETE':
        input_json = request.get_json(force=True) 
        dictToReturn = {
                        "post_id" : input_json["post_id"]
                       }
        post_id = int(dictToReturn["post_id"])
        post = get_post(post_id)
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    elif request.method == 'PATCH':
        input_json = request.get_json(force=True) 
        dictToReturn = {
                        "post_id" : input_json["post_id"],
                        'title' : input_json['title'],
                        'content' : input_json['content']
                       }
        post_id = int(dictToReturn['post_id'])
        title = dictToReturn['title']
        content = dictToReturn['content']

        if not title:
            return('Title is required!')
        else:
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, post_id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    else:
        flash('Method not allowed')
        return redirect(url_for('index'))


if __name__ == ('__main__'):
    app.run(debug=True)
