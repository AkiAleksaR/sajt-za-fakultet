from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'tajna_kljuc'  # Sekretni ključ za sesije

# Funkcija za proveru login podataka
def check_login(username, password):
    return username == 'Aleksa' and password == '1234'

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM post ORDER BY id DESC")  # Objave na vrhu
    posts = c.fetchall()
    conn.close()

    return render_template("index.html", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if check_login(username, password):
            session['username'] = username  # Spremi korisnika u sesiju
            return redirect(url_for('index'))  # Prebaci korisnika na početnu stranicu
        else:
            return "Pogrešno korisničko ime ili lozinka", 401  # Pogrešni podaci
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)  # Ukloni korisnika iz sesije
    return redirect(url_for('index'))  # Prebaci na početnu stranicu

@app.route("/add_post", methods=["POST"])
def add_post():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ako korisnik nije ulogovan, preusmeri ga na login

    naslov = request.form['naslov']
    datum = request.form['datum']
    sadrzaj = request.form['sadrzaj']

    # Dodavanje nove objave u bazu
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute('''INSERT INTO post (naslov, datum, sadrzaj) VALUES (?, ?, ?)''',
              (naslov, datum, sadrzaj))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if 'username' not in session:
        return redirect(url_for('login'))  # Ako korisnik nije ulogovan, preusmeri ga na login

    # Proveri da li je korisnik "Aleksa"
    if session['username'] != 'Aleksa':
        return "Nemate pravo da obrišete ovu objavu.", 403  # Ako nije "Aleksa", zabraniti brisanje

    # Brisanje objave sa baze
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute('''DELETE FROM post WHERE id = ?''', (post_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/post/<int:post_id>")
def blog_post(post_id):
    conn = sqlite3.connect('posts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM post WHERE id = ?", (post_id,))
    post = c.fetchone()
    conn.close()

    if post:
        return render_template("blog_post.html", post=post)
    else:
        return "Post not found", 404
