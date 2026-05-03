from . import orders, order_details, ratings, customers, payment_info, promotions, menu, resources

def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(ratings.router)
    app.include_router(customers.router)
    app.include_router(payment_info.router)
    app.include_router(promotions.router)
    app.include_router(menu.router)
    app.include_router(resources.router)
