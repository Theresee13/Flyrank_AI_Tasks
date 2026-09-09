"""Create a deterministic, disposable 200-order dataset."""

import random
from datetime import date, timedelta

from database import connection, initialize_database


def seed_orders() -> int:
    initialize_database()
    randomizer = random.Random(20260908)
    customers = ["Amina", "Mina", "Noor", "Omar", "Salma", "Youssef"]
    products = ["Notebook", "Keyboard", "Monitor", "Mouse", "Desk lamp", "Webcam"]
    today = date.today()
    rows = []
    for _ in range(200):
        rows.append(
            (
                randomizer.choice(customers),
                randomizer.choice(products),
                round(randomizer.uniform(5, 200), 2),
                (today - timedelta(days=randomizer.randrange(30))).isoformat(),
            )
        )
    with connection() as db:
        db.execute("DELETE FROM orders")
        db.executemany(
            "INSERT INTO orders (customer, product, amount, created_at) VALUES (?, ?, ?, ?)", rows
        )
        return db.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


if __name__ == "__main__":
    print(f"seeded_orders={seed_orders()}")
