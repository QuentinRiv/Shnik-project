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

# class Image(db.Model):
#     id = db.Column(db.Integer, primary_key=True)    # Clé primaire
#     image_path = db.Column(db.String(200), nullable=False, unique=True)
#     info = db.relationship('Variante', backref='lName')

#     # Function that gonna returns a string everytime we create a new element
#     def __repr__(self):
#         return '<Im %r>' % self.id

# class Variante(db.Model):
#     id = db.Column(db.Integer, primary_key=True)    # Clé primaire
#     name = db.Column(db.String(1000), default="")
#     count = db.Column(db.Integer, default=0)
#     im_id = db.Column(db.Integer, db.ForeignKey('image.id'))

#     # Function that gonna returns a string everytime we create a new element
#     def __repr__(self):
#         return '<Var %r>' % self.id


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # Clé primaire
    name = db.Column(db.String(50), nullable=False, unique=True)
    image_path = db.Column(db.String(200), nullable=False, unique=True)
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


liste1 = ["chat.jpg", ["chat","cat","gatto"], ["0","0","0"]]
liste2 = ["chien.jpg", ["chien","dog","cane"], ["0","0","0"]]
liste3 = ["loup.jpg", ["loup","wolf","luppo"], ["0","0","0"]]
liste4 = ["poisson.jpg", ["poisson","fish","pesce"], ["0","0","0"]]
liste5 = ["lapin.jpg", ["lapin","bunny","caniglio"], ["0", "0", "0"]]

biglist = [liste1, liste2, liste3, liste4, liste5]

# def fillDB():
#     for liste in biglist:
#         full_filename = os.path.join(app.config['UPLOAD_FOLDER'], liste[0])
#         newIm = Image(image_path=full_filename)
#         db.session.add(newIm)
#         for j, mots in enumerate(liste[1]):
#             newVar = Variante(name=mots, lName=newIm)
#             try:
#                 db.session.add(newVar)    # Rajoute la tâche
#                 db.session.commit()
#             except:
#                 return "appblème pour le commit"


path = "C:\\Users\\quent\\Desktop\\Projet\\words_albanian.txt"
def fillDB(path):
    file1 = open(path, 'r')
    lines = file1.readlines()
    words = []
    for line in lines[2:]:
        if line != '\n':
            words += [line[:-1]]
    print(words)
    for word in words:
        newIm = Image(name=word, image_path='/static/data/leksik/' + word + '.jpg')
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
        http_addr = request.environ['REMOTE_ADDR']
    else:
        http_addr = request.environ['HTTP_X_FORWARDED_FOR']
    
    if 'X-Forwarded-For' in request.headers:
        proxy_data = request.headers['X-Forwarded-For']
        ip_list = proxy_data.split(',')
        # user_ip = ip_list[0]  # first address in list is User IP
    else:
        ip_list = request.remote_addr  # For local development

    routes = request.access_route

    if request.environ.getlist("HTTP_X_FORWARDED_FOR"):
       ip_forward_list = request.environ.getlist("HTTP_X_FORWARDED_FOR")
    else:
        ip_forward_list = 'rien du tout'

    if request.environ.get("HTTP_X_FORWARDED_FOR"):
        ip_forward = request.environ.get("HTTP_X_FORWARDED_FOR")
    else:
        ip_forward = 'rien du tout'

    return jsonify({'remote_addr': remote_addr, 'ip_add': ip_add,
                    'http_addr': http_addr, 'ip_list': ip_list,
                    'routes': routes, 'ip_forward_list': ip_forward_list,
                    'ip_forward': ip_forward}), 200
 

@app.route('/', methods=['POST', 'GET'])
def home():
    # fillDB(path)
    remote_addr = request.environ['REMOTE_ADDR']
    ip_add = request.remote_addr
    accept_ip = ["10.39.236.138", "127.0.0.1",
                 "176.153.30.138", "10.39.211.254"]

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        http_addr = request.environ['REMOTE_ADDR']
    else:
        http_addr = request.environ['HTTP_X_FORWARDED_FOR']

    # if (ip_address in accept_ip):
    #     return render_template('welcome.html', remote_addr=remote_addr, ip_add=ip_add)
    # else:
    #     return "Not accepted, Mr. " + request.environ['REMOTE_ADDR']
    return render_template('welcome.html', remote_addr=remote_addr, ip_add=ip_add, http_addr=http_addr)

def str2arr(string):
    return (string).split(',')

def arr2str(array):
    return ','.join(array)

@app.route('/random')
def randomIm():
    id = random.randint(1,5)
    return redirect('/display/'+str(id))


@app.route('/essai', methods=['POST', 'GET'])
def bidule():
    if request.method == 'GET':
        return render_template('indexx.html')

@app.route('/test/<string:name>', methods=['POST', 'GET'])
def index(name):
    image_query = Image.query.filter_by(name=name).first()                  # Get the corresponding image
    vars = image_query.info                                             # Get the variantes of the images
    words = np.array([vari.name for vari in vars])                     # Put the words into an array (np is used to sort)
    scores = np.array([vari.count for vari in vars])                    # Get the scores
    path_im = image_query.image_path                                    # Path of the image

    # Order the words, according to their score
    ordre = scores.argsort()[::-1]
    path_im = image_query.image_path
    sorted_words = words[ordre].tolist()

    print(sorted_words)

    return jsonify({'path': path_im, 'words': sorted_words})


@app.route("/addDB", methods=["POST"])
def create_entry():

    # Get the JSON data
    req = request.get_json(force=True)

    print("Req = ")
    print(req)

    # Get the info for adding the new word(s)
    name = req['name']
    new_words = req['newwords']
    image_query = Image.query.filter_by(name=name).first()

    if (new_words != ""):
        newVar = Variante(name=new_words, count='1', lName=image_query)
        try:
            db.session.add(newVar)
            db.session.commit()
        except:
            return "problème pour le commit"

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

@app.route("/display/<string:name>", methods=['GET'])
def display(name):
    print("name")
    # look at all the database content in the order they were created, and return all of them
    image_query = Image.query.filter_by(name=name).first()                  # Get the corresponding image
    vars = image_query.info                                             # Get the variantes of the images
    words = np.array([vari.name for vari in vars]).tolist()            # Put the words into an array (np is used to sort)
    scores = np.array([vari.count for vari in vars]).tolist()           # Get the scores
    path_im = image_query.image_path                                    # Path of the image

    return jsonify({'path': path_im, 'words': words, 'count': scores})

# Route to delete a word in a database, given the index of an image
@app.route("/delete", methods=["POST"])
def delete_entry():

    # Get the JSON data
    req = request.get_json(force=True)

    print(req)  # Just print what we received

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
        dico[image.name] = {'variance': names_ordered,
                            'scores': scores_ordered,
                            'flag': flags_ordered}
        dico['names'] += [image.name]
    # vars = image_query.info
    # words = np.array([vari.name for vari in vars]).tolist()
    # scores = np.array([vari.count for vari in vars]).tolist()
    # path_im = image_query.image_path
    return jsonify(dico)

if __name__ == "__main__":
    app.run(debug=True)
