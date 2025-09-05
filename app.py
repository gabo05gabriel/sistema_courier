from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# URI de PostgreSQL (reemplaza con tus credenciales)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:OgnOBIGvrOGSZLLSwelkrHIDpKducfQm@crossover.proxy.rlwy.net:40695/railway'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

# Rutas y funcionalidad CRUD

@app.route('/')
@app.route('/dashboard')  # Página inicial como Dashboard
def dashboard():
    return render_template('dashboard.html')

@app.route('/usuarios')
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/usuario/add', methods=['GET', 'POST'])
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
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuarios'))

@app.route('/zonas')
def zonas():
    # Aquí va la lógica para mostrar zonas
    return render_template('zonas.html')

@app.route('/rutas')
def rutas():
    # Aquí va la lógica para mostrar rutas
    return render_template('rutas.html')

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
