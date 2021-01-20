
from flask import Flask, current_app, render_template, abort, request, redirect, url_for
from datetime import datetime
import psycopg2
import user
from flask_login import LoginManager, login_user, logout_user
from flask import flash
from werkzeug.utils import secure_filename
import os

#conn = psycopg2.connect(os.environ.get("DATABASE_URL"), sslmode='require')
conn=psycopg2.connect("dbname='myDB' user='postgres' host='localhost' password='yusufalppAAAASSSS1'")

def home_page():
    return render_template("home.html")

def admin_Ranks():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM adminranking ORDER BY total_points DESC")
    ranking = cur.fetchall()
    cur.execute("SELECT * FROM adminranking ORDER BY total_replies DESC")
    ranking1 = cur.fetchall()
    cur.execute("SELECT * FROM adminranking ORDER BY total_extra_points DESC")
    ranking2 = cur.fetchall()
    cur.execute("SELECT * FROM adminranking ORDER BY total_points_from_users DESC")
    ranking3 = cur.fetchall()
    return render_template("adminRanks.html",users=users,ranking=ranking,ranking1=ranking1,ranking2=ranking2,ranking3=ranking3)
   
def regular_Ranks():
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM regularranking ORDER BY total_marked_answers DESC")
    ranking = cur.fetchall()
    cur.execute("SELECT * FROM regularranking ORDER BY entry_count DESC")
    ranking1 = cur.fetchall()
    cur.execute("SELECT * FROM regularranking ORDER BY total_given_points DESC")
    ranking2 = cur.fetchall()
    return render_template("regularRanks.html",users=users,ranking=ranking,ranking1=ranking1,ranking2=ranking2)

def profile(id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM privilege")
    privilege = cur.fetchall()
    cur.execute("SELECT * FROM admin")
    admin = cur.fetchall()
    cur.execute("SELECT * FROM regular")
    regular = cur.fetchall()
    cur.execute("SELECT * FROM complaint")
    complaint = cur.fetchall()
    cur.execute("SELECT * FROM reply")
    reply = cur.fetchall()
    cur.execute("SELECT * FROM entry")
    entry = cur.fetchall()
    cur.execute("SELECT ENCODE(images.img, 'base64') FROM images WHERE user_id=%s", (id,))
    img = cur.fetchone()
    if img is not None:
        img = img[0]
        img = "data:image/png;base64," + img
    return render_template("profile.html", users=users, privilege=privilege, admin=admin, regular=regular, entry=entry, complaint=complaint,  reply=reply, img=img)

def ask(id):
    if request.method == "POST":
        title = request.form["title"]
        email = request.form["email"]
        phone = request.form["phone"]
        category = request.form["category"]
        question = request.form["question"]
        status = "Pending"
        cur = conn.cursor()
        cur.execute(''' INSERT INTO entry(id, title, text, email, phone)
        VALUES (%s,%s,%s,%s,%s) returning entry_id''',(id, title, question, email, phone)) 
        entry_id = cur.fetchone()
        cur.execute(''' INSERT INTO complaint(entry_id, status, category)
        VALUES (%s,%s,%s) returning entry_id''',(entry_id, status, category)) 
        temp = id
        cur.execute(''' UPDATE regularranking SET entry_count = entry_count + 1 WHERE id = %s''', (temp,))
        conn.commit()
        cur.close()
    return render_template("ask.html")

def answer(id):
    if request.method == "POST":
        title = request.form["title"]
        email = request.form["email"]
        phone = request.form["phone"]
        answer = request.form["answer"]
        questionId = request.form["questionId"]
        cur = conn.cursor()
        cur.execute('''SELECT * FROM complaint WHERE entry_id=%s''', (questionId,))
        entry = cur.fetchone()
        temp = id
        status = "Answered"
        if entry is not None:
            if entry[1] == "Pending":
                cur.execute(''' UPDATE adminranking SET total_replies = total_replies + 1 WHERE id = %s''', (temp,))
                cur.execute(''' UPDATE complaint SET status = %s WHERE entry_id = %s''', (status,questionId))
                cur.execute(''' SELECT * FROM entry WHERE entry_id=%s''', (entry[0],))
                entryTop = cur.fetchone()
                cur.execute(''' UPDATE regularranking SET total_marked_answers = total_marked_answers + 1 WHERE id = %s''', (entryTop[1],))
                cur.execute(''' INSERT INTO entry(id, title, text, email, phone)
                VALUES (%s,%s,%s,%s,%s) returning entry_id''',(id, title, answer, email, phone)) 
                newEntryId = cur.fetchone()
                timeQuestion = entryTop[4]
                timeNow = datetime.now()
                delta = timeNow - timeQuestion
                points = 10
                extraPoints = int(10 - 0.00001157 * delta.seconds)
                cur.execute(''' UPDATE adminranking SET total_extra_points = total_extra_points + %s WHERE id = %s''', (extraPoints,temp))
                cur.execute(''' UPDATE adminranking SET total_points = total_points + %s WHERE id = %s''', (extraPoints,temp))
                cur.execute(''' INSERT INTO reply(entry_id, extra_points, given_points, complaint_id)
                VALUES (%s,%s,%s,%s) ''',(newEntryId, extraPoints, 0, questionId)) 
                conn.commit()
                cur.close()
            else:
                return render_template("answer.html")
        else:
            return render_template("answer.html")
    return render_template("answer.html")

def signUp_page():
    if request.method == "POST":
        admin = False
        name = request.form["name"]
        surname = request.form["surname"]
        username = request.form["username"]
        password = request.form["password"]
        expertise = request.form["expertise"]
        company = request.form["company"]
        subject = request.form["subject"]
        job = request.form["job"]
        if len(request.form.getlist('checkbox')) > 0 and (expertise == "" or company == ""):
            flash("Please fill required spaces for admin.")
            return render_template("signUp.html")
        if len(request.form.getlist('checkbox')) == 0 and (subject == "" or job == ""):
            flash("Please fill required spaces for regular.")
            return render_template("signUp.html")
        if len(request.form.getlist('checkbox')) > 0:
            admin = True
        cur = conn.cursor()
        cur.execute('''select * from users WHERE username = %s''',(username,))
        entry = cur.fetchone()
        if entry is not None:
            flash("User already exists.")
        else:
            cur.execute(''' INSERT INTO users(name, surname, username, password)
            VALUES (%s,%s,%s,%s) ''',(name, surname, username, password)) 
            cur.execute('''select * from users''')
            cur.execute(''' INSERT INTO privilege(privelege_type)
            VALUES (%s) returning id''',(admin,))
            id = cur.fetchone()
            if admin == True:
                cur.execute(''' INSERT INTO admin(id,expertise,company)
                VALUES (%s,%s,%s)''',(id,expertise,company))
                cur.execute(''' INSERT INTO adminranking(id)
                VALUES (%s)''',(id,))
            else:
                cur.execute(''' INSERT INTO regular(id,subject_of_interest,job)
                VALUES (%s,%s,%s)''',(id,subject,job))
                cur.execute(''' INSERT INTO regularranking(id)
                VALUES (%s)''',(id,))
            conn.commit()
            cur.close()
            return redirect(url_for('login_page'))
    return render_template("signUp.html")
       
    return render_template("signUp.html")

def login_page():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=%s", (username,))
        newUser = user.get_user(username)
        if newUser != 0:
            if password == newUser.password:
                login_user(newUser)
                return redirect(url_for('main_page'))
            else:
                flash("Password is incorrect.")
                return render_template("login.html")
            cur.close()
        else:
            flash("User does not exist.")
            return render_template("login.html")
    return render_template("login.html")

def main_page():
    cur = conn.cursor()
    cur.execute("SELECT * FROM entry")
    entry = cur.fetchall()
    cur.execute("SELECT * FROM complaint")
    complaint = cur.fetchall()
    cur.execute("SELECT * FROM privilege")
    privilege = cur.fetchall()
    cur.execute("SELECT * FROM reply")
    reply = cur.fetchall()
    cur.execute("SELECT * FROM entry")
    entry2 = cur.fetchall()
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM users")
    users2 = cur.fetchall()
    return render_template('main.html',users=users, users2=users2, entry=entry, complaint=complaint, privilege=privilege, reply=reply, entry2=entry2)

def logout_page(value):
    logout_user()
    flash("You have logged out.")
    return redirect(url_for("main_page"))


def submit(sender_id, receiver_id, entry_id):
    if request.method == "POST":
        cur = conn.cursor()
        given_points = request.form["points"]
        cur.execute(''' UPDATE regularranking SET total_given_points = total_given_points + %s WHERE id = %s''', (given_points,sender_id))
        cur.execute(''' UPDATE adminranking SET total_points_from_users = total_points_from_users + %s WHERE id = %s''', (given_points,receiver_id))
        cur.execute(''' UPDATE adminranking SET total_points = total_points + %s WHERE id = %s''', (given_points,receiver_id))
        cur.execute(''' UPDATE reply SET given_points = given_points + %s WHERE entry_id = %s''', (given_points,entry_id))
        conn.commit()
        cur.close()
        return redirect(url_for("main_page"))

def delete_entry(entry_id, privilege, id):
    if request.method == "POST":
        cur = conn.cursor()
        if privilege == "False":
            cur.execute(''' DELETE FROM complaint WHERE entry_id = %s''', (entry_id,))
            cur.execute(''' UPDATE regularranking SET entry_count = entry_count - 1 WHERE id = %s''', (id,))
            cur.execute(''' DELETE FROM entry WHERE entry_id = %s''', (entry_id,))
            conn.commit()
            cur.close()
            return redirect(url_for("profile",id=id))
        else:
            cur.execute(''' SELECT * FROM reply WHERE entry_id = %s''', (entry_id,))
            row = cur.fetchone()
            complaintId = row[3]
            status = "Pending"
            cur.execute(''' UPDATE complaint SET status = %s WHERE entry_id = %s''', (status, complaintId))
            cur.execute(''' DELETE FROM reply WHERE entry_id = %s''', (entry_id,))
            cur.execute(''' UPDATE adminranking SET total_replies = total_replies - 1 WHERE id = %s''', (id,))
            cur.execute(''' DELETE FROM entry WHERE entry_id = %s''', (entry_id,))
            conn.commit()
            cur.close()
            return redirect(url_for("profile",id=id))
        
def change_name(user_id):
    if request.method == "POST":
        name = request.form["name"]
        cur = conn.cursor()
        cur.execute(''' UPDATE users SET name = %s WHERE id = %s''', (name, user_id))
        conn.commit()
        cur.close()
    return redirect(url_for("profile",id=user_id))

def change_surname(user_id):
    if request.method == "POST":
        surname = request.form["surname"]
        cur = conn.cursor()
        cur.execute(''' UPDATE users SET surname = %s WHERE id = %s''', (surname, user_id))
        conn.commit()
        cur.close()
    return redirect(url_for("profile",id=user_id))

def change_phone(user_id):
    if request.method == "POST":
        phone = request.form["phone"]
        cur = conn.cursor()
        cur.execute(''' UPDATE entry SET phone = %s WHERE id = %s''', (phone, user_id))
        conn.commit()
        cur.close()
    return redirect(url_for("profile",id=user_id))

def change_email(user_id):
    if request.method == "POST":
        email = request.form["email"]
        cur = conn.cursor()
        cur.execute(''' UPDATE entry SET email = %s WHERE id = %s''', (email, user_id))
        conn.commit()
        cur.close()
    return redirect(url_for("profile",id=user_id))


def delete_user(user_id,privilege):
    i = 0
    logout_user()
    if privilege == "False":
        cur = conn.cursor()
        cur.execute(''' SELECT * FROM regularranking WHERE id = %s''', (user_id,))
        row = cur.fetchone()
        entryCount = row[2]
        cur.execute(''' DELETE FROM regularranking WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM regular WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM privilege WHERE id = %s''', (user_id,))
        cur.execute(''' SELECT * FROM entry WHERE id = %s''', (user_id,))
        entry = cur.fetchall()
        while i < entryCount:
            cur.execute(''' DELETE FROM complaint WHERE entry_id = %s''', (entry[i][0],))
            i = i + 1
        cur.execute(''' DELETE FROM entry WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM users WHERE id = %s''', (user_id,))
        conn.commit()
        cur.close()
        return redirect(url_for("main_page"))
    else:
        cur = conn.cursor()
        cur.execute(''' SELECT * FROM adminranking WHERE id = %s''', (user_id,))
        row = cur.fetchone()
        entryCount = row[2]
        cur.execute(''' DELETE FROM adminranking WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM admin WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM privilege WHERE id = %s''', (user_id,))
        cur.execute(''' SELECT * FROM entry WHERE id = %s''', (user_id,))
        entry = cur.fetchall()
        while i < entryCount:
            cur.execute(''' SELECT * FROM reply WHERE entry_id = %s''', (entry[i][0],))
            row = cur.fetchone()
            complaintId = row[3]
            status = "Pending"
            cur.execute(''' UPDATE complaint SET status = %s WHERE entry_id = %s''', (status, complaintId))
            cur.execute(''' DELETE FROM reply WHERE entry_id = %s''', (entry[i][0],))
            i = i + 1
        cur.execute(''' DELETE FROM entry WHERE id = %s''', (user_id,))
        cur.execute(''' DELETE FROM users WHERE id = %s''', (user_id,))
        conn.commit()
        cur.close()
        return redirect(url_for("main_page"))


def allowed_image(filename):

    extensions = ["PNG", "JPEG", "JPG", "GIF"] 

    if not "." in filename:
        return False
    
    ext = filename.rsplit(".",1)[1]

    if ext.upper() in extensions:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    
    if int(filesize) <= 20000:
        return True
    else:
        return False

def add_image(user_id):
    if request.method == "POST":
        if request.files:
            
            image = request.files["image"]
            if image.filename == "":
                flash("Please choose a file.")
                return redirect(url_for("profile",id=user_id))
            if not allowed_image(image.filename):
                flash("File extension is not allowed.")
                return redirect(url_for("profile",id=user_id))

            binary_image = image.read()
            cur = conn.cursor()
            cur.execute("INSERT INTO images VALUES (%s,%s)", (user_id,psycopg2.Binary(binary_image),))
            conn.commit()
            cur.close()
    return redirect(url_for("profile",id=user_id))



