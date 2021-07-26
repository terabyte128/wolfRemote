import os
import json
import logging
from flask import Flask, render_template, Blueprint
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")

logging.getLogger().setLevel(logging.INFO)

with app.app_context():
    from api import TV
    from api.tv import tv_bp
    from api.receiver import receiver_bp
    from api.sequences import seq_bp, SEQUENCES
    from api.lights import lights_bp

API_PREFIX = "/api/v1"


# register API blueprints
app.register_blueprint(tv_bp, url_prefix=f"/{API_PREFIX}/tv")
app.register_blueprint(receiver_bp, url_prefix=f"{API_PREFIX}/receiver")
app.register_blueprint(seq_bp, url_prefix=f"{API_PREFIX}/sequence")
app.register_blueprint(lights_bp, url_prefix=f"{API_PREFIX}/lights")

# special blueprint to serve API static files from a separate directory from the frontend
app.register_blueprint(
    Blueprint(
        "api_static",
        "api_static",
        static_folder="static",
        static_url_path="/api/static",
    )
)

# register API docs blueprint
SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/api/static/openapi.yaml"  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={"app_name": "wolfRemote"},  # Swagger UI config overrides
)

app.register_blueprint(swaggerui_blueprint)

# try to import and use CEC if its installed
use_cec = True

try:
    import cec

    logging.info("using cec")
except ModuleNotFoundError:
    print("cec not found, not using")
    use_cec = False

if use_cec:
    cec.init()
    cec_devices = cec.list_devices()
    logging.info(f"found {cec_devices}")

CEC_SEQUENCES = {
    # chromecast concatenates the device name
    "Living Room T": SEQUENCES["chromecast"],
    "NintendoSwitch": SEQUENCES["switch"],
}

# callback for HDMI-CEC
def cec_cb(*args):
    if len(args) != 2:
        return  # only respond to the right command

    source = args[0]
    params = args[1]

    if params["opcode"] != 0x82:
        return  # only respond to 0x82, which is "active source"

    logging.info(f"received CEC from {source} with params {params}")

    device = cec_devices[source]
    logging.info(f"device {device.osd_string} became active")

    # activate seq if exists
    if device.osd_string in CEC_SEQUENCES:
        CEC_SEQUENCES[device.osd_string]()


if use_cec:
    cec.add_callback(cec_cb, cec.EVENT_ALL)


@app.route("/")
def index():
    return app.send_static_file("index.html")


print("registered routes:")
print(app.url_map)
