# wsgi.py
from flask import Flask, request, jsonify
from config import Config
app = Flask(__name__)
app.config.from_object(Config)


from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Order is important here!
db = SQLAlchemy(app)
ma = Marshmallow(app)

from models import Product
from schemas import products_schema, product_schema

@app.route('/products')
def products():
    products = db.session.query(Product).all() # SQLAlchemy request => 'SELECT * FROM products'
    return products_schema.jsonify(products)

@app.route('/api/v1/products', methods=['GET', 'POST'])
def my_products():
    if request.method == 'GET':
        return jsonify(PRODUCTS)
    elif request.method == 'POST':
        payload = request.get_json()
        new_product = Product()
        new_product.name = payload['name']
        db.session.add(new_product)
        db.session.commit()
        return '', 201
    else:
        return "Unimplemented method {0}".format(request.method), 500

@app.route('/api/v1/products/<int:product_id>', methods=['GET', 'DELETE', 'PATCH'])
def manage_product(product_id):
    if request.method in ['GET', 'DELETE']:
        return get_del_product(product_id)
    elif request.method == 'PATCH':
        return update_product(product_id)
    else:
        return "Unimplemented method {0}".format(request.method), 500

def update_product(product_id):
    product = db.session.query(Product).get(product_id)
    if product:
        payload = request.get_json()
        try:
            name = payload['name']
            if name:
                product.name = name
                db.session.commit()
                return '', 204
            else:
                return 'Invalid Name in payload', 422
        except KeyError:
            return 'No name in payload', 422

    return 'Product Not Found', 422

def get_del_product(product_id):
    product = db.session.query(Product).get(product_id)
    if product:
        if request.method == 'GET':
            return product_schema.jsonify(product), 200
        else:
            db.session.delete(product)
            db.session.commit()
            return '', 204
    return 'Product Not Found', 404
