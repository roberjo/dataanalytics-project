"""
Generate synthetic e-commerce transaction data for testing the analytics pipeline.
"""
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
import click
from faker import Faker

fake = Faker()


class TransactionGenerator:
    """Generate realistic e-commerce transaction data."""
    
    STATUSES = ['completed', 'completed', 'completed', 'completed', 'completed',
                'completed', 'completed', 'returned', 'refunded']
    
    def __init__(self, num_customers=1000, num_products=500):
        self.num_customers = num_customers
        self.num_products = num_products
        self.customer_ids = [f"cust_{i:06d}" for i in range(1, num_customers + 1)]
        self.product_ids = [f"prod_{i:06d}" for i in range(1, num_products + 1)]
    
    def generate_transaction(self, txn_id, base_date):
        """Generate a single transaction record."""
        customer_id = random.choice(self.customer_ids)
        product_id = random.choice(self.product_ids)
        quantity = random.randint(1, 5)
        
        # Price distribution: most items $10-100, some expensive items
        if random.random() < 0.9:
            price = round(random.uniform(9.99, 99.99), 2)
        else:
            price = round(random.uniform(100, 999.99), 2)
        
        total_amount = round(price * quantity, 2)
        
        # Transaction date within the specified date range
        days_offset = random.randint(0, 30)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        
        transaction_date = base_date + timedelta(
            days=days_offset,
            hours=hours_offset,
            minutes=minutes_offset
        )
        
        status = random.choice(self.STATUSES)
        
        return {
            'transaction_id': f"txn_{txn_id:09d}",
            'customer_id': customer_id,
            'product_id': product_id,
            'quantity': quantity,
            'price': price,
            'total_amount': total_amount,
            'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': status
        }
    
    def generate_transactions(self, num_rows, base_date):
        """Generate multiple transaction records."""
        transactions = []
        for i in range(1, num_rows + 1):
            transactions.append(self.generate_transaction(i, base_date))
            
            if i % 10000 == 0:
                print(f"Generated {i:,} transactions...")
        
        return transactions
    
    def save_to_csv(self, transactions, output_path):
        """Save transactions to CSV file."""
        fieldnames = [
            'transaction_id', 'customer_id', 'product_id', 'quantity',
            'price', 'total_amount', 'transaction_date', 'status'
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(transactions)
        
        print(f"Saved {len(transactions):,} transactions to {output_path}")


@click.command()
@click.option('--rows', default=100000, help='Number of transaction rows to generate')
@click.option('--customers', default=1000, help='Number of unique customers')
@click.option('--products', default=500, help='Number of unique products')
@click.option('--output', default='data/transactions.csv', help='Output file path')
@click.option('--date', default=None, help='Base date (YYYY-MM-DD), defaults to 30 days ago')
def main(rows, customers, products, output, date):
    """Generate synthetic e-commerce transaction data."""
    
    # Parse base date
    if date:
        base_date = datetime.strptime(date, '%Y-%m-%d')
    else:
        base_date = datetime.now() - timedelta(days=30)
    
    print(f"Generating {rows:,} transactions...")
    print(f"Customers: {customers:,}")
    print(f"Products: {products:,}")
    print(f"Base date: {base_date.strftime('%Y-%m-%d')}")
    print()
    
    generator = TransactionGenerator(num_customers=customers, num_products=products)
    transactions = generator.generate_transactions(rows, base_date)
    
    output_path = Path(output)
    generator.save_to_csv(transactions, output_path)
    
    # Print statistics
    total_revenue = sum(t['total_amount'] for t in transactions)
    completed_revenue = sum(t['total_amount'] for t in transactions if t['status'] == 'completed')
    
    print()
    print("Statistics:")
    print(f"  Total transactions: {len(transactions):,}")
    print(f"  Total revenue: ${total_revenue:,.2f}")
    print(f"  Completed revenue: ${completed_revenue:,.2f}")
    print(f"  Average order value: ${total_revenue/len(transactions):.2f}")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    main()
