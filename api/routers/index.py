from . import orders, order_details, ratings, customers, promotions


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(ratings.router)
    app.include_router(customers.router)
    app.include_router(promotions.router)