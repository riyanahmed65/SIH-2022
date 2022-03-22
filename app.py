import pymysql.cursors
from flask import Flask, render_template, request, redirect
from pymysql import connect
import random
import string

app = Flask(__name__)

connection = connect(
    host='127.0.0.1',
    port=3306,
    user='auth_system',
    password='auth_system',
    database='prod')


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/url/<url>')
def start_assessment(url: string):
    email = request.form.get('email')
    if not email:
        return render_template('start-assessment.html', start=True, authenticated=False, url=url)
    else:
        return render_template('start-assessment.html', start=False, authenticated=False, url=url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM faculty WHERE username = '{0}';".format(username))
            data = cursor.fetchone()
            if data is None or data[5] != password:
                return render_template('incorrect-password.html')
        return render_template('dashboard.html', username=username, url=None)
    else:
        return render_template('faculty-login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    return 'register'


@app.route('/create-form', methods=['POST'])
def create_form():
    new = request.form.get('new')
    url = None
    username = request.form.get('username')
    if new:
        render_template('dashboard.html', url=url, username=username)
    url = request.form.get('url')
    form_url = generate_url(url)
    return render_template('dashboard.html', url=form_url, username=username)


@app.route('/validate', methods=['POST'])
def validate():
    email = request.form.get('email')
    url = request.form.get('url')
    print(url)
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users u JOIN aadhaar_auth aa ON u.email_address = aa.user_email WHERE u.email_address = '{0}';".format(email))
        result = cursor.fetchone()
        if result:
            cursor.execute('select * from forms where generated_form_url = \'url/{0}\''.format(url))
            url = cursor.fetchone()
            if url:
                url = url[1]
            return render_template('start-assessment.html', start=False, authenticated=True, url=url)
    return render_template('start-assessment.html', start=False, authenticated=False, url=url)


def generate_url(url):
    global connection
    size = 40
    char = string.ascii_lowercase + string.ascii_uppercase + string.digits
    generated_url = 'url/' + ''.join(random.choice(char) for _ in range(size))
    with connection.cursor() as cursor:
        cursor.execute("insert into forms (form_url, generated_form_url) values (\'{0}\', '{1}');".format(url, generated_url))
        connection.commit()
    return generated_url


if __name__ == '__main__':
    app.run()
