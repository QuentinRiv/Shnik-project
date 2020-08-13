from flask import Flask, render_template, url_for, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import random
import numpy as np
from flask import jsonify
from flask_cors import CORS


# Initialisation
app = Flask(__name__)

CORS(app, supports_credentials=True)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///leksik.db'     # Tell our app where the database is located

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

# initialise the db, with the setting of our app
db = SQLAlchemy(app)



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

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Var %r>' % self.id



path = "C:\\Users\\quent\\Desktop\\Projet\\words_albanian.txt"
path_transl = "C:\\Users\\quent\\Desktop\\Projet\\transl_alb.txt"
def fillDB(path):
    file1 = open(path, 'r', encoding='utf-8')
    lines = file1.readlines()
    words = []
    for line in lines[2:]:
        if line != '\n':
            words += [line[:-1]]

    file2 = open(path_transl, 'r', encoding='utf-8')
    lines_transl = file2.readlines()
    words2 = []
    for line in lines_transl[2:]:
        if line != '\n':
            words2 += [line[:-1]]

    print(words)
    for i, word in enumerate(words):
        newIm = Image(name=word, image_path='/static/data/leksik/' + word + '.jpg')
        newVar = Variante(name=words2[i], lName=newIm)
        db.session.add(newIm)
        db.session.add(newVar)
        try:
            db.session.commit()
        except:
            print("***Problème***")
            return "Problème pour le commit"
    print("DB correctly done")
    file1.close()

    return jsonify(dico), 200


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

@app.route('/')
def home():
    if checkip() != 'OK':
        return make_response(jsonify({"message": checkip()}), 200)
    # fillDB(path)

    return render_template('welcome.html')




@app.route('/image/<string:name>', methods=['POST', 'GET'])
def index(name):
    image_query = Image.query.filter_by(name=name).first()                  # Get the corresponding image
    vars = image_query.info                                                 # Get the variantes of the images
    words = np.array([vari.name for vari in vars])                          # Put the words into an array (np is used to sort)
    scores = np.array([vari.count for vari in vars])                        # Get the scores
    path_im = image_query.image_path                                        # Path of the image

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

    print("Req = ")
    print(req)

    # Get the info for adding the new word(s)
    name = req['name']
    new_words = req['newwords'].lower()
    image_query = Image.query.filter_by(name=name).first()
    image_query.nb_ans += 1

    # Add new words
    if (new_words != ""):
        newVar = Variante(name=new_words, count='1', lName=image_query)
        try:
            db.session.add(newVar)
            db.session.commit()
        except:
            return "problème pour le commit"

    # +1 for selected words
    selected = req['selwords']
    if (selected != []):
        for selection in selected:
            selElem = Variante.query.filter_by(name=selection).first()
            selElem.count += 1
            try:
                db.session.commit()
                print("MAJ ok")
            except:
                return "Problème pour le commit"

    # Flag the words
    flagge = req['flagwords']
    if (flagge != []):
        for flag_word in flagge:
            selElem = Variante.query.filter_by(name=flag_word).first()
            selElem.flag += 1
            try:
                db.session.commit()
                print("MAJ ok")
            except:
                return "Problème pour le commit"

    return make_response(jsonify({"message": "OK : word(s) added"}), 200)


# Route to delete a word in a database, given the index of an image
@app.route("/delete", methods=["POST"])
def delete_entry():

    # Get the JSON data
    req = request.get_json(force=True)

    # Get the info for adding the new word(s)
    name = req['name']
    image_query = Image.query.filter_by(name=name).first()

    for w2del in req['selwords']:
        elem2del = Variante.query.filter_by(name=w2del).first()

        try:
            db.session.delete(elem2del)
            db.session.commit()     # Update
        except:
            return make_response(jsonify({"message": "Problem to delete in the database"}), 404)

    # Response we hope to return
    return make_response(jsonify({"message": "OK : Word(s) deleted"}), 200)


@app.route('/stats')
def stats():
    return render_template('stats.html')

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
        order = scores.argsort()
        names_ordered = names[order].tolist()
        scores_ordered = np.sort(scores).tolist()
        flags_ordered = flags[order].tolist()
        nb_ans = image.nb_ans
        dico[image.name] = {'variance': names_ordered,
                            'scores': scores_ordered,
                            'flag': flags_ordered,
                            'nb_ans': nb_ans}
        dico['names'] += [image.name]


    return jsonify(dico)



if __name__ == "__main__":
    app.run(debug=True)
