from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


try:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/articulos'
    db = SQLAlchemy(app)
    db.create_all()
    print("Tablas creadas con éxito.")
except Exception as e:
    print(f"Error al crear tablas: {str(e)}")
import requests



# Define el modelo de Artículo
class Articulo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(10), unique=True, nullable=False)
    descripcion_corta = db.Column(db.String(100), nullable=False)
    descripcion_larga = db.Column(db.String(500), nullable=False)
    unidad_medida = db.Column(db.String(20), nullable=False)
    costo = db.Column(db.Float, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    tipo_cambio = db.Column(db.Float)
    precio_dolares = db.Column(db.Float)

# Crear la tabla en la base de datos (debería ejecutarse solo una vez)


# Rutas y controladores para listar los artículos
@app.route('/')
def listar_articulos():
    articulos = Articulo.query.all()
    return render_template('index.html', articulos=articulos)
@app.route('/detalle_articulo/<int:id>')
def detalle_articulo(id):
    articulo = Articulo.query.get(id)
    if articulo is not None:
        return render_template('detalle_articulo.html', articulo=articulo)
    else:
        # Manejar el caso en el que el artículo no existe
        return 'Artículo no encontrado', 404

# Ruta para crear un nuevo artículo
@app.route('/nuevo_articulo', methods=['GET', 'POST'])
def nuevo_articulo():
    if request.method == 'POST':
        # Obtener los datos del formulario
        clave = request.form['clave']
        descripcion_corta = request.form['descripcion_corta']
        descripcion_larga = request.form['descripcion_larga']
        unidad_medida = request.form['unidad_medida']
        costo = float(request.form['costo'])
        precio = float(request.form['precio'])

        # Consultar la API del Banco de México para obtener el tipo de cambio
        token = '9b096caa50c1fa65f8747351496d8e44599d18c042ba188509eb4aa9f545178a'
        api_url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno'
        headers = {'Bmx-Token': token}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            tipo_cambio = float(data['bmx']['series'][0]['datos'][0]['dato'])
            precio_dolares = precio / tipo_cambio

            # Crear un nuevo artículo con los datos ingresados y el tipo de cambio obtenido
            nuevo_articulo = Articulo(
                clave=clave,
                descripcion_corta=descripcion_corta,
                descripcion_larga=descripcion_larga,
                unidad_medida=unidad_medida,
                costo=costo,
                precio=precio,
                tipo_cambio=tipo_cambio,
                precio_dolares=precio_dolares
            )

            db.session.add(nuevo_articulo)
            db.session.commit()

            return redirect(url_for('listar_articulos'))
        else:
            # Manejar el caso en el que no se pueda obtener el tipo de cambio
            return 'Error al obtener el tipo de cambio. Código de estado: {}'.format(response.status_code)

    return render_template('nuevo_articulo.html')
if __name__ == '__main__':
    app.run(debug=True)
