from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from util import convert

db = SQLAlchemy()


def init_app(app):
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    db.init_app(app)


# [START model]
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    reservation = db.relationship('Reservation', lazy=False, uselist=False)

    def __repr__(self):
        return "<User(name='%s', email=%s, reservation=%s)" % (self.name, self.email, self.reservation)


class Garage(db.Model):
    __tablename__ = 'garages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    spots = db.relationship('Spot', backref='garage', lazy=False)

    def __repr__(self):
        return "<Garage(name='%s', address=%s)" % (self.name, self.address)


class Spot(db.Model):
    __tablename__ = 'spots'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    garage_id = db.Column(db.Integer, db.ForeignKey('garages.id'), nullable=False)
    location = db.Column(db.String(255), nullable=False, unique=True)
    reservation = db.relationship('Reservation', lazy=False, uselist=False)

    def __repr__(self):
        return "<Spot(location='%s')" % self.location


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    occupied = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('spots.id'), nullable=False, unique=True)
    time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<Reservation(occupied='%s', time=%s)" % (self.occupied, self.time)


# [END model]


def authenticate(email, password):
    return (User.query
            .filter(User.email == email)
            .filter(User.password == password)
            .first())


def abort(reservation: Reservation):
    db.session.delete(reservation)
    db.session.commit()


def validate(reservation: Reservation):
    if reservation is None or reservation.occupied is True:
        return True
    else:
        expiry = reservation.time
        return expiry > datetime.now()


def refresh():
    garages = many(Garage)
    for garage in garages:
        for spot in garage.spots:
            reservation = spot.reservation
            if not validate(reservation):
                abort(reservation)


def details(user_id):
    existing_reservation = one(User, user_id).reservation

    if existing_reservation is not None:
        if validate(existing_reservation):
            return convert(one(Spot, existing_reservation.spot_id))

    refresh()

    return convert(many(Garage))


def reserve(user_id, garage_id):
    spot = (Spot.query
            .filter(Spot.garage_id == garage_id)
            .filter_by(reservation=None)
            .first())

    new_reservation = {
        'occupied': False,
        'user_id': user_id,
        'spot_id': spot.id,
        'time': datetime.now() + timedelta(seconds=10)
    }

    create(Reservation, new_reservation)
    return True


def occupy(reservation_id):
    reservation = one(Reservation, reservation_id)
    setattr(reservation, 'occupied', True)
    setattr(reservation, 'time', datetime.now())
    db.session.commit()
    return True


def many(model):
    return list(model.query.all())


def one(model, key):
    result = model.query.get(key)
    if not result:
        return None
    return result


def create(model, data):
    row = model(**data)
    db.session.add(row)
    db.session.commit()
    return row


def update(data, id):
    user = User.query.get(id)
    for k, v in data.items():
        setattr(user, k, v)
    db.session.commit()
    return user


def delete(key):
    User.query.get(key).delete()
    db.session.commit()


def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
