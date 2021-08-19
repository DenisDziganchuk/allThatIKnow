from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blogs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Article %r>" % self.id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/create_post", methods=["POST", "GET"])
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        text = request.form["text"]
        article = Article(title=title, description=description, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect("/posts")
        except:
            return "Problem with saving post"
    else:
        return render_template("create_post.html")


@app.route("/posts")
def posts():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', article=article)
