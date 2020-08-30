from flask import Flask, render_template, url_for, request, redirect, make_response
from flask import jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from flask_cors import CORS
from flask_login import UserMixin, LoginManager
from flask_login import login_required, current_user
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
import os
import random
import numpy as np
import requests
import json
import io
import csv



# Initialisation
app = Flask(__name__)

CORS(app, supports_credentials=True)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///leksik.db'     # Tell our app where the database is located
# Tell our app where the database is located
app.config['SECRET_KEY'] = 'secret-key-goes-here'

# initialise the db, with the setting of our app
db = SQLAlchemy(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'     # Page name to log in
login_manager.login_message = u"Nop ! You cannot access to this page..."
login_manager.init_app(app)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    name = db.Column(db.String(50), nullable=False, unique=True)
    image_path = db.Column(db.String(200), nullable=False, unique=True)
    nb_ans = db.Column(db.Integer, default=0)
    info = db.relationship('Variante', backref='lName')

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Im %r>' % self.id

class Variante(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    name = db.Column(db.String(1000), default="ABC", unique=True)
    count = db.Column(db.Integer, default=1)
    flag = db.Column(db.Integer, default=0)
    im_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    user_info = db.Column(db.String(200), nullable=False, default='default_user')

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Var %r>' % self.id

class User(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))




def fillDB():
    path = "./words_albanian.txt"
    path_transl = "./transl_alb.txt"

    try:
        file1 = open(path, 'r', encoding='utf-8')
    except:
        return make_response(jsonify({"message": "Problem to open the file " + path}), 404)

    lines = file1.readlines()
    words = []
    for line in lines[2:]:
        if line != '\n':
            words += [line[:-1]]

    try:
        file2 = open(path_transl, 'r', encoding='utf-8')
    except:
        return make_response(jsonify({"message": "Problem to open file " + path_transl}), 404)

    lines_transl = file2.readlines()
    words2 = []
    for line in lines_transl[2:]:
        if line != '\n':
            words2 += [line[:-1]]

    print(words)
    for i, word in enumerate(words):
        newIm = Image(
            name=word, image_path='/static/data/leksik/' + word + '.jpg')
        newVar = Variante(name=words2[i], lName=newIm)
        db.session.add(newIm)
        db.session.add(newVar)
        try:
            db.session.commit()
        except:
            return "Problème pour le commit"
    print("DB correctly done")
    file2.close()

    return 0

def checkip():
    website_ip = request.environ.get('HTTP_ORIGIN')
    if website_ip is None:
        if 'X-Forwarded-For' in request.headers:
            proxy_data = request.headers['X-Forwarded-For']
            ip_list = proxy_data.split(',')[0]
        else:
            ip_list = request.remote_addr  # For local development

        if ip_list not in ['127.0.0.1', '176.153.30.138']:
            return 'No Access Granted : Website is None and not good ip_list (' + ip_list + ')'

    elif website_ip != "http://130.60.24.55:5000":
        return 'No Access Granted : Wrong website_ip (' + website_ip + ')'

    return 'OK'


@app.route('/main')
def home():
    if checkip() != 'OK':
        return make_response(jsonify({"message": checkip()}), 200)
    ans = fillDB()
    if ans != 0:
        return ans

    return render_template('welcome.html')


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email,
                    name=name,
                    password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    print(user)

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect(url_for('login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('profile'))


@app.route('/stats')
@login_required
def stats():
    return render_template('stats.html')


@app.route('/download')
def post():
    response = requests.get("https://retry-unige.herokuapp.com/alldata")
    # TODO : Rajouter l'adresse du serveur
    print('\nJSON :')
    data = json.loads(response.text)
    csv_array = [
        ["IMAGE", "NANSWERS", "VARIANCES"],
    ]
    for word in data['names']:
        sCsv = ""
        mot = data[word]
        aCsv = [word, mot['nb_ans']]
        for i, vari in enumerate(data[word]['variance']):
            if sCsv != "":
                sCsv += "&"
            sCsv += "(" + str(mot['scores'][i])
            if mot['flag'][i] != 0:
                sCsv += "/" + str(mot['flag'][i])
            sCsv += ")" + vari
        aCsv += [sCsv.encode("utf-8")]
        print(aCsv)
        csv_array += [aCsv]

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(csv_array)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=shnik.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route('/image/<string:name>', methods=['POST', 'GET'])
def image(name):
    # Get the corresponding image
    image_query = Image.query.filter_by(name=name).first()

    if image_query is None:
        return 'No image found with the name ' + name
    # Get the variantes of the images
    vars = image_query.info
    # Put the words into an array (np is used to sort)
    words = np.array([vari.name for vari in vars])
    # Get the scores
    scores = np.array([vari.count for vari in vars])
    # Path of the image
    path_im = image_query.image_path

    # Order the words, according to their score
    ordre = scores.argsort()[::-1]
    path_im = image_query.image_path
    sorted_words = words[ordre].tolist()

    print(sorted_words)

    return jsonify({'path': path_im, 'words': sorted_words})


@app.route("/addDB", methods=["POST"])
def create_entry():

    if checkip() != 'OK':
        return make_response(jsonify({"message": checkip()}), 200)

    # Get the JSON data
    req = request.get_json(force=True)

    print("Req = \n", req)

    # Get the info for adding the new word(s)
    name = req['name']
    user_info = req['user_data']
    new_words = req['newwords'].lower()
    image_query = Image.query.filter_by(name=name).first()

    if image_query is None:
        return 'No image found with the name ' + name

    image_query.nb_ans += 1     # Update the number of answer

    # Add new words
    if (new_words != []):
        for new_word in new_words:
            [email, id, fullname] = user_info.split(',')
            newVar = Variante(name=new_word, count='1', lName=image_query, user_info=email+','+id+','+fullname)
            try:
                db.session.add(newVar)
                db.session.commit()
            except:
                return "problem for the commit"

    # +1 for selected words
    selected = req['selwords']
    if (selected != []):
        for selection in selected:
            selElem = Variante.query.filter_by(name=selection).first()
            if selElem is None:
                return 'No Variance found with the name ' + selection
            selElem.count += 1
            try:
                db.session.commit()
            except:
                return "problem for the commit"

    # Flag the words
    flagge = req['flagwords']
    if (flagge != []):
        for flag_word in set(flagge):
            selElem = Variante.query.filter_by(name=flag_word).first()
            if selElem is None:
                return 'No Variance found with the name ' + flag_word
            selElem.flag += 1
            try:
                db.session.commit()
            except:
                return "problem for the commit"

    return make_response(jsonify({"message": "OK : word(s) added"}), 200)


# Route to delete a word in a database, given the index of an image
@app.route("/delete", methods=["POST"])
def delete_entry():

    # Get the JSON data
    req = request.get_json(force=True)

    # Get the info for adding the new word(s)
    name = req['name']
    image_query = Image.query.filter_by(name=name).first()

    if image_query is None:
        return 'No image found with the name ' + name

    for w2del in req['selwords']:
        elem2del = Variante.query.filter_by(name=w2del).first()

        try:
            db.session.delete(elem2del)
            db.session.commit()     # Update
        except SQLAlchemyError as e:
            return make_response(jsonify({"message": "Problem to delete in the database  => " + e}), 404)

    # Response we hope to return
    return make_response(jsonify({"message": "OK : Word(s) deleted"}), 200)


# @app.route('/stats')
# def stats():
#     return render_template('stats.html')


@app.route('/alldata')
def data():
    # Get the corresponding image
    dico = {}
    all_ims = Image.query.all()
    dico['names'] = []
    for image in all_ims:
        vars = image.info
        names = np.array([var.name for var in vars])
        scores = np.array([var.count for var in vars])
        flags = np.array([var.flag for var in vars])
        user_info = np.array([var.user_info for var in vars])
        order = scores.argsort()[::-1]
        names_ordered = names[order].tolist()
        scores_ordered = np.sort(scores).tolist()[::-1]
        flags_ordered = flags[order].tolist()
        u_info_ordered = user_info[order].tolist()
        nb_ans = image.nb_ans
        dico[image.name] = {'variance': names_ordered,
                            'scores': scores_ordered,
                            'flag': flags_ordered,
                            'nb_ans': nb_ans,
                            'user_info' : u_info_ordered}
        dico['names'] += [image.name]

    return jsonify(dico)


if __name__ == "__main__":
    app.run(debug=True)
