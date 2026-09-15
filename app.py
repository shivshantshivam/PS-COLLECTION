from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai
from dotenv import load_dotenv
import os
import random
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing")


def get_db():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "ai_ecommerce"),
        port=int(os.getenv("MYSQL_PORT", "3306"))
    )


db = get_db()


def is_admin():

    if "user_id" not in session:
        return False

    admin_db = get_db()
    cursor = admin_db.cursor(dictionary=True)

    cursor.execute(
        "SELECT is_admin FROM users WHERE id = %s",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    cursor.close()
    admin_db.close()

    return bool(user and user["is_admin"])


# Home
@app.route("/")
def home():

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY id DESC
        LIMIT 30
    """)

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        "home.html",
        products=products
    )


@app.route("/KIDS")
def kids():
    return render_template("home.html")


@app.route("/MENS")
def mens():
    return render_template("home.html")


@app.route("/WOMENS")
def womens():
    return render_template("home.html")


@app.route("/ELECTRONICS")
def electronics():
    return render_template("home.html")


@app.route("/GROCERY")
def grocery():
    return render_template("home.html")


# Wishlist
@app.route("/Wishlist")
def wishlist():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            wishlist.id,
            wishlist.product_id,
            products.name,
            products.price,
            products.description,
            products.image
        FROM wishlist
        JOIN products
        ON wishlist.product_id = products.id
        WHERE wishlist.user_id = %s
        ORDER BY wishlist.created_at DESC
    """, (session["user_id"],))

    wishlist_items = cursor.fetchall()

    cursor.close()

    return render_template(
        "wishlist.html",
        wishlist_items=wishlist_items
    )


@app.route("/add-to-wishlist/<int:product_id>")
def add_to_wishlist(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT id
        FROM wishlist
        WHERE user_id = %s AND product_id = %s
    """, (session["user_id"], product_id))

    item = cursor.fetchone()

    if not item:

        cursor.execute("""
            INSERT INTO wishlist (user_id, product_id)
            VALUES (%s, %s)
        """, (session["user_id"], product_id))

        db.commit()

    cursor.close()

    return redirect(request.referrer or url_for("products"))


@app.route("/remove-from-wishlist/<int:wishlist_id>")
def remove_from_wishlist(wishlist_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM wishlist
        WHERE id = %s AND user_id = %s
    """, (wishlist_id, session["user_id"]))

    db.commit()

    cursor.close()

    return redirect(url_for("wishlist"))


# Account
@app.route("/Account")
def account():
    return render_template("account.html")


@app.route("/account/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    error = None
    success = None

    if request.method == "POST":

        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT password FROM users WHERE id = %s",
            (session["user_id"],)
        )

        user = cursor.fetchone()

        if not user:
            cursor.close()
            return redirect(url_for("login"))

        if not check_password_hash(user["password"], current_password):

            error = "Current password is incorrect"

        elif new_password != confirm_password:

            error = "New passwords do not match"

        else:

            new_password_hash = generate_password_hash(new_password)

            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_password_hash, session["user_id"])
            )

            db.commit()

            success = "Password changed successfully"

        cursor.close()

    return render_template(
        "change_password.html",
        error=error,
        success=success
    )


@app.route("/account/profile", methods=["GET", "POST"])
def account_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        date_of_birth = request.form.get("date_of_birth")
        gender = request.form.get("gender")

        cursor.execute("""
            UPDATE users
            SET name = %s,
                email = %s,
                phone = %s,
                date_of_birth = %s,
                gender = %s
            WHERE id = %s
        """, (
            name,
            email,
            phone,
            date_of_birth,
            gender,
            session["user_id"]
        ))

        db.commit()

        session["user_name"] = name

        cursor.close()

        return redirect(url_for("account_profile"))

    cursor.execute("""
        SELECT name, email, phone, date_of_birth, gender, created_at
        FROM users
        WHERE id = %s
    """, (session["user_id"],))

    user = cursor.fetchone()

    cursor.close()

    return render_template("profile.html", user=user)


@app.route("/account/address", methods=["GET", "POST"])
def account_address():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form.get("name")
        phone = request.form.get("phone")
        address = request.form.get("address")
        city = request.form.get("city")
        state = request.form.get("state")
        pincode = request.form.get("pincode")

        cursor.execute("""
            INSERT INTO addresses
            (user_id, name, phone, address, city, state, pincode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            session["user_id"],
            name,
            phone,
            address,
            city,
            state,
            pincode
        ))

        db.commit()

    cursor.execute("""
        SELECT *
        FROM addresses
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    addresses = cursor.fetchall()

    cursor.close()

    return render_template(
        "address.html",
        addresses=addresses
    )


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        cursor.close()

        if existing_user:
            return "Email already exists"

        otp = str(random.randint(100000, 999999))

        session["register_name"] = name
        session["register_email"] = email
        session["register_password"] = generate_password_hash(password)
        session["register_otp"] = otp

        try:

            message = EmailMessage()

            message["Subject"] = "E-Commerce Email Verification"
            message["From"] = os.getenv("MAIL_EMAIL")
            message["To"] = email

            message.set_content(
                f"Your OTP for email verification is: {otp}\n\n"
                "Please enter this OTP on the website to verify your email."
            )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

                server.login(
                    os.getenv("MAIL_EMAIL"),
                    os.getenv("MAIL_PASSWORD")
                )

                server.send_message(message)

        except Exception as e:

            print("Email error:", e)

            session.pop("register_name", None)
            session.pop("register_email", None)
            session.pop("register_password", None)
            session.pop("register_otp", None)

            return "Unable to send OTP email"

        return redirect(url_for("verify_otp"))

    return render_template("register.html")


# Verify OTP
@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if "register_otp" not in session:
        return redirect(url_for("register"))

    error = None

    if request.method == "POST":

        otp = request.form.get("otp")

        if otp == session["register_otp"]:

            cursor = db.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password, email_verified)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    session["register_name"],
                    session["register_email"],
                    session["register_password"],
                    True
                )
            )

            db.commit()

            cursor.close()

            session.pop("register_name", None)
            session.pop("register_email", None)
            session.pop("register_password", None)
            session.pop("register_otp", None)

            return redirect(url_for("login"))

        error = "Invalid OTP"

    return render_template(
        "verify_otp.html",
        error=error
    )


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):

            if not user["email_verified"]:

                cursor.close()

                error = "Please verify your email first"

                return render_template(
                    "login.html",
                    error=error
                )

            cursor.execute(
                """
                UPDATE users
                SET last_login = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (user["id"],)
            )

            db.commit()

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["is_admin"] = bool(user["is_admin"])

            cursor.close()

            return redirect(url_for("home"))

        cursor.close()

        error = "Invalid email or password"

    return render_template(
        "login.html",
        error=error
    )


# Forgot Password
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    error = None

    if request.method == "POST":

        email = request.form.get("email")

        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()

        if not user:

            error = "Email not found"

            return render_template(
                "forgot_password.html",
                error=error
            )

        otp = str(random.randint(100000, 999999))

        session["reset_email"] = email
        session["reset_otp"] = otp

        try:

            message = EmailMessage()

            message["Subject"] = "Password Reset OTP"
            message["From"] = os.getenv("MAIL_EMAIL")
            message["To"] = email

            message.set_content(
                f"Your password reset OTP is: {otp}\n\n"
                "Please enter this OTP on the website to reset your password."
            )

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:

                server.login(
                    os.getenv("MAIL_EMAIL"),
                    os.getenv("MAIL_PASSWORD")
                )

                server.send_message(message)

        except Exception as e:

            print("Email error:", e)

            session.pop("reset_email", None)
            session.pop("reset_otp", None)

            return "Unable to send OTP email"

        return redirect(url_for("reset_password"))

    return render_template(
        "forgot_password.html",
        error=error
    )


# Reset password
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if "reset_otp" not in session:
        return redirect(url_for("forgot_password"))

    error = None

    if request.method == "POST":

        otp = request.form.get("otp")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if otp != session["reset_otp"]:

            error = "Invalid OTP"

        elif password != confirm_password:

            error = "Passwords do not match"

        else:

            hashed_password = generate_password_hash(password)

            cursor = db.cursor()

            cursor.execute(
                """
                UPDATE users
                SET password = %s
                WHERE email = %s
                """,
                (
                    hashed_password,
                    session["reset_email"]
                )
            )

            db.commit()

            cursor.close()

            session.pop("reset_email", None)
            session.pop("reset_otp", None)

            return redirect(url_for("login"))

    return render_template(
        "reset_password.html",
        error=error
    )


# Logout
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# Products
@app.route("/products")
def products():

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "").strip()

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT *
        FROM products
        WHERE 1=1
    """

    values = []

    if search:

        query += " AND LOWER(name) LIKE LOWER(%s)"

        values.append("%" + search + "%")

    if category:

        query += " AND LOWER(TRIM(category)) = LOWER(TRIM(%s))"

        values.append(category)

    if sort == "price_low":

        query += " ORDER BY price ASC"

    elif sort == "price_high":

        query += " ORDER BY price DESC"

    elif sort == "newest":

        query += " ORDER BY id DESC"

    else:

        query += " ORDER BY id DESC"

    cursor.execute(query, values)

    products = cursor.fetchall()

    cursor.execute("""
        SELECT DISTINCT TRIM(category) AS category
        FROM products
        WHERE category IS NOT NULL
        AND TRIM(category) != ''
        ORDER BY category
    """)

    categories = cursor.fetchall()

    cursor.close()

    return render_template(
        "product.html",
        products=products,
        categories=categories,
        search=search,
        selected_category=category,
        sort=sort
    )


@app.route("/product/<int:product_id>")
def product_detail(product_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE id = %s
        """,
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()

        return "Product not found", 404

    cursor.execute(
        """
        SELECT *
        FROM products
        WHERE category = %s
        AND id != %s
        LIMIT 4
        """,
        (
            product["category"],
            product_id
        )
    )

    similar_products = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            reviews.rating,
            reviews.review,
            reviews.created_at,
            users.name
        FROM reviews
        JOIN users
        ON reviews.user_id = users.id
        WHERE reviews.product_id = %s
        ORDER BY reviews.created_at DESC
        """,
        (product_id,)
    )

    reviews = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            AVG(rating) AS average_rating,
            COUNT(*) AS review_count
        FROM reviews
        WHERE product_id = %s
        """,
        (product_id,)
    )

    rating_data = cursor.fetchone()

    cursor.close()

    return render_template(
        "product_detail.html",
        product=product,
        similar_products=similar_products,
        reviews=reviews,
        average_rating=rating_data["average_rating"],
        review_count=rating_data["review_count"]
    )


@app.route("/add-review/<int:product_id>", methods=["POST"])
def add_review(product_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    rating = request.form.get("rating")
    review = request.form.get("review", "").strip()

    if not rating:
        return redirect(
            url_for(
                "product_detail",
                product_id=product_id
            )
        )

    try:

        rating = int(rating)

    except ValueError:

        return redirect(
            url_for(
                "product_detail",
                product_id=product_id
            )
        )

    if rating < 1 or rating > 5:

        return redirect(
            url_for(
                "product_detail",
                product_id=product_id
            )
        )

    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO reviews
        (product_id, user_id, rating, review)
        VALUES (%s, %s, %s, %s)
        """,
        (
            product_id,
            session["user_id"],
            rating,
            review
        )
    )

    db.commit()

    cursor.close()

    return redirect(
        url_for(
            "product_detail",
            product_id=product_id
        )
    )


# Recommendations
@app.route("/recommendations/<int:product_id>")
def recommendations(product_id):

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT category FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    if not product:

        cursor.close()

        return "Product not found"

    cursor.execute("""
        SELECT *
        FROM products
        WHERE category = %s
        AND id != %s
    """, (
        product["category"],
        product_id
    ))

    recommended = cursor.fetchall()

    cursor.close()

    return render_template(
        "recommendations.html",
        recommended=recommended
    )


# AI Chatbot
@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data:
        return "Please enter a message."

    message = data.get("message", "").strip()

    if not message:
        return "Please enter a message."

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT name, price, description, category
        FROM products
        ORDER BY category, name
    """)

    products = cursor.fetchall()

    cursor.close()

    product_info = ""

    for product in products:

        product_info += f"""
Product: {product['name']}
Price: ₹{product['price']}
Category: {product['category']}
Description: {product['description']}
"""

    prompt = f"""
You are the AI Shopping Assistant for a premium e-commerce website.

Your goal is to help customers find suitable products quickly and naturally.

AVAILABLE PRODUCTS:
{product_info}

CUSTOMER MESSAGE:
{message}

IMPORTANT RULES:

1. Only recommend products that exist in the available products list.

2. Never invent:
- product names
- prices
- categories
- features
- discounts
- stock availability

3. Always use the exact product name and actual price when recommending a product.

4. If the customer asks for recommendations:
- Recommend only 2 or 3 products.
- Explain briefly why each product is suitable.

5. If the customer asks about one specific product:
- Focus only on that product.
- Mention its actual price and relevant description.

6. If the customer asks about products in a category:
- Recommend products from that category only.
- Keep the response short.

7. If the customer asks for a product that does not exist:
- Clearly say that the product is not available.
- Suggest similar products only if suitable products exist.

8. If the customer asks generally what products are available:
- Group products by category.
- Do not list every product unless necessary.

9. If the customer asks about price:
- Give the actual price from the product data.

10. If the customer asks something unrelated to shopping:
- Politely say that you are mainly here to help with shopping and products.

11. Use simple, natural and friendly English.

12. Keep responses short and useful.

13. Do not repeat the customer's question.

14. Do not say:
- "according to the database"
- "based on the provided data"
- "I have access to"
- "the database shows"

15. Use small headings or bullet points when they make the answer easier to read.

16. Always use ₹ for Indian prices.

17. Never make up information just to satisfy the customer.

RESPONSE STYLE:

Be like a helpful premium shopping assistant.

Now answer the customer naturally.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# Cart
@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    product_id = request.form.get("product_id")
    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM cart
        WHERE product_id = %s
        AND user_id = %s
    """, (
        product_id,
        user_id
    ))

    item = cursor.fetchone()

    if item:

        cursor.execute("""
            UPDATE cart
            SET quantity = quantity + 1
            WHERE product_id = %s
            AND user_id = %s
        """, (
            product_id,
            user_id
        ))

    else:

        cursor.execute("""
            INSERT INTO cart
            (product_id, quantity, user_id)
            VALUES (%s, %s, %s)
        """, (
            product_id,
            1,
            user_id
        ))

    db.commit()

    cursor.close()

    return redirect(url_for("cart"))


@app.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.id,
            cart.product_id,
            cart.quantity,
            products.name,
            products.price,
            products.image
        FROM cart
        JOIN products
        ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, (user_id,))

    cart_items = cursor.fetchall()

    total = 0

    for item in cart_items:

        item["subtotal"] = float(item["price"]) * item["quantity"]

        total += item["subtotal"]

    cursor.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


@app.route("/update-cart/<int:cart_id>/<action>")
def update_cart(cart_id, action):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT quantity
        FROM cart
        WHERE id = %s
        AND user_id = %s
    """, (
        cart_id,
        user_id
    ))

    item = cursor.fetchone()

    if item:

        if action == "increase":

            cursor.execute("""
                UPDATE cart
                SET quantity = quantity + 1
                WHERE id = %s
                AND user_id = %s
            """, (
                cart_id,
                user_id
            ))

        elif action == "decrease":

            if item["quantity"] > 1:

                cursor.execute("""
                    UPDATE cart
                    SET quantity = quantity - 1
                    WHERE id = %s
                    AND user_id = %s
                """, (
                    cart_id,
                    user_id
                ))

            else:

                cursor.execute("""
                    DELETE FROM cart
                    WHERE id = %s
                    AND user_id = %s
                """, (
                    cart_id,
                    user_id
                ))

        db.commit()

    cursor.close()

    return redirect(url_for("cart"))


@app.route("/remove-from-cart/<int:cart_id>")
def remove_from_cart(cart_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = db.cursor()

    cursor.execute("""
        DELETE FROM cart
        WHERE id = %s
        AND user_id = %s
    """, (
        cart_id,
        user_id
    ))

    db.commit()

    cursor.close()

    return redirect(url_for("cart"))


# Checkout
@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            cart.product_id,
            cart.quantity,
            products.name,
            products.price
        FROM cart
        JOIN products
        ON cart.product_id = products.id
        WHERE cart.user_id = %s
    """, (user_id,))

    cart_items = cursor.fetchall()

    if not cart_items:

        cursor.close()

        return "Your cart is empty"

    total = 0

    for item in cart_items:

        total += float(item["price"]) * item["quantity"]

    if request.method == "POST":

        cursor.execute(
            """
            INSERT INTO orders
            (user_id, total_amount)
            VALUES (%s, %s)
            """,
            (
                user_id,
                total
            )
        )

        order_id = cursor.lastrowid

        for item in cart_items:

            cursor.execute("""
                INSERT INTO order_items
                (order_id, product_id, quantity, price)
                VALUES (%s, %s, %s, %s)
            """, (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            ))

        cursor.execute("""
            DELETE FROM cart
            WHERE user_id = %s
        """, (user_id,))

        db.commit()

        cursor.close()

        return redirect(url_for("orders"))

    cursor.close()

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )


# Orders
@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM orders
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "orders.html",
        orders=orders
    )


# Admin
@app.route("/admin")
def admin():

    if not is_admin():
        return redirect(url_for("login"))

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin.html",
        products=products
    )


# Admin Orders
@app.route("/admin/orders")
def admin_orders():

    if not is_admin():
        return "Access Denied"

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            orders.id,
            users.name,
            users.email,
            orders.total_amount,
            orders.status,
            orders.created_at
        FROM orders
        JOIN users
        ON orders.user_id = users.id
        ORDER BY orders.created_at DESC
    """)

    orders = cursor.fetchall()

    cursor.close()

    return render_template(
        "admin_orders.html",
        orders=orders
    )


# Admin Users
@app.route("/admin/users")
def admin_users():

    if not is_admin():
        return "Access Denied"

    admin_db = get_db()
    cursor = admin_db.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id,
            name,
            email,
            phone,
            created_at,
            last_login
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    admin_db.close()

    return render_template(
        "admin_users.html",
        users=users
    )


@app.route("/admin/update-order/<int:order_id>", methods=["POST"])
def update_order(order_id):

    if not is_admin():
        return "Access Denied"

    status = request.form.get("status")

    cursor = db.cursor()

    cursor.execute(
        "UPDATE orders SET status = %s WHERE id = %s",
        (status, order_id)
    )

    db.commit()

    cursor.close()

    return redirect(url_for("admin_orders"))


@app.route("/admin/delete-order/<int:order_id>", methods=["POST"])
def delete_order(order_id):

    if not is_admin():
        return "Access Denied"

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM order_items WHERE order_id = %s",
        (order_id,)
    )

    cursor.execute(
        "DELETE FROM orders WHERE id = %s",
        (order_id,)
    )

    db.commit()

    cursor.close()

    return redirect(url_for("admin_orders"))


@app.route("/admin/add-product", methods=["POST"])
def add_product():

    if not is_admin():
        return "Access Denied"

    name = request.form.get("name")
    price = request.form.get("price")
    category = request.form.get("category")
    description = request.form.get("description")
    image = request.form.get("image")

    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO products
        (name, price, description, category, image)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        name,
        price,
        description,
        category,
        image
    ))

    db.commit()

    cursor.close()

    return redirect(url_for("admin"))


@app.route("/admin/delete-product/<int:product_id>")
def delete_product(product_id):

    if not is_admin():
        return "Access Denied"

    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM order_items WHERE product_id = %s",
        (product_id,)
    )

    cursor.execute(
        "DELETE FROM cart WHERE product_id = %s",
        (product_id,)
    )

    cursor.execute(
        "DELETE FROM products WHERE id = %s",
        (product_id,)
    )

    db.commit()

    cursor.close()

    return redirect(url_for("admin"))


@app.route(
    "/admin/edit-product/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):

    if not is_admin():
        return "Access Denied"

    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form.get("name")
        price = request.form.get("price")
        category = request.form.get("category")
        description = request.form.get("description")
        image = request.form.get("image")

        cursor.execute("""
            UPDATE products
            SET name = %s,
                price = %s,
                category = %s,
                description = %s,
                image = %s
            WHERE id = %s
        """, (
            name,
            price,
            category,
            description,
            image,
            product_id
        ))

        db.commit()

        cursor.close()

        return redirect(url_for("admin"))

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()

    return render_template(
        "edit_product.html",
        product=product
    )


if __name__ == "__main__":

    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )