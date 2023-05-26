from flask import Blueprint, render_template, request, redirect, flash, session, url_for
from flask_login import logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from model.user import User
from functions import is_valid_email, is_valid_nickname, is_valid_password, nickname_exists, email_exists
from flask_login import login_required
from srp import srp
import redis

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        errors = session.pop('errors', [])
        form_data = session.pop('form_data', {'nickname': '', 'email': ''})

        if request.method == 'POST':
            form_data['nickname'] = request.form['nickname']
            form_data['email'] = request.form['email']
            password = request.form['password']
            password_repeat = request.form['password-repeat']

            nickname = form_data['nickname']
            email = form_data['email']

            if not is_valid_nickname(nickname):
                errors.append('El nickname debe tener entre 3 y 20 caracteres alfanuméricos y puede contener "_" pero no debe comenzar con él.')

            if not is_valid_email(email):
                errors.append('La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas y números o caracteres especiales.')

            if not is_valid_password(password):
                errors.append('La contraseña debe tener al menos 8 caracteres.')

            if password != password_repeat:
                errors.append('Las contraseñas no coinciden.')

            if nickname_exists(nickname):
                errors.append('Ya existe un usuario con ese nickname.')

            if email_exists(email):
                errors.append('Ya existe un usuario con ese correo electrónico.')

            if not errors:
                password_hash = generate_password_hash(password)

                new_user = User(nickname, email, password_hash)

                srp.save(new_user)

                print(f"Registrando usuario: nickname={nickname}, email={email}")

                return redirect('/login')
            else:
                session['errors'] = errors
                session['form_data'] = form_data
                return redirect('/register')

        return render_template('register.html', errors=errors, form_data=form_data)
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        errors = session.pop('errors', [])
        form_data = session.pop('form_data', {'email': ''})

        if request.method == 'POST':
            form_data['email'] = request.form['email']
            password = request.form['password']

            email = form_data['email']

            if not is_valid_email(email):
                errors.append('Por favor, introduce un correo electrónico válido.')

            user = None
            if not errors:
                for user_oid in srp.load_all_keys(User):
                    loaded_user = srp.load(user_oid)
                    if loaded_user.email == email:
                        user = loaded_user
                        break

                if user is not None and check_password_hash(user.password, password):
                    login_user(user)
                    flash('Inicio de sesión exitoso.', 'success')
                    return redirect('/')
                else:
                    errors.append('Correo electrónico o contraseña incorrecta.')

            session['errors'] = errors
            session['form_data'] = form_data
            return redirect('/login')

        return render_template('login.html', errors=errors, form_data=form_data)
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')


@auth_bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Sesión cerrada.', 'success')
        return redirect('/')
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')