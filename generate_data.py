import sys
import os
import random

# Add the current directory to the path so we can import the api package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from api.dependencies.database import SessionLocal, engine
from api.models import model_loader, customers, menu, orders, order_details, payment_info, promotions, ratings, recipes, resources, favorite_orders, rewards
from api.controllers.orders import generate_tracking_number
from api.dependencies.security import hash_password
from datetime import datetime, timedelta, date
from decimal import Decimal

def generate_data():
    # Ensure tables are created
    model_loader.index()

    db = SessionLocal()
    try:
        # 1. Resources
        print("Adding resources...")
        ingredient_data = [
            ("Bread", 500, 50), ("Ham", 200, 20), ("Turkey", 200, 20),
            ("Cheese", 300, 30), ("Lettuce", 150, 15), ("Tomato", 150, 15),
            ("Bacon", 100, 10), ("Mayo", 500, 50), ("Mustard", 500, 50),
            ("Onions", 100, 10), ("Pickles", 100, 10)
        ]
        for name, amt, thresh in ingredient_data:
            if not db.query(resources.Resource).filter(resources.Resource.item == name).first():
                db.add(resources.Resource(item=name, amount=amt, min_threshold=thresh))
        db.commit()

        # 2. Menu
        print("Adding menu items...")
        menu_data = [
            ("Classic Ham", "Ham and cheese", 7.99, 400, "Sandwich"),
            ("Turkey Club", "Turkey and bacon", 9.99, 550, "Sandwich"),
            ("Veggie Sub", "Fresh vegetables", 6.99, 300, "Sandwich"),
            ("BLT Special", "Bacon, lettuce, tomato", 8.50, 480, "Sandwich"),
            ("Spicy Italian", "Salami and peppers", 9.50, 620, "Sandwich"),
            ("Side Salad", "Small garden salad", 3.99, 100, "Side"),
            ("Soda", "Large fountain drink", 2.50, 200, "Drink")
        ]
        for name, desc, price, cal, cat in menu_data:
            if not db.query(menu.Menu).filter(menu.Menu.dish_name == name).first():
                db.add(menu.Menu(dish_name=name, dish_description=desc, price=Decimal(str(price)), calories=cal, category=cat))
        db.commit()

        # 3. Recipes
        print("Linking recipes...")
        res_map = {r.item: r.id for r in db.query(resources.Resource).all()}
        menu_items = db.query(menu.Menu).all()
        for m in menu_items:
            if not m.recipes:
                if m.dish_name == "Classic Ham":
                    db.add_all([recipes.Recipe(menu_id=m.id, resource_id=res_map["Bread"], amount=2),
                                recipes.Recipe(menu_id=m.id, resource_id=res_map["Ham"], amount=3),
                                recipes.Recipe(menu_id=m.id, resource_id=res_map["Cheese"], amount=1)])
                elif m.dish_name == "Turkey Club":
                    db.add_all([recipes.Recipe(menu_id=m.id, resource_id=res_map["Bread"], amount=3),
                                recipes.Recipe(menu_id=m.id, resource_id=res_map["Turkey"], amount=3),
                                recipes.Recipe(menu_id=m.id, resource_id=res_map["Bacon"], amount=2)])
        db.commit()

        # 4. Customers
        print("Adding customers...")
        # Today's date for birthday demo
        today = date.today()
        customer_data = [
            ("John", "Doe", "john@example.com", "555-0101", "123 Main St", date(1990, today.month, today.day), "pass123"),
            ("Jane", "Smith", "jane@example.com", "555-0102", "456 Oak Rd", date(1995, 5, 15), "pass456"),
            ("Bob", "Wilson", "bob@example.com", "555-0103", "789 Pine Ln", date(1985, 12, 10), "pass789")
        ]
        for f, l, e, p, a, b, pw in customer_data:
            if not db.query(customers.Customers).filter(customers.Customers.email == e).first():
                db.add(customers.Customers(
                    first_name=f, 
                    last_name=l, 
                    email=e, 
                    phone=p, 
                    address=a, 
                    birthday=b, 
                    password=hash_password(pw),
                    reward_points=random.randint(0, 150)
                ))
        db.commit()

        # 5. Promotions
        print("Adding promotions...")
        if not db.query(promotions.Promotions).first():
            db.add(promotions.Promotions(promotions_name="SAVE10", promotions_discount=10, expiration_date=datetime.now() + timedelta(days=30)))
            db.add(promotions.Promotions(promotions_name="WELCOME", promotions_discount=20, expiration_date=datetime.now() + timedelta(days=60)))
        db.commit()

        # 6. Orders (Simulating historical data for reports)
        print("Generating historical orders, rewards, and favorites...")
        custs = db.query(customers.Customers).all()
        menus = db.query(menu.Menu).all()
        
        # Add 15 varied orders
        for i in range(15):
            c = random.choice(custs)
            m = random.choice(menus)
            qty = random.randint(1, 3)
            price = m.price * qty
            
            # Scatter dates over the last 60 days
            order_date = datetime.now() - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
            
            new_order = orders.Order(
                customers_id=c.id,
                customers_name=f"{c.first_name} {c.last_name}",
                customers_email=c.email,
                customers_phone=c.phone,
                tracking_number=generate_tracking_number(),
                order_status="Completed",
                order_date=order_date,
                description=f"Automated demo order {i}",
                total_price=price,
                order_type=random.choice(["Pickup", "Dine-in", "Delivery"])
            )
            db.add(new_order)
            db.flush()

            # Link details
            db.add(order_details.OrderDetail(order_id=new_order.id, menu_id=m.id, amount=qty))
            
            # Add payment
            db.add(payment_info.PaymentInfo(transaction_status="Success", payment_type="Credit Card", order_id=new_order.id, amount=price))
            
            # Add some rewards
            pts = int(price * 10)  # 10 points per dollar
            db.add(rewards.Reward(customer_id=c.id, order_id=new_order.id, points_earned=pts, reward_type="purchase"))

            # Add some favorites
            if random.random() > 0.7:
                # Check if already favorited to avoid unique constraint issues if any (though model doesn't specify unique)
                exists = db.query(favorite_orders.FavoriteOrder).filter_by(customer_id=c.id, order_id=new_order.id).first()
                if not exists:
                    db.add(favorite_orders.FavoriteOrder(customer_id=c.id, order_id=new_order.id))

            # Add some ratings
            if random.random() > 0.5:
                db.add(ratings.Ratings(customers_id=c.id, menu_id=m.id, customers_name=c.first_name, review_text="Delicious!", rating=random.randint(4, 5)))

        db.commit()
        print("Data generation complete! You are ready for your video demo.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_data()
