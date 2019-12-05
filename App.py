from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sispavo'
mysql = MySQL(app)

app.secret_key = '?\xbf,\xb4\x8d\xa3"<\x9c\xb0@\x0f5\xab,w\xee\x8d$0\x13\x8b83'
csrf = CSRFProtect(app)

@app.route('/')
def Index():
    if 'email' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM registro ORDER BY id DESC LIMIT 5')
        data = cur.fetchall()
        return render_template('index.html', users = data)
    else:
        return redirect(url_for('Login'))

@app.route('/profile')
def Profile():
    if 'email' in session:
        cur = mysql.connection.cursor()
        cur.execute('SELECT username FROM user WHERE email = "' + session['email'] + '" limit 1')
        data = cur.fetchone()[0]
        return render_template('profile.html', username = data)
    else:
        return redirect(url_for('Login'))

@app.route('/add', methods=['POST'])
def Add():
    if request.method == 'POST':
        cedula = request.form['cedula']
        localidad = session['place']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM registro WHERE cedula = "' + cedula + '" limit 1')
        data = cur.rowcount
        if data > 0:
            userdata = cur.fetchone()
            usercedula = userdata[1]
            userlocalidad = userdata[2]
            userfecha = str(userdata[3])
            mensaje = usercedula +"/" + userlocalidad+"/" + userfecha
            flash(mensaje,'error')
        else:
            cur.execute('INSERT INTO registro (cedula,localidad) VALUES (%s,%s)',
            (cedula,localidad))
            mysql.connection.commit()
            flash('El usuario puede ingresar.','success')
        return redirect(url_for('Index'))

@app.route('/user')
def UserIndex():
    if 'email' in session:
        if session['role'] == 'Administrador':
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM user')
            data = cur.fetchall()
            return render_template('index-user.html', users = data)
        else:
            return redirect(url_for('Index'))
    else:
        return redirect(url_for('Login'))

@app.route('/user/add', methods=['POST'])
def UserAdd():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM user WHERE email = "' + email + '" limit 1')
        data = cur.rowcount
        if data > 0: 
            flash('El usuario ya ha sido agregado','error')
        else:

            cur.execute('INSERT INTO user (username,email,password,role) VALUES (%s,%s,%s,%s)',
            (username,email,generate_password_hash(password),role))
            mysql.connection.commit()
            flash('Usuario almacenado correctamente.','success')
        return redirect(url_for('UserIndex'))

@app.route('/user/edit/<id>')
def UserEdit(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM user WHERE id = %s',(id))
    data = cur.fetchall()
    return render_template('edit-user.html', user = data[0])

@app.route('/user/update/<id>',methods = ['POST'])
def UserUpdate(id):
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        role = request.form['role']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE user
        SET username = %s,
        email = %s,
        role = %s
        WHERE id = %s
        """,(username,email,role,id))
        mysql.connection.commit()
        flash('Datos actualizados correctamente','success')
        return redirect(url_for('UserIndex'))

@app.route('/user/delete/<string:id>')
def UserDelete(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM user WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Datos eliminados correctamente','success')
    return redirect(url_for('UserIndex'))

@app.route('/place')
def PlaceIndex():
    if 'email' in session:
        if session['role'] == 'Administrador':
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM place')
            data = cur.fetchall()
            return render_template('index-place.html', places = data)
        else:
            return redirect(url_for('Index'))
    else:
        return redirect(url_for('Login'))

@app.route('/place/add', methods=['POST'])
def PlaceAdd():
    if request.method == 'POST':
        nombre = request.form['nombre']
        user = session['email']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM place WHERE nombre = "' + nombre + '" limit 1')
        data = cur.rowcount
        if data > 0: 
            flash('El lugar ya ha sido agregado','error')
        else:
            cur.execute('INSERT INTO place (nombre,created_at) VALUES (%s,%s)',
            (nombre,user))
            mysql.connection.commit()
            flash('Lugar almacenado correctamente.','success')
        return redirect(url_for('PlaceIndex'))

@app.route('/place/edit/<id>')
def PlaceEdit(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM place WHERE id = %s',(id))
    data = cur.fetchall()
    return render_template('edit-place.html', place = data[0])

@app.route('/place/update/<id>',methods = ['POST'])
def PlaceUpdate(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        cur = mysql.connection.cursor()
        cur.execute("""
        UPDATE place
        SET nombre = %s
        WHERE id = %s
        """,(nombre,id))
        mysql.connection.commit()
        flash('Datos actualizados correctamente','success')
        return redirect(url_for('PlaceIndex'))

@app.route('/place/delete/<string:id>')
def PlaceDelete(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM place WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Datos eliminados correctamente','success')
    return redirect(url_for('PlaceIndex'))

@app.route('/login')
def Login():
    if 'email' in session:
        return redirect(url_for('Index'))
    else:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM place')
        data = cur.fetchall()
        return render_template('login.html', places = data)

@app.route('/logout')
def Logout():
    if 'email' in session:
        session.pop('email', None)
        session.pop('place', None) 
        session.pop('role', None)       
    return redirect(url_for('Login'))

@app.route('/login/auth', methods=['POST'])
def UserAuth():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        place = request.form['place']
        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM user WHERE email = "' + email + '" limit 1')
        count = cur.rowcount
        if count > 0: 
            data = cur.fetchone()[0]
            verif = check_password_hash(data,password)
            if verif:
                cur.execute('SELECT role FROM user WHERE email = "' + email + '" limit 1')
                role = cur.fetchone()[0]
                session['email'] = email
                session['place'] = place
                session['role'] = role
                
            else:
                flash('El correo o la contraseña son incorrectos.','error')   
        else:
            flash('El correo o la contraseña son incorrectos.','error')  
    return redirect(url_for('Index'))   

if __name__ == '__main__':
    app.run(debug = True)



