from . import orders, order_details, recipes, sandwiches, resources, payment_info, customers, menuitems, promotions, ratings

from ..dependencies.database import engine


def index():
    orders.Base.metadata.create_all(engine)
    order_details.Base.metadata.create_all(engine)
    recipes.Base.metadata.create_all(engine)
    sandwiches.Base.metadata.create_all(engine)
    resources.Base.metadata.create_all(engine)
    payment_info.Base.metadata.create_all(engine)
    customers.Base.metadata.create_all(engine)
    menuitems.Base.metadata.create_all(engine)
    promotions.Base.metadata.create_all(engine)
    ratings.Base.metadata.create_all(engine)