import logging
from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

logging.getLogger().setLevel(logging.INFO)

with app.app_context():
    from server.api.tv import tv_bp
    from server.api.receiver import receiver_bp
    from server.api.sequences import seq_bp, SEQUENCES
    from server.api.lights import lights_bp


API_PREFIX = "/api/v1"


# register API blueprints
app.register_blueprint(tv_bp, url_prefix=f"/{API_PREFIX}/tv")
app.register_blueprint(receiver_bp, url_prefix=f"{API_PREFIX}/receiver")
app.register_blueprint(seq_bp, url_prefix=f"{API_PREFIX}/sequence")
app.register_blueprint(lights_bp, url_prefix=f"{API_PREFIX}/lights")

# register API docs blueprint
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = (
    "/static/openapi.yaml"  # Our API url (can of course be a local resource)
)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={"app_name": "wolfRemote"},  # Swagger UI config overrides
)

app.register_blueprint(swaggerui_blueprint)
