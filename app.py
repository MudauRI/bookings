# app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Database Models ---

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    bookings = db.relationship('Booking', backref='client', lazy=True)
    print_orders = db.relationship('PrintOrder', backref='client', lazy=True)

    def __repr__(self):
        return f"Client('{self.name}', '{self.email}')"

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    bookings = db.relationship('Booking', backref='service', lazy=True)

    def __repr__(self):
        return f"Service('{self.name}', '{self.price}')"

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)

    def __repr__(self):
        return f"Booking('{self.date}', '{self.time}')"

class PrintProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    print_orders = db.relationship('PrintOrder', backref='product', lazy=True)

    def __repr__(self):
        return f"PrintProduct('{self.name}', '{self.price}')"

class PrintOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Ordered')
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('print_product.id'), nullable=False)

    def __repr__(self):
        return f"PrintOrder('{self.quantity}', '{self.status}')"

# --- Routes ---

@app.route('/')
def index():
    """Main dashboard view."""
    # Fetch upcoming bookings (e.g., for today or later)
    upcoming_bookings = Booking.query.filter(Booking.date >= datetime.today().date()).order_by(Booking.date).limit(5).all()
    recent_clients = Client.query.order_by(Client.id.desc()).limit(5).all()
    return render_template('dashboard.html', bookings=upcoming_bookings, clients=recent_clients)

@app.route('/clients')
def view_clients():
    """View all clients."""
    all_clients = Client.query.all()
    return render_template('clients.html', clients=all_clients)

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    """Add a new client."""
    if request.method == 'POST':
        new_client = Client(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone']
        )
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for('view_clients'))
    return render_template('add_client.html')

@app.route('/clients/<int:client_id>')
def view_client_details(client_id):
    """View a single client's details and history."""
    client = Client.query.get_or_404(client_id)
    client_bookings = Booking.query.filter_by(client_id=client_id).order_by(Booking.date.desc()).all()
    return render_template('client_details.html', client=client, bookings=client_bookings)

@app.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """Edit an existing client's details."""
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        client.name = request.form['name']
        client.email = request.form['email']
        client.phone = request.form['phone']
        db.session.commit()
        return redirect(url_for('view_client_details', client_id=client.id))
    return render_template('edit_client.html', client=client)

@app.route('/clients/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    """Delete a client and their associated bookings/orders."""
    client = Client.query.get_or_404(client_id)
    # Delete related bookings and print orders first to avoid foreign key errors
    Booking.query.filter_by(client_id=client.id).delete()
    PrintOrder.query.filter_by(client_id=client.id).delete()
    db.session.delete(client)
    db.session.commit()
    return redirect(url_for('view_clients'))

@app.route('/bookings')
def view_bookings():
    """View all bookings."""
    all_bookings = Booking.query.all()
    return render_template('bookings.html', bookings=all_bookings)

@app.route('/bookings/add', methods=['GET', 'POST'])
def add_booking():
    """Add a new booking."""
    clients = Client.query.all()
    services = Service.query.all()
    if request.method == 'POST':
        try:
            booking_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date()
            booking_time = datetime.strptime(request.form['booking_time'], '%H:%M').time()
            new_booking = Booking(
                date=booking_date,
                time=booking_time,
                client_id=request.form['client_id'],
                service_id=request.form['service_id']
            )
            db.session.add(new_booking)
            db.session.commit()
            return redirect(url_for('view_bookings'))
        except (ValueError, IndexError):
            return "Invalid date or time format.", 400
    return render_template('add_booking.html', clients=clients, services=services)

@app.route('/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    """Edit an existing booking."""
    booking = Booking.query.get_or_404(booking_id)
    clients = Client.query.all()
    services = Service.query.all()
    if request.method == 'POST':
        try:
            booking.date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date()
            booking.time = datetime.strptime(request.form['booking_time'], '%H:%M').time()
            booking.client_id = request.form['client_id']
            booking.service_id = request.form['service_id']
            db.session.commit()
            return redirect(url_for('view_bookings'))
        except (ValueError, IndexError):
            return "Invalid date or time format.", 400
    return render_template('edit_booking.html', booking=booking, clients=clients, services=services)

@app.route('/bookings/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    """Delete a booking."""
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('view_bookings'))

@app.route('/prints')
def view_print_orders():
    """View all print orders."""
    all_print_orders = PrintOrder.query.all()
    return render_template('print_orders.html', print_orders=all_print_orders)

@app.route('/prints/add', methods=['GET', 'POST'])
def add_print_order():
    """Add a new print order."""
    clients = Client.query.all()
    products = PrintProduct.query.all()
    if request.method == 'POST':
        new_order = PrintOrder(
            quantity=request.form['quantity'],
            client_id=request.form['client_id'],
            product_id=request.form['product_id']
        )
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('view_print_orders'))
    return render_template('add_print_order.html', clients=clients, products=products)

@app.route('/services')
def view_services():
    """View all services offered."""
    all_services = Service.query.all()
    return render_template('services.html', services=all_services)

@app.route('/invoicing')
def view_invoices():
    """View and manage invoices."""
    invoices = []  # Invoicing logic would go here
    return render_template('invoices.html', invoices=invoices)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Add dummy data only if tables are empty
        if not Client.query.first():
            client1 = Client(name='Rebafenyi Mudau', email='rebafenyiisrael@gmail.com', phone='082 722 2080')
            client2 = Client(name='Israel Vhadau', email='israel.vhadau@izra.pri.za', phone='076 892 1234')
            db.session.add(client1)
            db.session.add(client2)

            service1 = Service(name='Family Portrait Session', price=1500.00)
            service2 = Service(name='Wedding Photography Package', price=10000.00)
            service3 = Service(name='Professional Headshots', price=1000.00)
            db.session.add(service1)
            db.session.add(service2)
            db.session.add(service3)

            product1 = PrintProduct(name='Canvas Print (16x20)', price=750.00)
            product2 = PrintProduct(name='Photo Album', price=1500.00)
            db.session.add(product1)
            db.session.add(product2)

            db.session.commit()

            booking1 = Booking(date=datetime(2025, 8, 15), time=datetime(2025, 8, 15, 10, 0), client=client1, service=service1)
            booking2 = Booking(date=datetime(2025, 9, 20), time=datetime(2025, 9, 20, 14, 30), client=client2, service=service2)
            db.session.add(booking1)
            db.session.add(booking2)
            db.session.commit()

    app.run(debug=True)