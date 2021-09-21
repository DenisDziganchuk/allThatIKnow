from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blogs.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "denisdziganchuk"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    # author = db.Column(db.Text, default="Guest")

    def __repr__(self):
        return "<Article %r>" % self.id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(50), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError("User already exists! Try another username")


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=3, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")


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
        # author = current_user.username
        article = User(title=title, description=description, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect("/posts")
        except:
            return "Problem with saving post"
    else:
        return render_template("create_post.html")


@app.route("/posts/<int:id>/update", methods=["POST", "GET"])
def update_post(id):
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        text = request.form["text"]
        article = User(title=title, description=description, text=text)
        try:
            db.session.commit()
            return redirect("/posts")
        except:
            return "Problem with updating post"
    else:
        article = User.query.get(id)
        return render_template("update_post.html", article=article)


@app.route("/posts")
def posts():
    article = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', article=article)


@app.route("/posts/<int:id>")
def post_detail(id):
    article = User.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route("/posts/<int:id>/delete")
def post_delete(id):
    article = User.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect("/posts")
    except:
        return "Error deleting post"


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("dashboard"))
    return render_template("login.html", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hash_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("registration.html", form=form)


@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", current_user=current_user)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))
