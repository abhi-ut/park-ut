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
    spots = db.relationship('Spot', lazy=False)

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
    time = db.Column(db.DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return "<Reservation(occupied='%s', time=%s)" % (self.occupied, self.time)


# [END model]


def abort(reservation: Reservation):
    db.session.delete(reservation)
    db.session.commit()


def admin(email, password):
    return (User.query
            .filter(User.email == email)
            .filter(User.password == password)
            .filter_by(admin=True)
            .first())


def authenticate(email, password):
    return (User.query
            .filter(User.email == email)
            .filter(User.password == password)
            .first())


def cascade(model, key):
    obj = one(model, key)
    if obj.reservation is not None:
        db.session.delete(obj.reservation)
    db.session.delete(obj)
    db.session.commit()


def clear(user_id):
    reservation = one(User, user_id).reservation
    db.session.delete(reservation)
    db.session.commit()
    return True


def create(model, data):
    row = model(**data)
    db.session.add(row)
    db.session.commit()


def delete(model, key):
    model.query.filter_by(id=key).delete()
    db.session.commit()


def details(reservation: Reservation):
    spot = one(Spot, reservation.spot_id)
    garage_dict = convert(one(Garage, spot.garage_id))
    garage_dict['spot'] = convert(spot)
    garage_dict.pop('spots')
    return garage_dict


def garages():
    refresh()
    return convert(many(Garage))


def reservations():
    result = []
    for reservation in many(Reservation):
        if validate(reservation):
            if reservation.occupied is False:
                spot = one(Spot, reservation.spot_id)
                reservation_dict = convert(reservation)
                reservation_dict['spot_location'] = spot.location
                result.append(reservation_dict)
        else:
            abort(reservation)

    return result


def inform(user_id):
    existing_reservation = one(User, user_id).reservation

    if existing_reservation is not None:
        if validate(existing_reservation):
            return details(existing_reservation)

    return garages()


def kill(user_id):
    cascade(User, user_id)


def many(model: db.Model):
    return model.query.all()


def occupy(user_id):
    reservation = one(User, user_id).reservation
    setattr(reservation, 'occupied', True)
    setattr(reservation, 'time', datetime.now())
    db.session.commit()
    return True


def one(model: db.Model, key):
    result = model.query.get(key)
    if not result:
        return None
    return result


def plebs():
    return User.query.filter_by(admin=False).all()


def refresh():
    for reservation in many(Reservation):
        if not validate(reservation):
            abort(reservation)


def register(data):
    if data['password'] != data['passwordDuplicate']:
        raise ValueError('Passwords do not match')
    if data['email'] is '' or data['password'] is '':
        raise ValueError('Empty email address or password')

    data.pop('passwordDuplicate')
    data['admin'] = False
    create(User, data)


def remove(spot_id):
    cascade(Spot, spot_id)


def reserve(user_id, garage_id):
    spot = (Spot.query
            .filter(Spot.garage_id == garage_id)
            .filter_by(reservation=None)
            .first())

    reservation = {
        'occupied': False,
        'user_id': user_id,
        'spot_id': spot.id,
        'time': datetime.now() + timedelta(minutes=10)
    }

    create(Reservation, reservation)
    return True


def spots():
    refresh()
    return convert(many(Spot))


def validate(reservation: Reservation):
    return reservation is None or reservation.occupied is True or reservation.time > datetime.now()


# _____

def _create_database():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    init_app(app)
    with app.app_context():
        db.create_all()
    print("All tables created")


if __name__ == '__main__':
    _create_database()
