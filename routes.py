from flask import request, render_template, redirect, url_for, session, jsonify, flash
from forms import LoginForm
import model


def register(app):
    with app.app_context():
        model.init_app(app)

    @app.route('/')
    def default():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if 'user_id' in session:
            return redirect(url_for('status'))

        if request.method == 'POST':
            #data = request.form.to_dict(flat=True)
            email = form.email.data
            password = form.password.data

            result = model.authenticate(email, password)

            if isinstance(result, model.User):
                session.permanent = True
                session['user_id'] = result.id
                session['user_admin'] = result.admin
                return redirect('/status')
            else:
                return render_template('login.html', invalid=True, form= form)

        return render_template('login.html', form = form)

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
