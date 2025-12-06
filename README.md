# 🚀 SocialMedia – Flask Social Networking Application

A lightweight social media platform built with **Flask** and  **Appache Cassandra**, featuring user authentication, post creation, likes, comments, and a clean Bootstrap UI.

---

## 🌟 Features

### 🔐 User Authentication

* User registration with email & password
* Secure login using session management
* Password hashing (SHA-256)

### 📝 Post Management

* Create posts with captions & optional images
* View all posts in a shared feed
* Delete your own posts
* Timestamped posts

### ❤️ Engagement Features

* Like / unlike posts
* Add & view comments
* Interaction metrics (like + comment count)

### 👤 User Profile

* View username, email, and bio
* Display "Member Since" date
* See all posts made by the user
* Post statistics

### 📱 Responsive UI

* Bootstrap 5 mobile-friendly design
* Clean and intuitive interface
* Dark navbar with easy navigation

---

## 🛠️ Technology Stack

| Layer          | Technology                 |
| -------------- | -------------------------- |
| Backend        | Flask (Python)             |
| Database       | MySQL                      |
| Frontend       | HTML, Jinja2, Bootstrap 5  |
| Authentication | Sessions + SHA-256 hashing |

---

## 📋 Requirements

* Python 3.7+
* MySQL Server
* `flask`
* `mysql-connector-python`

---

## 🚀 Installation Guide

### 1️⃣ Clone the Repository

<pre class="overflow-visible!" data-start="1521" data-end="1540"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>cd</span><span> DBMS
</span></span></code></div></div></pre>

### 2️⃣ Install Dependencies

<pre class="overflow-visible!" data-start="1571" data-end="1623"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>pip install flask mysql-connector-python
</span></span></code></div></div></pre>

### 3️⃣ Configure MySQL

Make sure MySQL is running on  **localhost** .

Default credentials used in the app:

<pre class="overflow-visible!" data-start="1732" data-end="1779"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>user: root</span><span>
</span><span>password: your_password_here</span><span>
</span></span></code></div></div></pre>

> ⚠️ Update these credentials in **app.py** before production.

### 4️⃣ Run the App

<pre class="overflow-visible!" data-start="1865" data-end="1890"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python app.py
</span></span></code></div></div></pre>

The app will automatically create the database and tables.

### 5️⃣ Run the Cassandra

<pre class="overflow-visible!" data-start="1865" data-end="1890"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>cassandra.bat
</span></span></code></div></div></pre>

To start the cassandra and run it in command prompt

### 6️⃣ Visit the Application

Open your browser:

<pre class="overflow-visible!" data-start="2002" data-end="2031"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>http:</span><span>//localhost:5000</span><span>
</span></span></code></div></div></pre>

---

## 📁 Project Structure

<pre class="overflow-visible!" data-start="2063" data-end="2352"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>DBMS/
├── app.py                 </span><span># Main Flask app</span><span>
├── README.md              </span><span># Project documentation</span><span>
├── .gitignore             </span><span># Ignore sensitive or unnecessary files</span><span>
└── templates/
    ├── </span><span>base</span><span>.html
    ├── index.html
    ├── login.html
    ├── register.html
    └── profile.html
</span></span></code></div></div></pre>

---

## 🗄️ Database Schema

### 🧑‍💼 Users Table

* user_id (PK)
* username
* email
* password (hashed)
* profile_picture
* bio
* created_at

### 📝 Posts Table

* post_id (PK)
* user_id (FK)
* caption
* image_url
* created_at

### 💬 Comments Table

* comment_id (PK)
* post_id (FK)
* user_id (FK)
* comment_text
* commented_at

### ❤️ Likes Table

* like_id (PK)
* post_id (FK)
* user_id (FK)
* liked_at
* Unique constraint: *(post_id, user_id)*

---

## 🔐 Security Notes

* Update MySQL credentials before deployment.
* For production, use **bcrypt** instead of SHA-256.
* Use environment variables for secrets (`.env` recommended).

---

## 📝 Usage Guide

### 🧾 Register

1. Click **Register**
2. Enter username, email, password
3. Submit to create an account

### 🔑 Login

Use your email and password.

### ➕ Create a Post

* Add a caption
* Optionally add an image URL
* Click **Post**

### ❤️ Like a Post

Click the **heart icon** to like/unlike.

### 💬 Comment

* Enter your comment
* Click **Post Comment**

### 👤 View Your Profile

See:

* Your posts
* Your bio
* Member since date

### 🚪 Logout

Click **Logout** in the navbar.

---

## 🐛 Troubleshooting

### ❌ Database Connection Error

* Ensure MySQL is running
* Verify credentials in `app.py`
* Check MySQL is listening on port `3306`

### ❌ Port Already in Use

Run Flask on a different port:

<pre class="overflow-visible!" data-start="3724" data-end="3761"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>python app.py --port 5001
</span></span></code></div></div></pre>

---

## 📈 Future Enhancements

* Follow / unfollow users
* Search bar
* Direct messaging
* Notifications
* Edit post
* Upload profile picture
* Trending posts / hashtags
* Email verification
* Password reset

---

## 📄 License

This project is **open-source** under the  **MIT License** .
