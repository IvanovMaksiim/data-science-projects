import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import timedelta

fake = Faker()
random.seed(42)
np.random.seed(42)

def generate_users(n=500):
    users = []
    for i in range(1, n+1):
        users.append({
            'user_id': i,
            'name': fake.name(),
            'city': fake.city(),
            'signup_date': fake.date_between(start_date='-1y', end_date='today')
        })
    return pd.DataFrame(users)

def generate_products(n=100):
    categories = ['Electronics', 'Books', 'Clothing', 'Home', 'Toys']
    products = []
    for i in range(1, n+1):
        products.append({
            'product_id': i,
            'product_name': fake.word().capitalize(),
            'category': random.choice(categories),
            'price': round(random.uniform(5, 500), 2)
        })
    return pd.DataFrame(products)


def generate_orders(users, max_orders_per_user=10):
    orders = []
    order_id = 1
    for _, user in users.iterrows():
        num_orders = np.random.poisson(2)
        for _ in range(min(num_orders, max_orders_per_user)):
            order_date = user.signup_date + timedelta(days=random.randint(1, 300))
            orders.append({
                'order_id': order_id,
                'user_id': user['user_id'],
                'order_date': order_date,
            })
            order_id += 1
    return pd.DataFrame(orders)

def generate_order_items(orders, products):
    items = []
    for _, order in orders.iterrows():
        product_sample = products.sample(random.randint(1, 5))
        for _, product in product_sample.iterrows():
            items.append({
                'order_id': order['order_id'],
                'product_id': product['product_id'],
                'quantity': random.randint(1, 3),
            })
    return pd.DataFrame(items)

def generate_events(users, products):
    event_types = ['view', 'cart', 'purchase']
    events = []
    for _, user in users.iterrows():
        for _ in range(random.randint(5, 20)):
            event = random.choices(event_types, weights=[0.6, 0.25, 0.15])[0]
            timestamp = user.signup_date + timedelta(days=random.randint(0, 364))
            events.append({
                'user_id': user['user_id'],
                'event_date': timestamp,
                'event': event,
                'product_id': random.choice(products['product_id'].tolist())
            })
    return pd.DataFrame(events)

users_df = generate_users()
products_df = generate_products()
orders_df = generate_orders(users_df)
order_items_df = generate_order_items(orders_df, products_df)
events_df = generate_events(users_df, products_df)

users_df.to_csv('users.csv', index=False)
products_df.to_csv('products.csv', index=False)
orders_df.to_csv('orders.csv', index=False)
order_items_df.to_csv('order_items.csv', index=False)
events_df.to_csv('events.csv', index=False)