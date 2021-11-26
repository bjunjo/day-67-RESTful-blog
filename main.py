from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

# GET
@app.route('/')
def get_all_posts():
    # Read from the database
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/post/<int:index>")
def show_post(index):
    # Get the specific post with the index as an ID
    requested_post = BlogPost.query.get(index)
    print(f"Requested post's ID: {requested_post.id}")
    return render_template("post.html", post=requested_post)

# POST - Create a new POST route called /new-post in your Flask server.
@app.route("/new-post", methods=["GET", "POST"])
def create_new_post():
    form = CreatePostForm()
    # When the user is done typing out entries to all the fields,
    if form.validate_on_submit():
        # the data in the form should be saved as a BlogPost Object into the posts.db
        new_post = BlogPost(
            title=request.form.get("title"),
            subtitle=request.form.get("subtitle"),
            date=date.today().strftime("%B %d, %Y"),
            body=request.form.get("body"),
            author=request.form.get("author"),
            img_url=request.form.get("img_url")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('show_post', index=new_post.id))
    return render_template("make-post.html", form=form)

# Create a new route /edit-post/<post_id>
@app.route("/edit/post/<int:index>", methods=["GET", "POST"])
def edit_post(index):
    # Get the post to edit
    post = BlogPost.query.get(index)

    # When you head over to make-post.html
    #  it should auto-populate the fields in the WTForm with the blog post's data.
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    
    # Update the database once the form is submitted
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', index=post.id))
    return render_template("make-post.html", post=post, form=edit_form)

# DELETE Blog Posts
@app.route("/delete/<int:index>", methods=['GET', 'DELETE'])
def delete(index):
    # Delete a movie
    post_to_delete = BlogPost.query.get(index)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)