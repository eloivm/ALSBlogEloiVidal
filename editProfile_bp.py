from flask import Blueprint, render_template, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user
from model.user import User
from model.post import Post
from model.comment import Comment
from functions import is_valid_email, is_valid_nickname, is_valid_password, nickname_exists, email_exists, update_posts
from srp import srp
import redis

editProfile_bp = Blueprint('editProfile', __name__)


@editProfile_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    try:
        errors = session.pop('errors', [])
        form_data = session.pop('form_data', {'nickname': '', 'email': ''})

        current_user_nickname = current_user.nickname
        local_current_user = None
        for user_oid in srp.load_all_keys(User):
            loaded_user = srp.load(user_oid)
            if loaded_user.nickname == current_user_nickname:
                local_current_user = loaded_user
                break

        if not local_current_user:
            flash('Usuario no encontrado.', 'error')
            print("F")
            return redirect('/')



        if request.method == 'POST':
            form_data['nickname'] = request.form['nickname']
            form_data['email'] = request.form['email']

            nickname = form_data['nickname']
            email = form_data['email']

            if not is_valid_nickname(nickname):
                errors.append('El nickname debe tener entre 3 y 20 caracteres alfanuméricos y puede contener "_" pero no debe comenzar con él.')

            if not is_valid_email(email):
                errors.append('La dirección de correo electrónico no es válida.')

            if nickname_exists(nickname) and nickname != current_user.nickname:
                errors.append('Ya existe un usuario con ese nickname.')

            if email_exists(email) and email != current_user.email:
                errors.append('Ya existe un usuario con ese correo electrónico.')

            if not errors:
                old_nickname = current_user.nickname
                current_user.nickname = nickname
                current_user.email = email

                srp.save(current_user)

                current_user.nickname = nickname

                update_posts(old_nickname, nickname)

                print(f"Actualizando perfil de usuario: nickname={nickname}, email={email}")

                return redirect('/')
            else:
                session['errors'] = errors
                session['form_data'] = form_data
                return redirect('/edit_profile')

        form_data['nickname'] = current_user.nickname
        form_data['email'] = current_user.email
        return render_template('editProfile.html', errors=errors, form_data=form_data)
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

@editProfile_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    try:
        errors = session.pop('errors', [])
        form_data = session.pop('form_data', {'old_password': '', 'new_password': '', 'new_password_repeat': ''})

        user = None
        for user_oid in srp.load_all_keys(User):
            loaded_user = srp.load(user_oid)
            if loaded_user.nickname == current_user.nickname:
                user = loaded_user
                break

        if request.method == 'POST':
            form_data['old_password'] = request.form['old_password']
            form_data['new_password'] = request.form['new_password']
            form_data['new_password_repeat'] = request.form['new_password_repeat']

            old_password = form_data['old_password']
            new_password = form_data['new_password']
            new_password_repeat = form_data['new_password_repeat']

            if not is_valid_password(new_password):
                errors.append('La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas y números o caracteres especiales.')

            if new_password != new_password_repeat:
                errors.append('Las contraseñas no coinciden.')

            if not check_password_hash(user.password, old_password):
                errors.append('Contraseña antigua incorrecta.')

            if not errors:
                user.password = generate_password_hash(new_password)
                srp.save(user)

                flash('Contraseña actualizada exitosamente.', 'success')
                return redirect('/')

            session['errors'] = errors
            session['form_data'] = form_data
            return redirect('/change_password')

        return render_template('changePassword.html', errors=errors, form_data=form_data, title=user.nickname if user else "Cambiar contraseña")
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

@editProfile_bp.route('/deleteUser', methods=['GET', 'POST'])
@login_required
def delete_user():
    try:
        if request.method == 'POST':
            user = None
            for user_oid in srp.load_all_keys(User):
                loaded_user = srp.load(user_oid)
                if loaded_user.nickname == current_user.nickname:
                    user = loaded_user
                    break

            if user is None:
                flash('Usuario no encontrado.', 'error')
                return redirect('/')

            for post_oid in srp.load_all_keys(Post):
                post = srp.load(post_oid)
                if post.user_id == user.nickname:
                    srp.delete(post_oid)

            for comment_oid in srp.load_all_keys(Comment):
                comment = srp.load(comment_oid)
                if comment.user_id == user.id:
                    srp.delete(comment_oid)

            srp.delete(user_oid)

            logout_user()
            flash('Usuario eliminado exitosamente.', 'success')

            return redirect('/')

        return render_template('deleteUser.html')
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

