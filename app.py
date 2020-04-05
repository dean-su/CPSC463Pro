from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from pytz import timezone
import pytz
import os
from flask_marshmallow import Marshmallow

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'manufacturer.db')
db = SQLAlchemy(app)
ma = Marshmallow(app)


def get_pst_time():
    # date_format='%m/%d/%Y %H:%M:%S %Z'
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(timezone('US/Pacific'))
    # pstDateTime=date.strftime(date_format)
    pstDateTime = date
    return pstDateTime


@app.cli.command('db_create')
def db_create():
    db.create_all()
    print('Database created!')


@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print('DB dropped!')


@app.cli.command('db_seed')
def db_seed():
    manufacturer = Manufacturer(part_name='Wagner QuickStop Semi-Metallic Disc Brake Pad Set',
                part_number='ZX914A',
                supplier_name="Wagner AUTO Parts",
                order_Status="Supplier preparing")

    db.session.add(manufacturer)

    test_user = Retail_Store(part_name='Wagner QuickStop Semi-Metallic Disc Brake Pad Set',
                part_number='ZX914A',
                auto_store_name="Pep boys Bakersfield",
                order_Status="Supplier preparing")


    db.session.add(test_user)
    db.session.commit()
    print('DB seeded!')


@app.route('/')
def hello_world():
    return 'Hello World! CPSC463'


@app.route('/m_new_order', methods=['POST'])
def m_new_order():

    part_number = request.form['part_number']
    part_name = request.form['part_name']
    supplier_name = request.form['supplier_name']
    order_Status = request.form['order_Status']
    order_time = get_pst_time()
    shipping_time = None
    modify_time = get_pst_time()
    manufacturer = Manufacturer(part_number=part_number, part_name=part_name, supplier_name=supplier_name, order_Status=order_Status, order_time=order_time,
                shipping_time=shipping_time, modify_time=modify_time)
    db.session.add(manufacturer)

    db.session.commit()
    return jsonify(message='Manufacturer order created successfully!'), 201


@app.route('/m_find_order_by_id/<int:id>', methods=['GET'])
def m_find_order_by_id(id: int):
    manufacturer = Manufacturer.query.filter_by(order_id=id).first()
    if manufacturer:
        result = manufacturer_schema.dump(manufacturer)
        return jsonify(result)
    else:
        return jsonify(message="That order does not exist"), 404


@app.route('/m_delete_order_by_id/<int:id>', methods=['DELETE'])
def remove_order(id: int):
    manufacturer = Manufacturer.query.filter_by(order_id=id).first()
    if manufacturer:
        db.session.delete(manufacturer)
        db.session.commit()
        return jsonify(message="You deleted an order"), 202
    else:
        return jsonify(message="That order does not exist"), 404


@app.route('/r_new_order', methods=['POST'])
def r_new_order():

    part_number = request.form['part_number']
    part_name = request.form['part_name']
    auto_store_name = request.form['auto_store_name']
    order_Status = request.form['order_Status']
    order_time = get_pst_time()
    shipping_time = None
    modify_time = get_pst_time()
    retail_Store = Retail_Store(part_number=part_number, part_name=part_name, auto_store_name=auto_store_name, order_Status=order_Status, order_time=order_time,
                shipping_time=shipping_time, modify_time=modify_time)
    db.session.add(retail_Store)

    db.session.commit()
    return jsonify(message='Retail Store order created successfully!'), 201


@app.route('/r_find_order_by_id/<int:id>', methods=['GET'])
def r_find_order_by_id(id: int):
    retail_Store = Retail_Store.query.filter_by(order_id=id).first()
    if retail_Store:
        result = retail_store_schema.dump(retail_Store)
        return jsonify(result)
    else:
        return jsonify(message="That order does not exist"), 404


@app.route('/r_delete_order_by_id/<int:id>', methods=['DELETE'])
def remove_retail_store_order(id: int):
    retail_Store = Retail_Store.query.filter_by(order_id=id).first()
    if retail_Store:
        db.session.delete(retail_Store)
        db.session.commit()
        return jsonify(message="You deleted an order"), 202
    else:
        return jsonify(message="That order does not exist"), 404


# database models
class Retail_Store(db.Model):
    __tablename__ = 'tb_retail_store'
    order_id = Column(Integer, primary_key=True)
    part_number = Column(String)
    part_name = Column(String)
    auto_store_name = Column(String)
    order_Status = Column(String)
    order_time = Column(DateTime, default=get_pst_time())
    shipping_time = Column(DateTime, default=None)
    modify_time = Column(DateTime, default=get_pst_time())


class Manufacturer(db.Model):
    __tablename__ = 'tb_manufacturer'
    order_id = Column(Integer, primary_key=True)
    part_number = Column(String)
    part_name = Column(String)
    supplier_name = Column(String)
    order_Status = Column(String)
    order_time = Column(DateTime, default=get_pst_time())
    shipping_time = Column(DateTime, default=None)
    modify_time = Column(DateTime, default=get_pst_time())


class RetailStoreSchema(ma.Schema):
    class Meta:
        fields = ('order_id', 'part_number', 'part_name', 'auto_store_name', 'order_Status', 'order_time', 'shipping_time',  'modify_time')


class ManufacturerSchema(ma.Schema):
    class Meta:
        fields = ('order_id', 'part_number', 'part_name', 'supplier_name', 'order_Status', 'order_time', 'shipping_time',  'modify_time')



retail_store_schema = RetailStoreSchema()
retail_stores_schema = RetailStoreSchema(many=True)

manufacturer_schema = ManufacturerSchema()
manufacturers_schema = ManufacturerSchema(many=True)


if __name__ == '__main__':
    app.run()
