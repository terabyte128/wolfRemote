import lifxlan as lifx

from api import LIGHTS, SCENES
from flask import Blueprint, request

lights_bp = Blueprint("lights", __name__)

@lights_bp.route("", methods=("GET",))
def get_lights():
    lights = {}

    try:
        for k, v in LIGHTS.items():
            color = v.get_color()

            lights[k] = {
                "hue": color[0],
                "saturation": color[1],
                "brightness": color[2],
                "kelvin": color[3]
            }
    except lifx.WorkflowException as e:
        return {
            "error": "Failed to communicate with lights",
            "details": str(e)
        }, 500
        
    return lights

@lights_bp.route("", methods=("PUT",))
def set_lights():
    resp = {}

    try:
        for k, v in LIGHTS.items():
            if k in request.json:
                new_params = request.json[k]
                orig_color = v.get_color()
                color = list(orig_color)
                resp[k] = {}

                for i, param in enumerate(['hue', 'saturation', 'brightness', 'kelvin']):
                    if param in new_params:
                        color[i] = new_params[param]

                    resp[k][param] = color[i]
                
                # be lazy
                if tuple(color) != orig_color:
                    v.set_color(color, 500)

    except lifx.WorkflowException as e:
        return {
            "error": "Failed to communicate with lights",
            "details": str(e)
        }, 500

    return resp
