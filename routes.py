from flask import request, redirect, url_for, session, jsonify, abort
import model
from util import delay

router = {
    'login': delay('login.html', ['show_register']),
    'register': delay('register.html', []),
    'admin': delay('admin.html', []),
    'status': delay('status.html', ['show_logout']),
    'add_spot': delay('add_spot.html', ['admin_page', 'show_logout']),
    'remove_spot': delay('remove_spot.html', ['admin_page', 'show_logout']),
    'remove_reservation': delay('remove_reservation.html', ['admin_page', 'show_logout']),
    'remove_user': delay('remove_user.html', ['admin_page', 'show_logout'])
}


def register(app):
    with app.app_context():
        model.init_app(app)

    @app.route('/auth', methods=['POST'])
    def auth():

        email = request.args.get('email')
        password = request.args.get('password')

        result = model.authenticate(email, password)

        if isinstance(result, model.User):
            # session.permanent = True
            # session['user_id'] = result.id
            # session['user_admin'] = result.admin
            return jsonify(model.convert(result))
        else:
            return abort(401)

    @app.route('/', methods=['GET', 'POST'])
    def login():
        if 'user_id' in session:
            return redirect(url_for('status'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            email = data['email']
            password = data['password']

            result = model.authenticate(email, password)

            if isinstance(result, model.User):
                session.permanent = True
                session['user_id'] = result.id
                session['user_admin'] = result.admin
                return redirect(url_for('status'))
            else:
                return router['login'](['invalid'])

        return router['login']([])

    @app.route('/admin', methods=['GET', 'POST'])
    def admin():
        if 'user_id' in session:
            if 'user_admin' in session and session['user_admin'] is True:
                return redirect(url_for('add_spot'))
            else:
                return redirect(url_for('status'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            email = data['email']
            password = data['password']

            result = model.admin(email, password)

            if isinstance(result, model.User):
                session.permanent = True
                session['user_id'] = result.id
                session['user_admin'] = result.admin
                return redirect(url_for('add_spot'))
            else:
                return router['admin'](['invalid'])

        return router['admin']([])

    @app.route('/add_spot', methods=['GET', 'POST'])
    def add_spot():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            if not data['location']:
                return router['add_spot'](['invalid'], data=model.garages())

            model.create(model.Spot, data)
            return router['add_spot'](['success'], data=model.garages())

        return router['add_spot']([], data=model.garages())

    @app.route('/remove_spot', methods=['GET', 'POST'])
    def remove_spot():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            model.remove(data['spot_id'])

            return router['remove_spot'](['success'], data=model.garages())

        return router['remove_spot']([], data=model.garages())

    @app.route('/remove_reservation', methods=['GET', 'POST'])
    def remove_reservation():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            model.delete(model.Reservation, data['reservation_id'])

            return router['remove_reservation'](['success'], data=model.reservations())

        app.logger.info(model.reservations())

        return router['remove_reservation']([], data=model.reservations())

    @app.route('/remove_user', methods=['GET', 'POST'])
    def remove_user():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            model.kill(data['user_id'])

            return router['remove_user'](['success'], data=model.plebs())

        app.logger.info(model.plebs())
        return router['remove_user']([], data=model.plebs())

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if 'user_id' in session:
            return redirect(url_for('status'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            app.logger.info(data)
            try:
                model.register(data)
            except ValueError as e:
                app.logger.info(e)
                return router['register'](['mismatch'])
            except Exception as e:
                app.logger.info(e)
                return router['register'](['invalid'])

            return router['login'](['success'])

        return router['register']([])

    @app.route('/status')
    def status():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        return router['status'](['success'], js='status.js')

    @app.route('/logout', methods=['POST'])
    def logout():
        if 'user_id' in session:
            del session['user_id']
            del session['user_admin']
            session.permanent = False

        return redirect(url_for('login'))

    @app.route('/details')
    def details():
        user_id = request.args.get('user_id')
        if user_id is None:
            if 'user_id' not in session:
                return redirect(url_for('login'))
            else:
                user_id = session['user_id']

        return jsonify(model.inform(user_id))

    @app.route('/reserve/<garage_id>', methods=['POST'])
    def reserve(garage_id):
        user_id = request.args.get('user_id')
        if user_id is None:
            if 'user_id' not in session:
                return redirect(url_for('login'))
            else:
                user_id = session['user_id']

        return jsonify(model.reserve(user_id, garage_id))

    @app.route('/occupy', methods=['POST'])
    def occupy():
        user_id = request.args.get('user_id')
        if user_id is None:
            if 'user_id' not in session:
                return redirect(url_for('login'))
            else:
                user_id = session['user_id']

        return jsonify(model.occupy(user_id))

    @app.route('/clear', methods=['POST'])
    def clear():
        user_id = request.args.get('user_id')
        if user_id is None:
            if 'user_id' not in session:
                return redirect(url_for('login'))
            else:
                user_id = session['user_id']

        return jsonify(model.clear(user_id))

    return app
