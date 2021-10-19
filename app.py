from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3
from werkzeug.exceptions import abort


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345'


@app.route('/')
@app.route('/<string:slug>')
def index(slug=None):
    if not slug:
        return render_template('index.html')
    else:
        return render_template(slug + '.html')


@app.route('/posts/', methods=('GET', 'POST'))
@app.route('/posts/<int:post_id>', methods=('GET', 'DELETE', 'PATCH'))
def posts_api(post_id=None):
    conn = get_db_connection()
    if request.method == 'GET':
        if post_id:
            posts = get_post(post_id)
        else:
            posts = conn.execute('SELECT * FROM posts').fetchall()
        return render_template('posts.html', posts=posts)

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
        post = get_post(id)
        conn.execute('DELETE FROM posts WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('"{}" Был успешно удален!'.format(post['title']))
        return redirect(url_for('index'))

    elif request.method == 'PATCH':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    else:
        flash('Method not allowed')
        return redirect(url_for('index'))


if __name__ == ('__main__'):
    app.run(debug=True)
