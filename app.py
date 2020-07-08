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
# "///" = relative path ("//"" = absolute path)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test_lexiq.db'     # Tell our app where the database is located
# everything will be stored in the database test.db

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

# initialise the db, with the setting of our app
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    image_path = db.Column(db.String(200), nullable=False, unique=True)     # Contenu de la tâche (nullable = False pour éviter de créer une tâche vide)
    info = db.relationship('Variante', backref='lName')

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Im %r>' % self.id

class Variante(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    names = db.Column(db.String(1000), default="")
    count = db.Column(db.Integer, default=0)
    im_id = db.Column(db.Integer, db.ForeignKey('image.id'))

    # Function that gonna returns a string everytime we create a new element
    def __repr__(self):
        return '<Var %r>' % self.id


liste1 = ["chat.jpg", ["chat","cat","gatto"], ["0","0","0"]]
liste2 = ["chien.jpg", ["chien","dog","cane"], ["0","0","0"]]
liste3 = ["loup.jpg", ["loup","wolf","luppo"], ["0","0","0"]]
liste4 = ["poisson.jpg", ["poisson","fish","pesce"], ["0","0","0"]]
liste5 = ["lapin.jpg", ["lapin","bunny","caniglio"], ["0", "0", "0"]]

biglist = [liste1, liste2, liste3, liste4, liste5]

def fillDB():
    for liste in biglist:
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], liste[0])
        newIm = Image(image_path=full_filename)
        db.session.add(newIm)
        for j, mots in enumerate(liste[1]):
            newVar = Variante(names=mots, lName=newIm)
            try:
                db.session.add(newVar)    # Rajoute la tâche
                db.session.commit()
            except:
                return "appblème pour le commit"

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


@app.route('/', methods=['POST', 'GET'])
def home():
    fillDB()
    return render_template('welcome.html')

@app.route('/traitement/<int:id>', methods=['POST', 'GET'])
def trait(id):
    if request.method == 'POST':    # If the request set for this route is set, do stuff there
        liste_query = Image.query.filter_by(id=id).first()
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
                return "appblème pour le commit"
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
                return "appblème pour le commit"

        ind = random.randint(1, 5)
        return redirect('/'+str(ind))
    else:
        return "ERROR"

def str2arr(string):
    return (string).split(',')

def arr2str(array):
    return ','.join(array)

@app.route('/delete/<int:id>/<int:id2>')
def delete(id, id2):
    liste_query = Image.query.filter_by(id=id).first()      # Get the correct element
    mots = str2arr(liste_query.names)
    score = str2arr(liste_query.count)
    del mots[id2]
    del score[id2]
    liste_query.names = arr2str(mots)
    liste_query.count = arr2str(score)
    try:
        db.session.commit()
    except :
        return "appblème pour le commit"
    return redirect('/'+str(id))

# Par défaut, on a juste ma méthode GET
@app.route('/<int:id>', methods=['POST', 'GET'])
def index2(id):
    if request.method == 'POST':    # If the request set for this route is set, do stuff there
        liste_query = Image.query.filter_by(id=id).first()
        try:
            valeur = request.form['valeur']
        except :
            valeur = ""

        if (valeur == ""):    # Endroit où on récupère la nouvelle valeur entrée
            new_val = request.form['autre_valeur']
            liste_query.names += "," + new_val
            try:
                db.session.commit()
            except :
                return "appblème pour le commit"
        else: # Entrée déjà existante
            valeur = request.form['valeur']
            mots = str2arr(liste_query.names)
            posi = next((i for i, j in enumerate(mots) if j==valeur), None)

        ind = random.randint(1, 5)      # Random next new page
        return redirect('/'+str(ind))

    else:       # Partie affichage
        # look at all the database content in the order they were created, and return all of them
        liste_query = Image.query.filter_by(id=id).first()

        mots = str2arr(liste_query.names)
        score = str2arr(liste_query.count)
        return render_template('index2.html', liste=mots, user_image=liste_query.image_path, taille=len(mots), id=id, count=score)


@app.route('/machin', methods=['POST', 'GET'])
def bidule():
    if request.method == 'GET':
        return render_template('indexx.html')

@app.route('/test/<int:id>', methods=['POST', 'GET'])
def index2test(id):
    print("Bienvenu !")

    # look at all the database content in the order they were created, and return all of them
    image_query = Image.query.filter_by(id=id).first()
    vars = image_query.info
    motss = np.array([vari.names for vari in vars])
    counts = np.array([vari.count for vari in vars])
    print('Compte : ', counts)
    ordre = counts.argsort()[::-1]
    path_im = image_query.image_path
    new = motss[ordre].tolist()

    return jsonify({'path' : path_im , 'words' : new})


@app.route("/addDB", methods=["POST"])
def create_entry():

    req = request.get_json()

    print(req)

    res = make_response(jsonify({"message": "OK"}), 200)

    id = req['id']
    newwords = req['newwords']
    image_query = Image.query.filter_by(id=id).first()

    if (newwords != ""):    # Endroit où on récupère la nouvelle valeur entrée
        newVar = Variante(names=newwords, count='0', lName=image_query)
        try:
            db.session.add(newVar)
            db.session.commit()
        except:
            return "problème pour le commit"

    selected = req['selwords']
    if (selected != []):
        for selection in selected:
            selElem = Variante.query.filter_by(names=selection).first()
            selElem.count += 1
            try:
                db.session.commit()
                print("MAJ ok")
            except:
                return "appblème pour le commit"

    return res

@app.route("/display/<int:id>", methods=['GET'])
def display(id):
    print("Bienvenu !")

    # look at all the database content in the order they were created, and return all of them
    image_query = Image.query.filter_by(id=id).first()
    vars = image_query.info
    motss = np.array([vari.names for vari in vars])
    counts = np.array([vari.count for vari in vars])
    print('Compte : ', counts)
    ordre = counts.argsort()[::-1]
    path_im = image_query.image_path
    new = motss[ordre].tolist()

    return jsonify({'path': path_im, 'words': new, 'count': counts[ordre].tolist()})


@app.route("/delete", methods=["POST"])
def delete_entry():

    req = request.get_json()

    print(req)

    res = make_response(jsonify({"message": "OK"}), 200)

    id = req['id']
    w2del = req['selwords'][0]
    # image_query = Image.query.filter_by(id=id).first()

    elem2del = Variante.query.filter_by(names=w2del).first()

    try:
        db.session.delete(elem2del)
        db.session.commit()
    except:
        return "appblème pour la suppression"

    return res

if __name__ == "__main__":
    app.run(debug=True)
