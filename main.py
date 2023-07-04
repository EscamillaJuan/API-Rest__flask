from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

api_key = 'TopSecretAPIKey'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def conv_to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def get_random_cafe():
    cafes = db.session.query(Cafe).all()
    cafe = random.choice(cafes)
    return jsonify(cafe=cafe.conv_to_dict())


@app.route('/all')
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.conv_to_dict() for cafe in cafes])


@app.route('/search')
def search_cafe():
    location = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=location).first()
    if cafe:
        return jsonify(cafe.conv_to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route('/add', methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    price = request.args.get('new_price')
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that ID is not found in the database."}), 404


@app.route('/report-closed/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    key = request.args.get("api-key")
    cafe = db.session.query(Cafe).get(cafe_id)
    if key == api_key:
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"Success": "Successfully deleted the cafe."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry, a cafe with that ID is not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that is not allowed, make sure you have the correct key"}), 401


if __name__ == '__main__':
    app.run(debug=True)
