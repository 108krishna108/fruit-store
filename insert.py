from app import app, db, Product  # Import Flask app, db, and Product model

# Define product data
products = [
    {'id': 1, 'name': 'Apple', 'description': 'Fresh and juicy apples.', 'price': 2.99, 'image': 'apple.jpg'},
    {'id': 2, 'name': 'Banana', 'description': 'Sweet and ripe bananas.', 'price': 1.20, 'image': 'banana.jpg'},
    {'id': 3, 'name': 'Cherry', 'description': 'Delicious, tangy cherries.', 'price': 4.00, 'image': 'cherry.jpg'},
    {'id': 4, 'name': 'Kiwi', 'description': 'Tropical and tangy kiwi fruits.', 'price': 2.50, 'image': 'kiwi.jpg'},
    {'id': 5, 'name': 'Lichi', 'description': 'Sweet and juicy lichi fruit.', 'price': 6.00, 'image': 'lichi.jpg'},
    {'id': 6, 'name': 'Mango', 'description': 'Fresh and sweet mangoes.', 'price': 1.80, 'image': 'mango.jpg'},
    {'id': 8, 'name': 'Orange', 'description': 'Tangy and juicy oranges.', 'price': 1.50, 'image': 'orange.jpg'},
    {'id': 9, 'name': 'Papaya', 'description': 'Sweet and tropical papayas.', 'price': 3.00, 'image': 'papaya.jpg'},
    {'id': 10, 'name': 'Pear', 'description': 'Crisp and sweet pears.', 'price': 2.50, 'image': 'pear.jpg'},
    {'id': 11, 'name': 'Starfruit', 'description': 'Unique and tangy starfruit.', 'price': 5.50, 'image': 'starfruit.jpg'},
    {'id': 12, 'name': 'Strawberry', 'description': 'Fresh and sweet strawberries.', 'price': 3.50, 'image': 'strawberry.jpg'},
    {'id': 13, 'name': 'Sweetpotato', 'description': 'Sweet and nutritious.', 'price': 2.80, 'image': 'sweetpotato.jpg'},
    {'id': 14, 'name': 'Watermelon', 'description': 'Refreshing watermelon.', 'price': 6.00, 'image': 'watermelon.jpg'}
]

# Insert products into the database
def insert_products():
    with app.app_context():  # Ensure app context is available
        try:
            for product in products:
                # Create a new product instance
                new_product = Product(
                    id=product['id'],
                    name=product['name'],
                    description=product['description'],
                    price=product['price'],
                    image=product['image']
                )
                # Add the product to the session
                db.session.add(new_product)

            # Commit the session to save data in the database
            db.session.commit()
            print("Products inserted successfully.")
        except Exception as e:
            # Rollback in case of an error
            db.session.rollback()
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    with app.app_context():  # Ensure the app context for any setup
        db.create_all()  # Create the table if it doesn't already exist
    insert_products()
