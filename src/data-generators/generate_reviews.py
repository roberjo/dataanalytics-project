"""
Generate synthetic product review data for testing the analytics pipeline.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import click
from faker import Faker

fake = Faker()


class ReviewGenerator:
    """Generate realistic product review data."""

    # Review templates by rating
    POSITIVE_REVIEWS = [
        "Excellent product! Highly recommend.",
        "Great quality and fast shipping.",
        "Love it! Exactly as described.",
        "Perfect! Will buy again.",
        "Amazing product, exceeded expectations.",
        "Very satisfied with this purchase.",
        "Best purchase I've made in a while.",
        "Outstanding quality and value.",
    ]

    NEUTRAL_REVIEWS = [
        "It's okay, does the job.",
        "Average product, nothing special.",
        "Decent for the price.",
        "Works as expected.",
        "Not bad, not great.",
        "Acceptable quality.",
    ]

    NEGATIVE_REVIEWS = [
        "Disappointed with the quality.",
        "Not as described, returning it.",
        "Poor quality, broke after a week.",
        "Waste of money.",
        "Would not recommend.",
        "Very disappointed.",
        "Not worth the price.",
    ]

    def __init__(self, num_customers=1000, num_products=500):
        self.num_customers = num_customers
        self.num_products = num_products
        self.customer_ids = [f"cust_{i:06d}" for i in range(1, num_customers + 1)]
        self.product_ids = [f"prod_{i:06d}" for i in range(1, num_products + 1)]

    def generate_review(self, review_id, base_date):
        """Generate a single review record."""
        customer_id = random.choice(self.customer_ids)
        product_id = random.choice(self.product_ids)

        # Rating distribution: skewed towards positive (realistic)
        rating_weights = [0.05, 0.05, 0.10, 0.30, 0.50]  # 1-5 stars
        rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights)[0]

        # Generate review text based on rating
        if rating >= 4:
            review_text = random.choice(self.POSITIVE_REVIEWS)
        elif rating == 3:
            review_text = random.choice(self.NEUTRAL_REVIEWS)
        else:
            review_text = random.choice(self.NEGATIVE_REVIEWS)

        # Add some variation
        if random.random() < 0.3:
            review_text += " " + fake.sentence()

        # Review date within the specified date range
        days_offset = random.randint(0, 30)
        hours_offset = random.randint(0, 23)

        review_date = base_date + timedelta(days=days_offset, hours=hours_offset)

        # Verified purchase (80% of reviews)
        verified_purchase = random.random() < 0.8

        # Helpful votes
        helpful_votes = random.randint(0, 50) if rating >= 4 else random.randint(0, 10)

        return {
            "review_id": f"rev_{review_id:09d}",
            "product_id": product_id,
            "customer_id": customer_id,
            "rating": rating,
            "review_text": review_text,
            "review_date": review_date.strftime("%Y-%m-%d"),
            "verified_purchase": verified_purchase,
            "helpful_votes": helpful_votes,
        }

    def generate_reviews(self, num_rows, base_date):
        """Generate multiple review records."""
        reviews = []
        for i in range(1, num_rows + 1):
            reviews.append(self.generate_review(i, base_date))

            if i % 1000 == 0:
                print(f"Generated {i:,} reviews...")

        return reviews

    def save_to_csv(self, reviews, output_path):
        """Save reviews to CSV file."""
        fieldnames = [
            "review_id",
            "product_id",
            "customer_id",
            "rating",
            "review_text",
            "review_date",
            "verified_purchase",
            "helpful_votes",
        ]

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(reviews)

        print(f"Saved {len(reviews):,} reviews to {output_path}")


@click.command()
@click.option("--rows", default=2000, help="Number of reviews to generate")
@click.option("--customers", default=1000, help="Number of unique customers")
@click.option("--products", default=500, help="Number of unique products")
@click.option("--output", default="data/reviews.csv", help="Output file path")
@click.option(
    "--date", default=None, help="Base date (YYYY-MM-DD), defaults to 30 days ago"
)
def main(rows, customers, products, output, date):
    """Generate synthetic product review data."""

    # Parse base date
    if date:
        base_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        base_date = datetime.now() - timedelta(days=30)

    print(f"Generating {rows:,} reviews...")
    print(f"Customers: {customers:,}")
    print(f"Products: {products:,}")
    print(f"Base date: {base_date.strftime('%Y-%m-%d')}")
    print()

    generator = ReviewGenerator(num_customers=customers, num_products=products)
    reviews = generator.generate_reviews(rows, base_date)

    output_path = Path(output)
    generator.save_to_csv(reviews, output_path)

    # Print statistics
    rating_dist = {}
    for review in reviews:
        rating_dist[review["rating"]] = rating_dist.get(review["rating"], 0) + 1

    avg_rating = sum(r["rating"] for r in reviews) / len(reviews)
    verified = sum(1 for r in reviews if r["verified_purchase"])

    print()
    print("Statistics:")
    print(f"  Total reviews: {len(reviews):,}")
    print(f"  Average rating: {avg_rating:.2f}")
    print(f"  Verified purchases: {verified:,} ({verified / len(reviews) * 100:.1f}%)")
    print("  Rating distribution:")
    for rating in sorted(rating_dist.keys()):
        count = rating_dist[rating]
        print(f"    {rating} stars: {count:,} ({count / len(reviews) * 100:.1f}%)")
    print(f"  File size: {output_path.stat().st_size / 1024:.2f} KB")


if __name__ == "__main__":
    main()
