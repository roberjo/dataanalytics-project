"""
Generate synthetic product catalog data for testing the analytics pipeline.
"""

import json
import random
from pathlib import Path
import click
from faker import Faker

fake = Faker()


class ProductGenerator:
    """Generate realistic product catalog data."""

    CATEGORIES = [
        "Electronics",
        "Clothing",
        "Home & Garden",
        "Sports & Outdoors",
        "Books",
        "Toys & Games",
        "Health & Beauty",
        "Automotive",
        "Office Supplies",
        "Pet Supplies",
    ]

    BRANDS = [
        "TechBrand",
        "StyleCo",
        "HomeEssentials",
        "ActiveLife",
        "ReadMore",
        "PlayTime",
        "BeautyPlus",
        "AutoPro",
        "OfficePro",
        "PetCare",
        "GenericBrand",
        "PremiumChoice",
    ]

    PRODUCT_NAMES = {
        "Electronics": [
            "Wireless Mouse",
            "Keyboard",
            "Monitor",
            "Headphones",
            "Webcam",
            "USB Cable",
            "Phone Case",
            "Charger",
        ],
        "Clothing": [
            "T-Shirt",
            "Jeans",
            "Dress",
            "Jacket",
            "Sneakers",
            "Hat",
            "Socks",
            "Sweater",
        ],
        "Home & Garden": [
            "Lamp",
            "Pillow",
            "Blanket",
            "Plant Pot",
            "Candle",
            "Picture Frame",
            "Vase",
            "Rug",
        ],
        "Sports & Outdoors": [
            "Yoga Mat",
            "Dumbbells",
            "Water Bottle",
            "Backpack",
            "Tent",
            "Sleeping Bag",
            "Bike Helmet",
        ],
        "Books": [
            "Fiction Novel",
            "Cookbook",
            "Self-Help Book",
            "Biography",
            "Textbook",
            "Comic Book",
            "Magazine",
        ],
        "Toys & Games": [
            "Board Game",
            "Puzzle",
            "Action Figure",
            "Doll",
            "Building Blocks",
            "Card Game",
            "Stuffed Animal",
        ],
        "Health & Beauty": [
            "Shampoo",
            "Moisturizer",
            "Vitamins",
            "Toothpaste",
            "Makeup",
            "Perfume",
            "Soap",
        ],
        "Automotive": [
            "Car Wax",
            "Oil Filter",
            "Air Freshener",
            "Phone Mount",
            "Jumper Cables",
            "Tire Gauge",
        ],
        "Office Supplies": [
            "Notebook",
            "Pen Set",
            "Stapler",
            "Desk Organizer",
            "Paper",
            "Folders",
            "Tape",
        ],
        "Pet Supplies": [
            "Dog Food",
            "Cat Toy",
            "Pet Bed",
            "Leash",
            "Food Bowl",
            "Treats",
            "Collar",
        ],
    }

    def generate_product(self, product_id):
        """Generate a single product record."""
        category = random.choice(self.CATEGORIES)
        product_type = random.choice(self.PRODUCT_NAMES[category])
        brand = random.choice(self.BRANDS)

        # Generate product name
        name = f"{brand} {product_type}"
        if random.random() < 0.3:
            name += (
                f" {random.choice(['Pro', 'Plus', 'Premium', 'Deluxe', 'Standard'])}"
            )

        # Price based on category
        if category == "Electronics":
            price = round(random.uniform(19.99, 299.99), 2)
        elif category == "Clothing":
            price = round(random.uniform(9.99, 99.99), 2)
        elif category == "Books":
            price = round(random.uniform(5.99, 39.99), 2)
        else:
            price = round(random.uniform(4.99, 149.99), 2)

        # Stock levels
        stock = random.randint(0, 500)

        # Additional attributes
        weight_kg = round(random.uniform(0.1, 10.0), 2)
        rating = round(random.uniform(3.0, 5.0), 1)
        review_count = random.randint(0, 1000)

        return {
            "product_id": product_id,
            "name": name,
            "category": category,
            "brand": brand,
            "price": price,
            "stock": stock,
            "weight_kg": weight_kg,
            "rating": rating,
            "review_count": review_count,
            "is_active": stock > 0,
        }

    def generate_products(self, num_products):
        """Generate multiple product records."""
        products = []
        for i in range(1, num_products + 1):
            product_id = f"prod_{i:06d}"
            products.append(self.generate_product(product_id))

            if i % 100 == 0:
                print(f"Generated {i:,} products...")

        return products

    def save_to_json(self, products, output_path):
        """Save products to JSON file (one JSON object per line)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for product in products:
                f.write(json.dumps(product) + "\n")

        print(f"Saved {len(products):,} products to {output_path}")


@click.command()
@click.option("--rows", default=500, help="Number of products to generate")
@click.option("--output", default="data/products.json", help="Output file path")
def main(rows, output):
    """Generate synthetic product catalog data."""

    print(f"Generating {rows:,} products...")
    print()

    generator = ProductGenerator()
    products = generator.generate_products(rows)

    output_path = Path(output)
    generator.save_to_json(products, output_path)

    # Print statistics
    avg_price = sum(p["price"] for p in products) / len(products)
    total_stock = sum(p["stock"] for p in products)
    categories = {}
    for p in products:
        categories[p["category"]] = categories.get(p["category"], 0) + 1

    print()
    print("Statistics:")
    print(f"  Total products: {len(products):,}")
    print(f"  Average price: ${avg_price:.2f}")
    print(f"  Total stock: {total_stock:,}")
    print(f"  Categories: {len(categories)}")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"    {cat}: {count}")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()
