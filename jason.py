from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import os
import random
from flask import jsonify
from flask import make_response


# Initialisation
app = Flask(__name__)

@app.route("/guestbook")
def guestbook():
    return render_template("guestbook.html")

@app.route("/json", methods=["POST"])
def json_example():
    
    if request.is_json:

        req = request.get_json()

        response_body = {
            "message": "JSON received!",
            "sender": req.get("name")
        }

        res = make_response(jsonify(response_body), 200)

        return res

    else:

        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


@app.route("/guestbook/create-entry", methods=["POST"])
def create_entry():

    req = request.get_json()

    print(req)

    res = make_response(jsonify({"message": "OK"}), 200)

    return res



if __name__ == "__main__":
    app.run(debug=True)