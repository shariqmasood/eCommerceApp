# ====================
# seed_products.py
# ====================
"""
Seed your database with sample Products. Deleting existing entries
ensures placeholder images refresh on each run.

Usage:
    python seed_products.py
"""
from app import create_app
from models import db, Product

# Sample products to seed into the inventory
products_data = [
    {
        "name": "Wireless Ergonomic Mouse",
        "description": "Comfort-fit wireless mouse with adjustable DPI and silent clicks.",
        "price_cents": 2499,
        # Using dummyimage.com for reliable placeholder images
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Wireless+Ergonomic+Mouse"
    },
    {
        "name": "Mechanical RGB Keyboard",
        "description": "Backlit mechanical keyboard with customizable RGB lighting and tactile switches.",
        "price_cents": 7499,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Mechanical+RGB+Keyboard"
    },
    {
        "name": "USB-C Multiport Hub",
        "description": "7-in-1 USB-C hub: HDMI, USB-A, Ethernet, SD/TF, and PD charging passthrough.",
        "price_cents": 3999,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=USB-C+Multiport+Hub"
    },
    {
        "name": "Noise-Cancelling Headphones",
        "description": "Over-ear headphones with active noise-cancellation and up to 30h battery life.",
        "price_cents": 12999,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Noise-Cancelling+Headphones"
    },
    {
        "name": "Portable Power Bank 10000mAh",
        "description": "Slim power bank with dual USB outputs and fast-charge support.",
        "price_cents": 1999,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Portable+Power+Bank"
    },
    {
        "name": "Smart LED Desk Lamp",
        "description": "Adjustable brightness and color-temperature lamp with touch controls.",
        "price_cents": 3199,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Smart+LED+Desk+Lamp"
    },
    {
        "name": "Fitness Tracker Watch",
        "description": "Waterproof fitness tracker with heart-rate monitor and sleep analysis.",
        "price_cents": 4599,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Fitness+Tracker+Watch"
    },
    {
        "name": "Adjustable Laptop Stand",
        "description": "Aluminum laptop stand with adjustable height and cooling vents.",
        "price_cents": 2899,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Adjustable+Laptop+Stand"
    },
    {
        "name": "4K UHD Monitor 27\"",
        "description": "27-inch 4K monitor with HDR10 support and ultra-thin bezels.",
        "price_cents": 29999,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=4K+UHD+Monitor"
    },
    {
        "name": "Gaming Chair Pro",
        "description": "Ergonomic gaming chair with lumbar support and adjustable armrests.",
        "price_cents": 15999,
        "image_url": "https://dummyimage.com/400x300/cccccc/000000&text=Gaming+Chair+Pro"
    }
]

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Clear existing products to force reseed
        print("Clearing existing products...")
        Product.query.delete()
        db.session.commit()

        # Insert sample products
        for data in products_data:
            prod = Product(
                name=data['name'],
                description=data['description'],
                price_cents=data['price_cents'],
                image_url=data['image_url']
            )
            db.session.add(prod)
        db.session.commit()
        print(f"Seeded {len(products_data)} products into the database.")
