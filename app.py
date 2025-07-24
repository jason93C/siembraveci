from flask import Flask, request, render_template,redirect,url_for,session, request
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin.menu import MenuLink
import os
from flask_admin.form import ImageUploadField
from wtforms.fields import SelectField

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
app.config['UPLOAD_FOLDER'] = os.path.join('static','upload')

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
    def render(self, name, value, **kwargs):

        kwargs["logout_button"] = Markup('<a class = "btn btn-danger" href="/admin/logout">cerrar sesion</a>')
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
    categoria = db.relationship('Categoria', backref='productos')

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_ud_usuario = db.Column(db.Integer, primary_key=True)
    nom_usuario = db.Column(db.String(50), nullable=False)
    ape_usuario = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)  # usuario de login
    password = db.Column(db.String(128), nullable=False)

class ProductoAdmin(ModelView):
    # Personaliza el campo imagen para que permita subir archivos
    form_extra_fields = {
        'imagen': ImageUploadField('Imagen del producto',
        base_path=os.path.join(os.getcwd(), 'static', 'uploads'),
        relative_path='uploads/',
        url_relative_path='static/uploads/')
}
    # Sobrescribimos el tipo de campo
    form_overrides = {
    'id_categoria': SelectField
    }
    form_columns = ['nombre', 'descripcion', 'imagen', 'precio','id_categoria']

# Configuramos el comportamiento del SelectField
    form_args = {
        'id_categoria': {
        'coerce': int,
        'label': 'Categoría'
    }
}

# Llenamos las opciones para el campo select (crear)
    def create_form(self, obj=None):
        form = super().create_form(obj)
        form.id_categoria.choices = [(c.id_categoria, c.nom_categoria) for c in Categoria.query.all()]
        return form
# Llenamos las opciones para el campo select (editar)
    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        form.id_categoria.choices = [(c.id_categoria, c.nom_categoria) for c in Categoria.query.all()]
        return form

# Flask-Admin
admin = Admin(app, name='Panel Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
admin.add_view(ModelView(Usuario, db.session))
admin.add_view(ModelView(Categoria, db.session))
admin.add_view(ProductoAdmin(Producto, db.session))
admin.add_link(MenuLink(name='cerrar sesion',category='', url='/admin/logout'))


# Agregar al carrito
@app.route('/agregar/<int:id>')
def agregar_al_carrito(id):
    if "carrito" not in session:
        session["carrito"] = {}

    carrito = session["carrito"]

    if str(id) in carrito:
        carrito[str(id)] += 1
    else:
        carrito[str(id)] = 1

    session["carrito"] = carrito
    return redirect(url_for('tienda'))

# Ver carrito
@app.route('/carrito')
def ver_carrito():
    carrito = session.get("carrito", {})
    total = 0
    detalle = []

    for id, cantidad in carrito.items():
        prod = Producto.query.get(int(id))
        if prod:
            subtotal = prod.precio * cantidad
            total += subtotal
            detalle.append({
                "id": prod.id,
                "nombre": prod.nombre,
                "precio": prod.precio,
                "cantidad": cantidad,
                "subtotal": subtotal
            })

    return render_template("carrito.html", carrito=detalle, total=total)

# Eliminar un producto del carrito
@app.route('/eliminar/<int:id>')
def eliminar_producto(id):
    carrito = session.get("carrito", {})
    carrito.pop(str(id), None)
    session["carrito"] = carrito
    return redirect(url_for('ver_carrito'))

# Vaciar carrito
@app.route('/vaciar')
def vaciar_carrito():
    session.pop("carrito", None)
    return redirect(url_for('tienda'))


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
    return render_template('productos.html')

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