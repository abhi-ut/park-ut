from flask import Flask, request, render_template, flash, redirect, url_for, session, jsonify
import model


def register(app):
    with app.app_context():
        model.init_app(app)

    @app.route('/')
    def default():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
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
                session['user_name'] = result.name
                session['user_email'] = result.email
                session['user_admin'] = result.admin
                return redirect('/status')
            else:
                return render_template('login.html', invalid=True)

        return render_template('login.html')

    @app.route('/status')
    def status():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        return render_template('status.html', show_logout=True, js='status.js')

    @app.route('/details', methods=['POST'])
    def details():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        result = model.details(session['user_id'])
        app.logger.info(result)

        return jsonify(result)

    @app.route('/logout', methods=['POST'])
    def logout():
        if 'user_id' in session:
            del session['user_id']
            del session['user_name']
            del session['user_email']
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

    @app.route('/occupy/<reservation_id>', methods=['POST'])
    def occupy(reservation_id):
        result = model.occupy(reservation_id)
        app.logger.info(result)
        return jsonify(result)

    @app.route('/show')
    def show():
        users = model.many(model.User)

        app.logger.info(users)

        return render_template('show.html', users=users)

    # @app.errorhandler(500)
    # def server_error(e):
    #     return """
    #     An internal error occurred: <pre>{}</pre>
    #     See logs for full stacktrace.
    #     """.format(e), 500

    return app
