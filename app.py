# app.py

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# --- Dummy Data ---
clients = []
bookings = []
services = [
    # Updated prices to ZAR
    {'id': 1, 'name': 'Family Portrait Session', 'price': 1500},
    {'id': 2, 'name': 'Wedding Photography Package', 'price': 10000},
    {'id': 3, 'name': 'Professional Headshots', 'price': 1000},
]
print_products = [
    # Updated prices to ZAR
    {'id': 1, 'name': 'Canvas Print (16x20)', 'price': 750},
    {'id': 2, 'name': 'Photo Album', 'price': 1500},
]
print_orders = []

# --- Routes ---

@app.route('/')
def index():
    """Main dashboard view."""
    return render_template('dashboard.html', bookings=bookings, clients=clients)

@app.route('/clients')
def view_clients():
    """View all clients."""
    return render_template('clients.html', clients=clients)

@app.route('/clients/add', methods=['GET', 'POST'])
def add_client():
    """Add a new client."""
    if request.method == 'POST':
        new_id = max([c['id'] for c in clients]) + 1 if clients else 1
        new_client = {
            'id': new_id,
            'name': request.form['name'],
            'email': request.form['email'],
            'phone': request.form['phone']
        }
        clients.append(new_client)
        return redirect(url_for('view_clients'))
    return render_template('add_client.html')

@app.route('/clients/<int:client_id>')
def view_client_details(client_id):
    """View a single client's details and history."""
    client = next((c for c in clients if c['id'] == client_id), None)
    if client:
        client_bookings = [b for b in bookings if b['client_id'] == client_id]
        return render_template('client_details.html', client=client, bookings=client_bookings)
    return "Client not found", 404

@app.route('/clients/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    """Edit an existing client's details."""
    client = next((c for c in clients if c['id'] == client_id), None)
    if not client:
        return "Client not found", 404
    if request.method == 'POST':
        client['name'] = request.form['name']
        client['email'] = request.form['email']
        client['phone'] = request.form['phone']
        return redirect(url_for('view_client_details', client_id=client_id))
    return render_template('edit_client.html', client=client)

@app.route('/clients/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    """Delete a client."""
    global clients
    clients = [c for c in clients if c['id'] != client_id]
    return redirect(url_for('view_clients'))

@app.route('/bookings')
def view_bookings():
    """View all bookings."""
    return render_template('bookings.html', bookings=bookings)

@app.route('/bookings/add', methods=['GET', 'POST'])
def add_booking():
    """Add a new booking."""
    if request.method == 'POST':
        new_id = max([b['id'] for b in bookings]) + 1 if bookings else 1
        client = next((c for c in clients if str(c['id']) == request.form['client_id']), None)
        service = next((s for s in services if str(s['id']) == request.form['service_id']), None)
        
        if client and service:
            new_booking = {
                'id': new_id,
                'client_id': client['id'],
                'client_name': client['name'],
                'service_name': service['name'],
                'date': request.form['booking_date'],
                'time': request.form['booking_time']
            }
            bookings.append(new_booking)
        return redirect(url_for('view_bookings'))
    return render_template('add_booking.html', clients=clients, services=services)

@app.route('/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
def edit_booking(booking_id):
    """Edit an existing booking."""
    booking = next((b for b in bookings if b['id'] == booking_id), None)
    if not booking:
        return "Booking not found", 404
    if request.method == 'POST':
        client = next((c for c in clients if str(c['id']) == request.form['client_id']), None)
        service = next((s for s in services if str(s['id']) == request.form['service_id']), None)
        if client and service:
            booking['client_id'] = client['id']
            booking['client_name'] = client['name']
            booking['service_name'] = service['name']
            booking['date'] = request.form['booking_date']
            booking['time'] = request.form['booking_time']
        return redirect(url_for('view_bookings'))
    return render_template('edit_booking.html', booking=booking, clients=clients, services=services)

@app.route('/bookings/delete/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    """Delete a booking."""
    global bookings
    bookings = [b for b in bookings if b['id'] != booking_id]
    return redirect(url_for('view_bookings'))

@app.route('/prints')
def view_print_orders():
    """View all print orders."""
    return render_template('print_orders.html', print_orders=print_orders)

@app.route('/prints/add', methods=['GET', 'POST'])
def add_print_order():
    """Add a new print order."""
    if request.method == 'POST':
        new_id = max([p['id'] for p in print_orders]) + 1 if print_orders else 1
        client = next((c for c in clients if str(c['id']) == request.form['client_id']), None)
        product = next((p for p in print_products if str(p['id']) == request.form['product_id']), None)
        if client and product:
            new_order = {
                'id': new_id,
                'client_name': client['name'],
                'product_name': product['name'],
                'quantity': request.form['quantity'],
                'status': 'Ordered'
            }
            print_orders.append(new_order)
        return redirect(url_for('view_print_orders'))
    return render_template('add_print_order.html', clients=clients, products=print_products)

@app.route('/services')
def view_services():
    """View all services offered."""
    return render_template('services.html', services=services)

@app.route('/invoicing')
def view_invoices():
    """View and manage invoices."""
    invoices = [] # Dummy list
    return render_template('invoices.html', invoices=invoices)

if __name__ == '__main__':
    # Initialize some dummy data to work with
    clients = [
        {'id': 1, 'name': 'Rebafenyi Mudau', 'email': 'rebafenyiisrael@gmail.com', 'phone': '082 722 2080'},
        {'id': 2, 'name': 'Israel Vhadau', 'email': 'Israel.vhadau@izra.pri.za', 'phone': '076 892 1234'},
    ]
    bookings = [
        {'id': 101, 'client_id': 1, 'client_name': 'Rebafenyi Mudau', 'service_name': 'Family Portrait Session', 'date': '2025-08-15', 'time': '10:00'},
    ]
    app.run(debug=True)