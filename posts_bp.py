from flask import Blueprint, render_template, request, redirect, flash
import redis
from model.post import Post
from model.comment import Comment
from flask_login import login_required, current_user
from srp import srp

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/')
def index():
        try:
            posts = list(srp.load_all(Post))
            sorted_posts = sorted(posts, key=lambda post: post.edited_at, reverse=True)
            sust = {
                "posts": sorted_posts
            }

            return render_template('index.html', **sust)

        except redis.exceptions.ConnectionError as e:
            print(e)
            return render_template('databaseError.html')
        except Exception:
            return render_template('error.html')

 

@posts_bp.route('/myPosts')
@login_required
def my_posts():
    try:
        user_id = current_user.nickname
        posts = [post for post in srp.load_all(Post) if post.user_id == user_id]
        sorted_posts = sorted(posts, key=lambda post: post.edited_at, reverse=True)
        sust = {
            "posts": sorted_posts
        }

        return render_template('myPosts.html', **sust)
    except redis.exceptions.ConnectionError as e:
            print(e)
            return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

@posts_bp.route('/viewPost/<post_id>')
def view_post(post_id):
    try:
        oid_to_view = None
        for oid in srp.load_all_keys(Post):
            post = srp.load(oid)
            if post.post_id == post_id:
                oid_to_view = oid
                break

        if oid_to_view:
            post = srp.load(oid_to_view)
            comments = [comment for comment in srp.load_all(Comment) if comment.post_id == post_id]
            comments = sorted(comments, key=lambda comment: comment.created_at, reverse=True) 
            sust = {
                "post": post,
                "comments": comments
            }
            return render_template('viewPost.html', **sust)
        else:
            return "Post no encontrado"
    except redis.exceptions.ConnectionError as e:
            print(e)
            return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

@posts_bp.route('/addPost', methods=['GET', 'POST'])
@login_required
def add_post():
    try:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            user_id = current_user.nickname

            if not title.strip() or not content.strip():
                flash('El título y el contenido no pueden estar vacíos.', 'error')
                return redirect('/addPost')

            srp.save(Post(title, content, user_id))

            print(f"Guardando post: title={title}, content={content}")

            return redirect('/')

        return render_template('addPost.html')
    except redis.exceptions.ConnectionError as e:
            print(e)
            return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')

@posts_bp.route('/editPost/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    try:
        oid_to_edit = None
        for oid in srp.load_all_keys(Post):
            post = srp.load(oid)
            if post.post_id == post_id:
                oid_to_edit = oid
                break

        if oid_to_edit:
            post = srp.load(oid_to_edit)

            if post.user_id != current_user.nickname:
                flash('No tienes permiso para editar este post.', 'error')
                return redirect('/')

            if request.method == 'POST':
                title = request.form['title']
                content = request.form['content']

                if not title.strip() or not content.strip():
                    flash('El título y el contenido no pueden estar vacíos.', 'error')
                    return redirect(f'/editPost/{post_id}')

                if post.title == title and post.content == content:
                    flash('El título y el contenido son idénticos a los existentes, no se realizó ninguna actualización.', 'error')
                    return redirect('/')

                post.title = title
                post.content = content
                srp.save(post)

                return redirect('/')
    
            sust = {
                "post_id": post_id,
                "title": post.title,
                "content": post.content,
            }
            return render_template('editPost.html', **sust)
        else:
            return "Post no encontrado"
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')


@posts_bp.route('/deletePost/<post_id>', methods=['GET'])
@login_required
def delete_post(post_id):
    try:
        oid_to_delete = None
        for oid in srp.load_all_keys(Post):
            post = srp.load(oid)
            if post.post_id == post_id:
                oid_to_delete = oid
                break

        if oid_to_delete:
            post = srp.load(oid_to_delete)

            if post.user_id != current_user.nickname:
                flash('No tienes permiso para eliminar este post.', 'error')
                return redirect('/')

            for comment_oid in srp.load_all_keys(Comment):
                comment = srp.load(comment_oid)
                if comment.post_id == post_id:
                    srp.delete(comment_oid)

            srp.delete(oid_to_delete)
        else:
            return "Post no encontrado"

        return redirect('/')
    except redis.exceptions.ConnectionError as e:
        print(e)
        return render_template('databaseError.html')
    except Exception:
            return render_template('error.html')