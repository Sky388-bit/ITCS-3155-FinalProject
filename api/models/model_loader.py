from . import orders, order_details, recipes, sandwiches, resources, payment_info, customers, menu, promotions, ratings, favorite_orders, rewards

from ..dependencies.database import engine


def index():
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
    payment_info.Base.metadata.create_all(engine)
    customers.Base.metadata.create_all(engine)
    menu.Base.metadata.create_all(engine)
    promotions.Base.metadata.create_all(engine)
    ratings.Base.metadata.create_all(engine)
    favorite_orders.Base.metadata.create_all(engine)
    rewards.Base.metadata.create_all(engine)