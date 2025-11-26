

# # # backend/app.py
# # from flask import Flask, jsonify
# # from .config import Config
# # from .extensions import db
# # from .auth import bp as auth_bp
# # from .vendors import bp as vendors_bp
# # import os

# # def create_app():
# #     app = Flask(__name__, static_folder="static", template_folder="templates")
# #     app.config.from_object(Config)
# #     db.init_app(app)

# #     # register blueprint(s)
# #     app.register_blueprint(auth_bp)
# #     app.register_blueprint(vendors_bp)


# #     @app.route("/")
# #     def home():
# #        return jsonify({
# #             "message": "FEMS Backend API is running!",
# #             "version": "1.0",
# #             "status": "active",
# #             "endpoints": {
# #                 "register": "/api/register",
# #                 "verify_email": "/api/verify-email",
# #                 "complete_profile": "/api/complete-profile",
# #                 "login": "/api/login",
# #                 "profile": "/api/profile",
# #                 "create_menu": "/api/vendors/<vendor_id>/menu",
# #                 "add_items": "/api/vendors/<vendor_id>/menu/<menu_id>/items",
# #                 "update_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
# #                 "delete_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
# #                 "get_vendor": "/api/vendors/<vendor_id>"
# #             }
# #         })
# #     return app

# # if __name__ == "__main__":
# #     app = create_app()
# #     with app.app_context():
# #         db.create_all()  # creates tables according to models.py (including FK ondelete)
# #         print("✅ Database tables created successfully!")
    
    
    

# #     app.run(debug=True, port=5000)



# #AFTER MERGING :

# # backend/app.py
# from flask import Flask, jsonify
# from flask_cors import CORS
# from .config import Config
# from .extensions import db
# from .auth import bp as auth_bp
# from .vendors import bp as vendors_bp
# from .customer_routes import bp as customer_bp

# def create_app():
#     app = Flask(__name__, static_folder="static", template_folder="templates")
#     app.config.from_object(Config)
    
#     # Enable CORS for frontend communication
#     CORS(app, resources={
#         r"/api/*": {
#             "origins": ["http://localhost:3000", "http://localhost:5173"],
#             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
#             "allow_headers": ["Content-Type", "Authorization"]
#         }
#     })
    
#     db.init_app(app)

#     # Register all blueprints
#     app.register_blueprint(auth_bp)        # Authentication (shared by both)
#     app.register_blueprint(vendors_bp)     # Vendor operations
#     app.register_blueprint(customer_bp)    # Customer operations

#     @app.route("/")
#     def home():
#         return jsonify({
#             "message": "FEMS Backend API is running!",
#             "version": "2.0",
#             "status": "active",
#             "services": {
#                 "authentication": "active",
#                 "vendor_management": "active",
#                 "customer_operations": "active"
#             },
#             "endpoints": {
#                 "auth": {
#                     "register": "/api/register",
#                     "verify_email": "/api/verify-email",
#                     "login": "/api/login",
#                     "complete_profile": "/api/complete-profile",
#                     "profile": "/api/profile"
#                 },
#                 "vendor": {
#                     "create_menu": "/api/vendors/<vendor_id>/menu",
#                     "add_items": "/api/vendors/<vendor_id>/menu/<menu_id>/items",
#                     "update_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
#                     "delete_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
#                     "get_vendor": "/api/vendors/<vendor_id>"
#                 },
#                 "customer": {
#                     "browse_vendors": "/api/customer/vendors",
#                     "view_menu": "/api/customer/vendors/<vendor_id>/menu",
#                     "place_order": "/api/customer/orders",
#                     "view_order": "/api/customer/orders/<order_id>",
#                     "order_history": "/api/customer/orders",
#                     "cancel_order": "/api/customer/orders/<order_id>/cancel",
#                     "get_stats": "/api/customer/stats",
#                     "health_check": "/api/customer/health"
#                 }
#             }
#         })
    
#     @app.route("/api/health", methods=["GET"])
#     def health_check():
#         """Global health check endpoint"""
#         try:
#             db.session.execute(db.text("SELECT 1"))
#             return jsonify({
#                 "status": "healthy",
#                 "database": "connected",
#                 "services": {
#                     "auth": "operational",
#                     "vendor": "operational",
#                     "customer": "operational"
#                 }
#             }), 200
#         except Exception as e:
#             return jsonify({
#                 "status": "unhealthy",
#                 "database": "disconnected",
#                 "error": str(e)
#             }), 500

#     return app

# if __name__ == "__main__":
#     app = create_app()
#     with app.app_context():
#         db.create_all()
#         print("✅ Database tables created successfully!")
#         print("🚀 FEMS Backend Server Starting...")
#         print("📍 Vendor endpoints: /api/vendors/*")
#         print("📍 Customer endpoints: /api/customer/*")
#         print("📍 Auth endpoints: /api/register, /api/login, etc.")
    
#     app.run(debug=True, port=5000, host='0.0.0.0')
from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .extensions import db
from .auth import bp as auth_bp
from .vendors import bp as vendors_bp
from .customer_routes import bp as customer_bp

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)

    # ============ CORS CONFIGURATION ============
    # This allows frontend on different port to call backend API
    CORS(app, resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # Alternative port
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 3600
        }
    })

    # register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(vendors_bp)
    app.register_blueprint(customer_bp)

    @app.route("/")
    def home():
        return jsonify({
            "message": "FEMS Backend API is running!",
            "version": "1.0",
            "status": "active",
            "endpoints": {
                "auth": {
                    "register": "POST /api/register",
                    "verify_email": "POST /api/verify-email",
                    "complete_profile": "POST /api/complete-profile",
                    "login": "POST /api/login",
                    "profile": "GET /api/profile",
                },
                "vendors": {
                    "list": "GET /api/vendors",
                    "detail": "GET /api/vendors/<vendor_id>",
                    "create_menu": "POST /api/vendors/<vendor_id>/menu",
                    "add_items": "POST /api/vendors/<vendor_id>/menu/<menu_id>/items",
                    "update_item": "PUT /api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
                    "delete_item": "DELETE /api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
                }
            }
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")

    app.run(debug=True, port=5000, host='0.0.0.0')
