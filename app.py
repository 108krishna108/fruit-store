from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os  # Added to handle paths and Azure-specific settings

# Get current date and time
current_datetime = datetime.now()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Define database path for local and Azure deployments
if 'HOME' in os.environ:  # On Azure App Service
    DATABASE_PATH = os.path.join(os.environ['HOME'], 'ecommerce.db')  # Persistent storage in Azure
else:
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ecommerce.db')  # Local

# Helper function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database with tables
def init_db():
    conn = get_db_connection()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin BOOLEAN DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        image TEXT
    );
    
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES user (id),
        FOREIGN KEY (product_id) REFERENCES product (id)
    );
    ''')
    conn.close()

# Initialize the database if it doesn't exist
if not os.path.exists(DATABASE_PATH):  # Ensure the database file is created
    init_db()

# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    products = conn.execute('SELECT * FROM product').fetchall()
    conn.close()
    return render_template('home.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('home'))

        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        is_admin = 'is_admin' in request.form

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO user (username, password, is_admin) VALUES (?, ?, ?)',
                         (username, hashed_password, is_admin))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists', 'warning')
            conn.close()
            return redirect(url_for('register'))

        conn.close()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']

        conn = get_db_connection()
        conn.execute('INSERT INTO product (name, description, price) VALUES (?, ?, ?)',
                     (name, description, price))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template('edit_product.html')

@app.route('/edit_product', methods=['GET'])
def edit_product():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM product').fetchall()
    conn.close()
    return render_template('edit_product.html', products=products)

@app.route('/update_product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    conn = get_db_connection()
    conn.execute('UPDATE product SET name = ?, description = ?, price = ? WHERE id = ?',
                 (request.form['name'], request.form['description'], request.form['price'], product_id))
    conn.commit()
    conn.close()
    return redirect(url_for('edit_product'))

@app.route('/shipping_details/<int:product_id>', methods=['GET', 'POST'])
def shipping_details(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM product WHERE id = ?', (product_id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        address = request.form['address']
        total_price = product['price'] * quantity
        return redirect(url_for('order_confirmation', product_id=product['id'], quantity=quantity,
                                total_price=total_price, address=address))

    return render_template('shipping_page.html', product=product)

@app.route('/order_confirmation')
def order_confirmation():
    product_id = request.args.get('product_id')
    quantity = request.args.get('quantity')
    total_price = float(request.args.get('total_price'))
    address = request.args.get('address')

    return render_template('order.html', product_id=product_id, quantity=quantity,
                           total_price=total_price, address=address)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
