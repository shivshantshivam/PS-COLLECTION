from dotenv import load_dotenv
import os
load_dotenv()

import mysql.connector

db = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DATABASE", "ai_ecommerce")
)

cursor = db.cursor(dictionary=True)

categories = {
    "Electronics": "electronics",
    "Mens": "mens",
    "Womens": "womens",
    "Kids": "kids",
    "Makeup": "makeup",
    "Grocery": "grocery"
}

for category, prefix in categories.items():

    cursor.execute("""
        SELECT id
        FROM products
        WHERE category = %s
        AND (image IS NULL OR image = '')
        ORDER BY id
        LIMIT 10
    """, (category,))

    products = cursor.fetchall()

    for i, product in enumerate(products, start=1):

        image_name = f"{prefix}{i}.jpg"

        cursor.execute("""
            UPDATE products
            SET image = %s
            WHERE id = %s
        """, (image_name, product["id"]))

        print(category, product["id"], "->", image_name)

db.commit()

cursor.close()
db.close()

print("Images assigned successfully!")