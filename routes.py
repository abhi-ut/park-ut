from flask import request, render_template, redirect, url_for, session, jsonify
import model


def register(app):
    with app.app_context():
        model.init_app(app)

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
                return redirect('/status')
            else:
                return render_template('login.html', invalid=True)

        return render_template('login.html')

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
            app.logger.info(result)

            if isinstance(result, model.User):
                session.permanent = True
                session['user_id'] = result.id
                session['user_admin'] = result.admin
                return redirect(url_for('add_spot'))
            else:
                return render_template('admin.html', admin_page=True, invalid=True)

        return render_template('admin.html', admin_page=True)

    @app.route('/add_spot', methods=['GET', 'POST'])
    def add_spot():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            model.create(model.Spot, data)
            return render_template('add_spot.html', admin_page=True, show_logout=True, success=True,
                                   garages=model.garages())

        return render_template('add_spot.html', admin_page=True, show_logout=True, garages=model.garages())

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

            return render_template('remove_spot.html', admin_page=True, show_logout=True, success=True,
                                   garages=model.garages())

        return render_template('remove_spot.html', admin_page=True, show_logout=True, garages=model.garages())

    @app.route('/remove_reservation', methods=['GET', 'POST'])
    def remove_reservation():
        if 'user_id' in session:
            if 'user_admin' not in session or session['user_admin'] is False:
                return redirect(url_for('status'))
        else:
            return redirect(url_for('admin'))

        model.refresh()

        if request.method == 'POST':
            data = request.form.to_dict(flat=True)
            model.abort(model.one(model.Reservation, data['reservation_id']))

            return render_template('remove_reservation.html', admin_page=True, show_logout=True, success=True,
                                   garages=model.garages())

        return render_template('remove_reservation.html', admin_page=True, show_logout=True,
                               spots=model.many(model.Spot))

    @app.route('/status')
    def status():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        return render_template('status.html', show_logout=True, js='status.js')

    @app.route('/details')
    def details():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        result = model.inform(session['user_id'])
        app.logger.info(result)

        return jsonify(result)

    @app.route('/logout', methods=['POST'])
    def logout():
        if 'user_id' in session:
            del session['user_id']
            del session['user_admin']
            session.permanent = False

        return redirect(url_for('login'))

    @app.route('/reserve/<garage_id>', methods=['POST'])
    def reserve(garage_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        result = model.reserve(session['user_id'], garage_id)
        app.logger.info(result)
        return jsonify(result)

    @app.route('/occupy', methods=['POST'])
    def occupy():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        result = model.occupy(session['user_id'])
        app.logger.info(result)
        return jsonify(result)

    @app.route('/clear', methods=['POST'])
    def clear():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        result = model.clear(session['user_id'])
        app.logger.info(result)
        return jsonify(result)

    return app
