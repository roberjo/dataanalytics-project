"""
Generate synthetic clickstream data for testing the analytics pipeline.
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
import click
from faker import Faker

fake = Faker()


class ClickstreamGenerator:
    """Generate realistic website clickstream data."""
    
    EVENT_TYPES = [
        'page_view', 'page_view', 'page_view', 'page_view',  # Most common
        'product_view', 'product_view', 'product_view',
        'add_to_cart', 'add_to_cart',
        'remove_from_cart',
        'checkout_start',
        'purchase'
    ]
    
    PAGES = [
        '/', '/products', '/cart', '/checkout', '/account',
        '/about', '/contact', '/help', '/search'
    ]
    
    DEVICES = ['desktop', 'mobile', 'tablet']
    DEVICE_WEIGHTS = [0.5, 0.4, 0.1]  # Desktop 50%, Mobile 40%, Tablet 10%
    
    BROWSERS = ['Chrome', 'Safari', 'Firefox', 'Edge']
    
    def __init__(self, num_customers=1000, num_products=500):
        self.num_customers = num_customers
        self.num_products = num_products
        self.customer_ids = [f"cust_{i:06d}" for i in range(1, num_customers + 1)]
        self.product_ids = [f"prod_{i:06d}" for i in range(1, num_products + 1)]
    
    def generate_session_events(self, session_id, customer_id, base_timestamp):
        """Generate a realistic session with multiple events."""
        events = []
        current_time = base_timestamp
        device = random.choices(self.DEVICES, weights=self.DEVICE_WEIGHTS)[0]
        browser = random.choice(self.BROWSERS)
        
        # Session duration: 1-30 minutes
        session_duration = random.randint(60, 1800)
        num_events = random.randint(3, 20)
        
        # Start with a page view
        events.append(self._create_event(
            session_id, customer_id, 'page_view', '/', 
            current_time, device, browser
        ))
        
        # Generate subsequent events
        for _ in range(num_events - 1):
            # Increment time by 5-120 seconds
            current_time += timedelta(seconds=random.randint(5, 120))
            
            event_type = random.choice(self.EVENT_TYPES)
            
            if event_type == 'page_view':
                page = random.choice(self.PAGES)
            elif event_type in ['product_view', 'add_to_cart', 'remove_from_cart']:
                product_id = random.choice(self.product_ids)
                page = f"/product/{product_id}"
            elif event_type == 'checkout_start':
                page = '/checkout'
            elif event_type == 'purchase':
                page = '/confirmation'
            else:
                page = random.choice(self.PAGES)
            
            events.append(self._create_event(
                session_id, customer_id, event_type, page,
                current_time, device, browser
            ))
        
        return events
    
    def _create_event(self, session_id, customer_id, event_type, page, 
                     timestamp, device, browser):
        """Create a single clickstream event."""
        return {
            'session_id': session_id,
            'customer_id': customer_id,
            'event_type': event_type,
            'page': page,
            'timestamp': timestamp.isoformat(),
            'device': device,
            'browser': browser,
            'ip_address': fake.ipv4(),
            'user_agent': fake.user_agent()
        }
    
    def generate_clickstream(self, num_events, base_date):
        """Generate clickstream events."""
        events = []
        session_count = 0
        
        while len(events) < num_events:
            session_count += 1
            session_id = f"sess_{session_count:09d}"
            customer_id = random.choice(self.customer_ids)
            
            # Random timestamp within the date range
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            base_timestamp = base_date + timedelta(
                days=days_offset,
                hours=hours_offset,
                minutes=minutes_offset
            )
            
            session_events = self.generate_session_events(
                session_id, customer_id, base_timestamp
            )
            events.extend(session_events)
            
            if len(events) % 10000 == 0:
                print(f"Generated {len(events):,} events...")
        
        # Trim to exact number requested
        events = events[:num_events]
        
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        
        return events
    
    def save_to_json(self, events, output_path):
        """Save events to JSON file (one JSON object per line)."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')
        
        print(f"Saved {len(events):,} events to {output_path}")


@click.command()
@click.option('--rows', default=50000, help='Number of clickstream events to generate')
@click.option('--customers', default=1000, help='Number of unique customers')
@click.option('--products', default=500, help='Number of unique products')
@click.option('--output', default='data/clickstream.json', help='Output file path')
@click.option('--date', default=None, help='Base date (YYYY-MM-DD), defaults to 30 days ago')
def main(rows, customers, products, output, date):
    """Generate synthetic clickstream data."""
    
    # Parse base date
    if date:
        base_date = datetime.strptime(date, '%Y-%m-%d')
    else:
        base_date = datetime.now() - timedelta(days=30)
    
    print(f"Generating {rows:,} clickstream events...")
    print(f"Customers: {customers:,}")
    print(f"Products: {products:,}")
    print(f"Base date: {base_date.strftime('%Y-%m-%d')}")
    print()
    
    generator = ClickstreamGenerator(num_customers=customers, num_products=products)
    events = generator.generate_clickstream(rows, base_date)
    
    output_path = Path(output)
    generator.save_to_json(events, output_path)
    
    # Print statistics
    event_types = {}
    devices = {}
    for event in events:
        event_types[event['event_type']] = event_types.get(event['event_type'], 0) + 1
        devices[event['device']] = devices.get(event['device'], 0) + 1
    
    print()
    print("Statistics:")
    print(f"  Total events: {len(events):,}")
    print(f"  Event types:")
    for et, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {et}: {count:,} ({count/len(events)*100:.1f}%)")
    print(f"  Devices:")
    for dev, count in sorted(devices.items(), key=lambda x: x[1], reverse=True):
        print(f"    {dev}: {count:,} ({count/len(events)*100:.1f}%)")
    print(f"  File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


if __name__ == '__main__':
    main()
