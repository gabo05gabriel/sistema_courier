from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
# URI de PostgreSQL (reemplaza con tus credenciales)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:OgnOBIGvrOGSZLLSwelkrHIDpKducfQm@crossover.proxy.rlwy.net:40695/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'jwt-secret'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('rol') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Inicializar la base de datos
db = SQLAlchemy(app)

# Definir los modelos de base de datos (tabla 'roles', 'usuarios', etc.)

class Rol(db.Model):
    __tablename__ = 'roles'  # Asegura que la tabla se llame roles
    rol_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'  # Asegura que la tabla se llame usuarios
    usuario_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    contrasena = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.rol_id'), nullable=False)
    rol = db.relationship('Rol', backref='usuarios')


class Zona(db.Model):
    __tablename__ = 'zonas'
    zona_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)


class Ruta(db.Model):
    __tablename__ = 'rutas'
    ruta_id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    zona_id = db.Column(db.Integer, db.ForeignKey('zonas.zona_id'), nullable=False)
    zona = db.relationship('Zona', backref='rutas')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and usuario.contrasena == contrasena:
            access_token = create_access_token(identity={'id': usuario.usuario_id, 'rol': usuario.rol.nombre})
            session['token'] = access_token
            session['rol'] = usuario.rol.nombre
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenciales inválidas')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# Rutas y funcionalidad CRUD

@app.route('/')
@app.route('/dashboard')  # Página inicial como Dashboard
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/usuario/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        contrasena = request.form['contrasena']
        rol_id = request.form['rol_id']
        new_usuario = Usuario(nombre=nombre, email=email, telefono=telefono, contrasena=contrasena, rol_id=rol_id)
        db.session.add(new_usuario)
        db.session.commit()
        return redirect(url_for('usuarios'))
    return render_template('add_usuario.html')


@app.route('/usuario/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.email = request.form['email']
        usuario.telefono = request.form['telefono']
        usuario.contrasena = request.form['contrasena']
        usuario.rol_id = request.form['rol_id']
        db.session.commit()
        return redirect(url_for('usuarios'))
    return render_template('edit_usuario.html', usuario=usuario)


@app.route('/usuario/delete/<int:id>')
@login_required
@admin_required
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuarios'))


@app.route('/roles')
@login_required
@admin_required
def roles():
    roles = Rol.query.all()
    return render_template('roles.html', roles=roles)


@app.route('/rol/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_rol():
    if request.method == 'POST':
        nombre = request.form['nombre']
        new_rol = Rol(nombre=nombre)
        db.session.add(new_rol)
        db.session.commit()
        return redirect(url_for('roles'))
    return render_template('add_rol.html')


@app.route('/rol/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_rol(id):
    rol = Rol.query.get_or_404(id)
    if request.method == 'POST':
        rol.nombre = request.form['nombre']
        db.session.commit()
        return redirect(url_for('roles'))
    return render_template('edit_rol.html', rol=rol)


@app.route('/rol/delete/<int:id>')
@login_required
@admin_required
def delete_rol(id):
    rol = Rol.query.get_or_404(id)
    db.session.delete(rol)
    db.session.commit()
    return redirect(url_for('roles'))


@app.route('/zonas')
@login_required
@admin_required
def zonas():
    zonas = Zona.query.all()
    return render_template('zonas.html', zonas=zonas)


@app.route('/zona/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_zona():
    if request.method == 'POST':
        nombre = request.form['nombre']
        new_zona = Zona(nombre=nombre)
        db.session.add(new_zona)
        db.session.commit()
        return redirect(url_for('zonas'))
    return render_template('add_zona.html')


@app.route('/zona/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_zona(id):
    zona = Zona.query.get_or_404(id)
    if request.method == 'POST':
        zona.nombre = request.form['nombre']
        db.session.commit()
        return redirect(url_for('zonas'))
    return render_template('edit_zona.html', zona=zona)


@app.route('/zona/delete/<int:id>')
@login_required
@admin_required
def delete_zona(id):
    zona = Zona.query.get_or_404(id)
    db.session.delete(zona)
    db.session.commit()
    return redirect(url_for('zonas'))


@app.route('/rutas')
@login_required
@admin_required
def rutas():
    rutas = Ruta.query.all()
    return render_template('rutas.html', rutas=rutas)


@app.route('/ruta/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_ruta():
    zonas = Zona.query.all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        zona_id = request.form['zona_id']
        new_ruta = Ruta(nombre=nombre, zona_id=zona_id)
        db.session.add(new_ruta)
        db.session.commit()
        return redirect(url_for('rutas'))
    return render_template('add_ruta.html', zonas=zonas)


@app.route('/ruta/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_ruta(id):
    ruta = Ruta.query.get_or_404(id)
    zonas = Zona.query.all()
    if request.method == 'POST':
        ruta.nombre = request.form['nombre']
        ruta.zona_id = request.form['zona_id']
        db.session.commit()
        return redirect(url_for('rutas'))
    return render_template('edit_ruta.html', ruta=ruta, zonas=zonas)


@app.route('/ruta/delete/<int:id>')
@login_required
@admin_required
def delete_ruta(id):
    ruta = Ruta.query.get_or_404(id)
    db.session.delete(ruta)
    db.session.commit()
    return redirect(url_for('rutas'))

@app.route('/recojos')
def recojos():
    # Aquí va la lógica para mostrar recojos
    return render_template('recojos.html')

@app.route('/entregas')
def entregas():
    # Aquí va la lógica para mostrar entregas
    return render_template('entregas.html')

if __name__ == '__main__':
    app.run(debug=True)
