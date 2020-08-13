from flask_cors import CORS
import numpy as np
from flask import Flask, render_template, url_for, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import random
from flask import jsonify

# Initialisation
pro = Flask(__name__)
# "///" = relative path ("//"" = absolute path)
# Tell our pro where the database is located
pro.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test_lexiq.db'
# everything will be stored in the database test.db

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
pro.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

# initialise the db, with the setting of our pro
db = SQLAlchemy(pro)


class Lexiq(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    # Contenu de la tâche (nullable = False pour éviter de créer une tâche vide)
    image_path = db.Column(db.String(200), nullable=False, unique=True)
    names = db.Column(db.String(1000), default="")
    count = db.Column(db.String(100), default="")

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Lexiq %r>' % self.id


liste1 = ["chat.jpg", "chat,cat,gatto", "0,0,0"]
liste2 = ["chien.jpg", "chien,dog,cane", "0,0,0"]
liste3 = ["loup.jpg", "loup,wolf,luppo", "0,0,0"]
liste4 = ["poisson.jpg", "poisson,fish,pesce", "0,0,0"]
liste5 = ["lapin.jpg", "lapin,bunny,caniglio", "0,0,0"]

biglist = [liste1, liste2, liste3, liste4, liste5]


def fillDB():
    for liste in biglist:
        full_filename = os.path.join(pro.config['UPLOAD_FOLDER'], liste[0])
        new_elem = Lexiq(image_path=full_filename,
                         names=liste[1], count=liste[2])
        try:
            db.session.add(new_elem)    # Rajoute la tâche
            db.session.commit()
        except:
            return "Problème pour le commit"


@pro.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


@pro.route('/', methods=['POST', 'GET'])
def home():
    # fillDB()
    return render_template('welcome.html')


@pro.route('/traitement/<int:id>', methods=['POST', 'GET'])
def trait(id):
    if request.method == 'POST':    # If the request set for this route is set, do stuff there
        liste_query = Lexiq.query.filter_by(id=id).first()
        try:
            valeur = request.form['valeur']
        except:
            valeur = ""
        if (valeur == ""):      # Endroit où on récupère la nouvelle valeur entrée
            new_val = request.form['autre_valeur']
            liste_query.names += ","+new_val
            liste_query.count += ","+"0"
            try:
                db.session.commit()
            except:
                return "Problème pour le commit"
        else:  # Entrée déjà existante
            valeur = request.form['valeur']
            mots = (liste_query.names).split(',')
            score = (liste_query.count).split(',')
            posi = next((i for i, j in enumerate(mots) if j == valeur), None)
            score[posi] = str(int(score[posi])+1)
            liste_query.count = ','.join(score)
            try:
                db.session.commit()
            except:
                return "Problème pour le commit"

        ind = random.randint(1, 5)
        return redirect('/'+str(ind))
    else:
        return "ERROR"


def str2arr(string):
    return (string).split(',')


def arr2str(array):
    return ','.join(array)


@pro.route('/delete/<int:id>/<int:id2>')
def delete(id, id2):
    liste_query = Lexiq.query.filter_by(
        id=id).first()      # Get the correct element
    mots = str2arr(liste_query.names)
    score = str2arr(liste_query.count)
    del mots[id2]
    del score[id2]
    liste_query.names = arr2str(mots)
    liste_query.count = arr2str(score)
    try:
        db.session.commit()
    except:
        return "Problème pour le commit"
    return redirect('/'+str(id))

# Par défaut, on a juste ma méthode GET


@pro.route('/<int:id>', methods=['POST', 'GET'])
def index2(id):
    if request.method == 'POST':    # If the request set for this route is set, do stuff there
        liste_query = Lexiq.query.filter_by(id=id).first()
        try:
            valeur = request.form['valeur']
        except:
            valeur = ""

        if (valeur == ""):    # Endroit où on récupère la nouvelle valeur entrée
            new_val = request.form['autre_valeur']
            liste_query.names += "," + new_val
            try:
                db.session.commit()
            except:
                return "Problème pour le commit"
        else:  # Entrée déjà existante
            valeur = request.form['valeur']
            mots = str2arr(liste_query.names)
            posi = next((i for i, j in enumerate(mots) if j == valeur), None)

        ind = random.randint(1, 5)      # Random next new page
        return redirect('/'+str(ind))

    else:       # Partie affichage
        # look at all the database content in the order they were created, and return all of them
        liste_query = Lexiq.query.filter_by(id=id).first()

        mots = str2arr(liste_query.names)
        score = str2arr(liste_query.count)
        return render_template('index2.html', liste=mots, user_image=liste_query.image_path, taille=len(mots), id=id, count=score)

# @pro.route('/test/<int:id>', methods=['POST', 'GET'])
# def index3(id):
#     sortie = {'msg' : id}
#     name = request.json['name']
#     return jsonify(sortie)


@pro.route('/machin', methods=['POST', 'GET'])
def bidule():
    if request.method == 'GET':
        return render_template('indexx.html')


@pro.route('/test/<int:id>', methods=['POST', 'GET'])
def index2test(id):
    print("Bienvenu !")
    if request.method == 'POST':    # If the request set for this route is set, do stuff there
        liste_query = Lexiq.query.filter_by(id=id).first()
        try:
            valeur = request.form['valeur']
        except:
            valeur = ""

        if (valeur == ""):    # Endroit où on récupère la nouvelle valeur entrée
            new_val = request.form['autre_valeur']
            liste_query.names += "," + new_val
            try:
                db.session.commit()
            except:
                return "Problème pour le commit"
        else:  # Entrée déjà existante
            valeur = request.form['valeur']
            mots = str2arr(liste_query.names)
            posi = next((i for i, j in enumerate(mots) if j == valeur), None)

        ind = random.randint(1, 5)      # Random next new page
        return redirect('/'+str(ind))

    else:       # Partie affichage
        # look at all the database content in the order they were created, and return all of them
        liste_query = Lexiq.query.filter_by(id=id).first()
        print("GET demandé !")

        id = liste_query.id
        path_im = liste_query.image_path
        mots = str2arr(liste_query.names)
        score = str2arr(liste_query.count)

        return jsonify({'path': path_im, 'words': mots})


@pro.route("/addDB", methods=["POST"])
def create_entry():

    req = request.get_json()

    print(req)

    res = make_response(jsonify({"message": "OK"}), 200)

    id = req['id']
    liste_query = Lexiq.query.filter_by(id=id).first()

    return res


if __name__ == "__main__":
    pro.run(debug=True)



#########################################################


# -*- coding: utf-8 -*-

# from werkzeug.contrib.fixers import ProxyFix


# Initialisation
app = Flask(__name__)

CORS(app, supports_credentials=True)
# Tell our app where the database is located
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///leksik.db'

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


def fillDB(path):
    file1 = open(path, 'r', encoding='utf-8')
    lines = file1.readlines()
    words = []
    for line in lines[2:]:
        if line != '\n':
            words += [line[:-1]]
    print(words)
    for word in words:
        newIm = Image(
            name=word, image_path='/static/data/leksik/' + word + '.jpg')
        newVar = Variante(name=word, lName=newIm)
        db.session.add(newIm)
        db.session.add(newVar)
        try:
            db.session.commit()
        except:
            print("***Problème***")
            return "Problème pour le commit"
    print("DB correctly done")
    file1.close()


@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():

    remote_addr = request.environ['REMOTE_ADDR']
    ip_add = request.remote_addr

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        http_addr = 'pas interessant'
    else:
        http_addr = request.environ['HTTP_X_FORWARDED_FOR']

    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
    else:
        ip_list = request.remote_addr  # For local development

    print(request.environ)
    print(type(request.environ))

    dico = {}
    all_key = ['REQUEST_METHOD',  'PATH_INFO',
               'SERVER_PORT',     'HTTP_HOST',
               'HTTP_USER_AGENT', 'HTTP_ACCESS_CONTROL_ALLOW_ORIGIN',
               'HTTP_ORIGIN',     'HTTP_X_REQUEST_ID',
               'HTTP_X_REQUEST_FOR',  'HTTP_X_REQUEST_PROTO',
               'HTTP_VIA',        'REMOTE_ADDR'
               ]

    arr_key = []
    for key in request.environ:
        arr_key += [key]
        if key in all_key:
            dico[key] = request.environ.get(key)

    dico['AAA'] = arr_key
    dico['ip_list'] = ip_list

    print('Dico : \n', dico)

    return jsonify(dico), 200

    # return jsonify({'remote_addr': remote_addr, 'ip_add': ip_add,
    #                 'http_addr': http_addr, 'ip_list': ip_list,
    #                 'routes': routes, 'ip_forward_list': ip_forward_list,
    #                 'ip_forward': ip_forward}), 200


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


@app.route('/', methods=['POST', 'GET'])
def home():
    if checkip() != 'OK':
        return make_response(jsonify({"message": checkip()}), 200)
    fillDB(path)

    return render_template('welcome.html')


@app.route('/image/<string:name>', methods=['POST', 'GET'])
def index(name):
    # Get the corresponding image
    image_query = Image.query.filter_by(name=name).first()
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

    print("Req = ")
    print(req)

    # Get the info for adding the new word(s)
    name = req['name']
    new_words = req['newwords']
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
