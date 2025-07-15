from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask import redirect, url_for, session, requet
import psycopg2

conn = psycopg2.connect(
    host="dpg-d1o704ffte5s73aubihg-a.oregon-postgres.render.com",
    database="tienda_siembraveci",
    user="jason",
    password="PhIdQ6RtPUEAaHbvhtC2XHIiC98bEqOR"
)
# Crear la app Flask
app = Flask(__name__)
app.secret_key = 'Rr_123456'

# Conexión con PostgreSQL
# conexion con render
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jason:PhIdQ6RtPUEAaHbvhtC2XHIiC98bEqOR@dpg-d1o704ffte5s73aubihg-a.oregon-postgres.render.com:5432/tienda_siembraveci'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy directamente
db = SQLAlchemy(app)

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# Vista protegida para cada modelo
class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get('admin_logged_in')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_login'))

# Modelos
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True)
    nom_categoria = db.Column(db.String(100), nullable=False)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(200))
    precio = db.Column(db.Float, nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), nullable=False)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_ud_usuario = db.Column(db.Integer, primary_key=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    ape_usuario = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)  # usuario de login
    password = db.Column(db.String(128), nullable=False)

# Flask-Admin
admin = Admin(app, name='Panel Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(ModelView(Usuario, db.session))
admin.add_view(ModelView(Categoria, db.session))
admin.add_view(ModelView(Producto, db.session))





@app.route("/")
def home():
    logo = {
        'nombre': 'logo',
        'imagen': 'segunda.png'  # Solo el nombre del archivo
    }
    return render_template('index.html', logo=logo)

@app.route("/inicio/")
def inicio():
    return render_template("index.html")

@app.route("/plantilla1")
def ejemplo1():
    return render_template("plantilla1.html")

@app.route("/plantilla2")
def ejemplo2():
    return render_template("plantilla2.html")

@app.route('/productos')
def productos():
    return render_template('plantilla1.html')

@app.route('/servicios')
def servicios():
    return render_template("plantilla2.html")

@app.route('/ventas')
def ventas():
    productos = Producto.query.all()
    return render_template('ventas.html', productos=productos)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Usuario.query.filter_by(username=username, password=password).first()

        if user:
            session['admin_logged_in'] = True
            return redirect('/admin')
        else:
            error = 'Usuario o contraseña incorrectos'
    
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)