from flask import Flask, render_template, request, redirect, url_for, session, flash
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
import uuid
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'cassandra-social-media-secret-key-2024'


# Cassandra connection setup
def setup_cassandra_connection():
    """Setup Cassandra connection and create keyspace/tables"""
    try:
        # Connect to Cassandra (adjust contact_points for your setup)
        cluster = Cluster(['127.0.0.1'], port=9042)
        session_cass = cluster.connect()

        # Create keyspace
        session_cass.execute("""
            CREATE KEYSPACE IF NOT EXISTS social_media 
            WITH replication = {
                'class': 'SimpleStrategy', 
                'replication_factor': 1
            }
        """)
        print("✅ Keyspace created successfully!")

        # Use the keyspace
        session_cass.set_keyspace('social_media')

        # Create users table
        session_cass.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                username TEXT,
                email TEXT,
                password TEXT,
                profile_picture TEXT,
                bio TEXT,
                created_at TIMESTAMP
            )
        """)
        print("✅ Users table created successfully!")

        # Create posts table (NO counters)
        session_cass.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                post_id UUID PRIMARY KEY,
                user_id UUID,
                username TEXT,
                caption TEXT,
                image_url TEXT,
                created_at TIMESTAMP
            )
        """)
        print("✅ Posts table created successfully!")

        # Create comments table
        session_cass.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                comment_id UUID,
                post_id UUID,
                user_id UUID,
                username TEXT,
                comment_text TEXT,
                commented_at TIMESTAMP,
                PRIMARY KEY (post_id, commented_at, comment_id)
            ) WITH CLUSTERING ORDER BY (commented_at ASC)
        """)
        print("✅ Comments table created successfully!")

        # Create likes table (to track who liked what)
        session_cass.execute("""
            CREATE TABLE IF NOT EXISTS likes (
                post_id UUID,
                user_id UUID,
                liked_at TIMESTAMP,
                PRIMARY KEY (post_id, user_id)
            )
        """)
        print("✅ Likes table created successfully!")

        # Create user_posts table for querying posts by user (NO counters)
        session_cass.execute("""
            CREATE TABLE IF NOT EXISTS user_posts (
                user_id UUID,
                post_id UUID,
                caption TEXT,
                image_url TEXT,
                created_at TIMESTAMP,
                PRIMARY KEY (user_id, created_at, post_id)
            ) WITH CLUSTERING ORDER BY (created_at DESC)
        """)
        print("✅ User posts table created successfully!")

        session_cass.shutdown()
        cluster.shutdown()

    except Exception as e:
        print(f"❌ Cassandra setup error: {e}")


def get_cassandra_session():
    """Get Cassandra session for database operations"""
    try:
        cluster = Cluster(['127.0.0.1'], port=9042)
        session_cass = cluster.connect('social_media')
        return session_cass, cluster
    except Exception as e:
        print(f"❌ Cassandra connection error: {e}")
        return None, None


def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()


# Setup Cassandra when app starts
setup_cassandra_connection()


# Routes
@app.route('/')
def index():
    """Home page - show all posts with likes and comments"""
    session_cass, cluster = get_cassandra_session()
    if not session_cass:
        flash("Database connection failed", "error")
        return render_template('index.html', posts=[], session=session)

    try:
        # Get all posts
        posts_query = """
            SELECT post_id, user_id, username, caption, image_url, created_at
            FROM posts
        """
        rows = session_cass.execute(posts_query)
        posts = []

        for row in rows:
            # Count likes
            likes_row = session_cass.execute(
                "SELECT COUNT(*) FROM likes WHERE post_id = %s",
                (row.post_id,)
            ).one()
            likes_count = likes_row.count if likes_row and hasattr(likes_row, 'count') else 0

            # Count comments
            comments_row = session_cass.execute(
                "SELECT COUNT(*) FROM comments WHERE post_id = %s",
                (row.post_id,)
            ).one()
            comments_count = comments_row.count if comments_row and hasattr(comments_row, 'count') else 0

            post = {
                'post_id': row.post_id,
                'user_id': row.user_id,
                'username': row.username,
                'caption': row.caption,
                'image_url': row.image_url,
                'created_at': row.created_at,
                'likes_count': likes_count,
                'comments_count': comments_count,
                'user_liked': False,
                'comments': []
            }

            # Check if current user liked this post
            if 'user_id' in session:
                like_check = session_cass.execute(
                    "SELECT * FROM likes WHERE post_id = %s AND user_id = %s",
                    (row.post_id, uuid.UUID(session['user_id']))
                )
                post['user_liked'] = bool(like_check.one())

            # Get comments for this post
            comments_query = """
                SELECT comment_id, user_id, username, comment_text, commented_at 
                FROM comments WHERE post_id = %s
            """
            comments = session_cass.execute(comments_query, (row.post_id,))
            post['comments'] = list(comments)

            posts.append(post)

        # Sort posts by creation time (newest first)
        posts.sort(key=lambda x: x['created_at'], reverse=True)

        return render_template('index.html', posts=posts, session=session)

    except Exception as e:
        flash(f"Error: {e}", "error")
        return render_template('index.html', posts=[], session=session)
    finally:
        session_cass.shutdown()
        cluster.shutdown()


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords don't match!", "error")
            return render_template('cassandra_register.html')

        session_cass, cluster = get_cassandra_session()
        if not session_cass:
            flash("Database connection failed", "error")
            return render_template('cassandra_register.html')

        try:
            # Check if username already exists
            user_by_username = session_cass.execute(
                "SELECT * FROM users WHERE username = %s ALLOW FILTERING",
                (username,)
            ).one()

            # Check if email already exists
            user_by_email = session_cass.execute(
                "SELECT * FROM users WHERE email = %s ALLOW FILTERING",
                (email,)
            ).one()

            if user_by_username or user_by_email:
                flash("Username or email already exists!", "error")
            else:
                user_id = uuid.uuid4()
                hashed_password = hash_password(password)

                session_cass.execute(
                    """
                    INSERT INTO users (user_id, username, email, password, created_at) 
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_id, username, email, hashed_password, datetime.now())
                )

                flash("Registration successful! Please login.", "success")
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            session_cass.shutdown()
            cluster.shutdown()

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        session_cass, cluster = get_cassandra_session()
        if not session_cass:
            flash("Database connection failed", "error")
            return render_template('cassandra_login.html')

        try:
            hashed_password = hash_password(password)

            user = session_cass.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s ALLOW FILTERING",
                (email, hashed_password)
            ).one()

            if user:
                session['user_id'] = str(user.user_id)
                session['username'] = user.username
                session['email'] = user.email
                flash("Login successful!", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid email or password!", "error")

        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            session_cass.shutdown()
            cluster.shutdown()

    return render_template('login.html')


@app.route('/create_post', methods=['POST'])
def create_post():
    """Create a new post"""
    if 'user_id' not in session:
        flash("Please login to create posts", "error")
        return redirect(url_for('login'))

    caption = request.form['caption']
    image_url = request.form.get('image_url', '')

    session_cass, cluster = get_cassandra_session()
    if not session_cass:
        flash("Database connection failed", "error")
        return redirect(url_for('index'))

    try:
        post_id = uuid.uuid4()
        user_id = uuid.UUID(session['user_id'])
        now = datetime.now()

        # Insert into posts table
        session_cass.execute(
            """
            INSERT INTO posts (post_id, user_id, username, caption, image_url, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (post_id, user_id, session['username'], caption, image_url, now)
        )

        # Also insert into user_posts for user-specific queries
        session_cass.execute(
            """
            INSERT INTO user_posts (user_id, post_id, caption, image_url, created_at) 
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, post_id, caption, image_url, now)
        )

        flash("Post created successfully!", "success")

    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        session_cass.shutdown()
        cluster.shutdown()

    return redirect(url_for('index'))


@app.route('/like_post/<post_id>')
def like_post(post_id):
    """Like or unlike a post"""
    if 'user_id' not in session:
        flash("Please login to like posts", "error")
        return redirect(url_for('login'))

    session_cass, cluster = get_cassandra_session()
    if not session_cass:
        flash("Database connection failed", "error")
        return redirect(url_for('index'))

    try:
        post_uuid = uuid.UUID(post_id)
        user_uuid = uuid.UUID(session['user_id'])

        # Check if already liked
        existing_like = session_cass.execute(
            "SELECT * FROM likes WHERE post_id = %s AND user_id = %s",
            (post_uuid, user_uuid)
        ).one()

        if existing_like:
            # Unlike - remove from likes table
            session_cass.execute(
                "DELETE FROM likes WHERE post_id = %s AND user_id = %s",
                (post_uuid, user_uuid)
            )
            flash("Post unliked!", "info")
        else:
            # Like - add to likes table
            session_cass.execute(
                """
                INSERT INTO likes (post_id, user_id, liked_at) 
                VALUES (%s, %s, %s)
                """,
                (post_uuid, user_uuid, datetime.now())
            )
            flash("Post liked!", "success")

    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        session_cass.shutdown()
        cluster.shutdown()

    return redirect(url_for('index'))


@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    """Add comment to a post"""
    if 'user_id' not in session:
        flash("Please login to comment", "error")
        return redirect(url_for('login'))

    comment_text = request.form['comment_text']

    session_cass, cluster = get_cassandra_session()
    if not session_cass:
        flash("Database connection failed", "error")
        return redirect(url_for('index'))

    try:
        post_uuid = uuid.UUID(post_id)
        user_uuid = uuid.UUID(session['user_id'])
        comment_id = uuid.uuid4()

        # Insert comment
        session_cass.execute(
            """
            INSERT INTO comments (comment_id, post_id, user_id, username, comment_text, commented_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (comment_id, post_uuid, user_uuid, session['username'], comment_text, datetime.now())
        )

        flash("Comment added successfully!", "success")

    except Exception as e:
        flash(f"Error: {e}", "error")
    finally:
        session_cass.shutdown()
        cluster.shutdown()

    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    """User profile page"""
    if 'user_id' not in session:
        flash("Please login to view profile", "error")
        return redirect(url_for('login'))

    session_cass, cluster = get_cassandra_session()
    if not session_cass:
        flash("Database connection failed", "error")
        return redirect(url_for('index'))

    try:
        user_uuid = uuid.UUID(session['user_id'])

        # Get user info
        user = session_cass.execute(
            "SELECT * FROM users WHERE user_id = %s",
            (user_uuid,)
        ).one()

        # Get user's posts
        user_posts = session_cass.execute(
            "SELECT * FROM user_posts WHERE user_id = %s",
            (user_uuid,)
        )

        posts_list = []
        for post in user_posts:
            # Count likes for each post
            likes_row = session_cass.execute(
                "SELECT COUNT(*) FROM likes WHERE post_id = %s",
                (post.post_id,)
            ).one()
            likes_count = likes_row.count if likes_row and hasattr(likes_row, 'count') else 0

            # Count comments for each post
            comments_row = session_cass.execute(
                "SELECT COUNT(*) FROM comments WHERE post_id = %s",
                (post.post_id,)
            ).one()
            comments_count = comments_row.count if comments_row and hasattr(comments_row, 'count') else 0

            posts_list.append({
                'post_id': post.post_id,
                'caption': post.caption,
                'image_url': post.image_url,
                'created_at': post.created_at,
                'likes_count': likes_count,
                'comments_count': comments_count
            })

        return render_template('cassandra_profile.html', user=user, posts=posts_list)

    except Exception as e:
        flash(f"Error: {e}", "error")
        return redirect(url_for('index'))
    finally:
        session_cass.shutdown()
        cluster.shutdown()


@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Different port to run alongside MySQL version