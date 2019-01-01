import os
import datetime
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = 'sqlite:///{}'.format(os.path.join(project_dir, 'chinook.db'))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SECRET_KEY'] = 'fuck-the-fucking-borovik'
db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
Bootstrap(app)
table_names = ['invoices', 'customers']


class Invoices(db.Model):
    __table__ = db.Model.metadata.tables['invoices']


class Customers(db.Model):
    __table__ = db.Model.metadata.tables['customers']


def format_customer(customer):
    return f'{customer.CustomerId}: {customer.FirstName} {customer.LastName}'


app.jinja_env.globals.update(format_customer=format_customer)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.form:
        table_name = request.form.get('table')
        return redirect(f'/list/{table_name}')
    return render_template('index.html', table_names=table_names)


@app.route('/list/<table_name>', methods=['GET'])
def list_table(table_name):
    if table_name == 'invoices':
        return render_template('list_invoices.html', invoices=Invoices.query.all(), customers=Customers.query.all())
    elif table_name == 'customers':
        return render_template('list_customers.html', customers=Customers.query.all())


@app.route('/edit/invoices/<int:invoice_id>', methods=['GET', 'POST'])
def edit_invoice(invoice_id):
    if request.form:
        form = request.form
        invoice = Invoices.query.get(invoice_id)
        invoice.CustomerId = int(form.get('customer'))
        invoice.BillingAddress = form.get('address')
        invoice.Total = float(form.get('total'))
        invoice.InvoiceDate = datetime.datetime.strptime(form.get('date'), '%Y-%m-%d')
        db.session.commit()
        return redirect('/list/invoices')
    return render_template('edit_invoice.html', invoice=Invoices.query.get(invoice_id), customers=Customers.query.all())


@app.route('/add/invoice', methods=['POST'])
def add_invoice():
    if request.form:
        form = request.form
        invoice = Invoices(CustomerId=int(form.get('customer')),
                           BillingAddress=form.get('address'),
                           BillingCity='NA',
                           BillingState='NA',
                           BillingCountry='NA',
                           BillingPostalCode='000001',
                           Total=float(form.get('total')),
                           InvoiceDate=datetime.datetime.strptime(form.get('date'), '%Y-%m-%d'))
        db.session.add(invoice)
        db.session.commit()
    return redirect('/list/invoices')


# --------DELETE--------
@app.route('/delete/invoices/<int:invoice_id>', methods=['POST'])
def delete_invoice(invoice_id):
    db.session.delete(Invoices.query.get(invoice_id))
    db.session.commit()
    return redirect('/list/invoices')


@app.route('/delete/customers/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    db.session.delete(Customers.query.get(customer_id))
    db.session.commit()
    return redirect('/list/customers')
# --------END DELETE SECTION--------


@app.route('/update', methods=['POST'])
def update():
    newtitle = request.form.get('newtitle')
    oldtitle = request.form.get('oldtitle')
    # book = Book.query.filter_by(title=oldtitle).first()
    # book.title = newtitle
    db.session.commit()
    return redirect('/')


@app.route('/delete', methods=['POST'])
def delete():
    title = request.form.get('title')
    # book = Book.query.filter_by(title=title).first()
    # db.session.delete(book)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
