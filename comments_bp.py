from flask import Blueprint, request, redirect, flash, url_for, render_template
from model.comment import Comment
from flask_login import login_required, current_user
from model.user import User
from srp import srp
import redis

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/addComment/<post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    try:
        content = request.form['content']
        user_nickname = current_user.nickname

        if not content.strip():
            flash('El comentario no puede estar vacío.', 'error')
            return redirect(f'/viewPost/{post_id}')

        user_id = None
        for oid in srp.load_all_keys(User):
            user = srp.load(oid)
            if user.nickname == user_nickname:
                user_id = user.id
                break

        if user_id is None:
            flash('Usuario no encontrado.', 'error')
            return redirect(f'/viewPost/{post_id}')

        srp.save(Comment(content, user_id, post_id, user_nickname))

        return redirect(f'/viewPost/{post_id}')
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
        return render_template('error.html')


@comments_bp.route('/delete_comment/<comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
    try:
        oid_to_delete = None
        for oid in srp.load_all_keys(Comment):
            comment = srp.load(oid)
            if comment.comment_id == comment_id:
                oid_to_delete = oid
                break

        if oid_to_delete:
            user_nickname = current_user.nickname
            user_id = None
            for oid in srp.load_all_keys(User):
                user = srp.load(oid)
                if user.nickname == user_nickname:
                    user_id = user.id
                    break

            if user_id is None:
                flash('Usuario no encontrado.', 'error')
                return redirect(url_for('posts.view_post', post_id=comment.post_id))

            if user_id == comment.user_id:
                post_id = comment.post_id
                srp.delete(oid_to_delete)
                return redirect(url_for('posts.view_post', post_id=post_id))
            else:
                return "No tienes permiso para eliminar este comentario"
        else:
            return "Comentario no encontrado"
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')