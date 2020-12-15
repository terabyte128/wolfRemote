import os
import json
from flask import Flask, render_template
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

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

# register API docs blueprint
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/static/openapi.yaml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "wolfRemote"
    },
)

app.register_blueprint(swaggerui_blueprint)

# try to import and use CEC if its installed
use_cec = True

try:
    import cec
    print("using cec")
except ModuleNotFoundError:
    print("cec not found, not using")
    use_cec = False

if use_cec:
    cec.init()
    cec_devices = cec.list_devices()
    print("found", cec_devices)

CEC_SEQUENCES = {
    "Chromecast": SEQUENCES['chromecast'],
    "NintendoSwitch": SEQUENCES['switch']
}

# callback for HDMI-CEC
def cec_cb(*args):
    if len(args) != 2:
        return # only respond to the right command

    source = args[0]
    params = args[1]

    if params['opcode'] != 0x82:
        return # only respond to 0x82, which is "active source"

    device = cec_devices[source]
    print("device", device.osd_string, "became active")

    # activate seq if exists
    if device.osd_string in CEC_SEQUENCES:
        CEC_SEQUENCES[device.osd_string]()

if use_cec:
    cec.add_callback(cec_cb, cec.EVENT_ALL)

@app.route("/")
def index():
    context = {
        "picture_modes": TV.get_picture_mode()
    }
    return render_template("index.html", **context)