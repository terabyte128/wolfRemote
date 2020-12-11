function updateSlider() {
    fetch("/api/v1/tv/backlight").then((response) => {
        if (response.ok) {
            response.json().then(json => {
                document.querySelector('#backlight-slider').value = json['current'];
            })
        }
    })
}

function setInputsDisabled(disabled) {
    document.querySelectorAll("button, input[type=range]").forEach(b => {
        b.disabled = disabled;
    })
}

function makeRequest(url, method, data) {
    setInputsDisabled(true);
    let badge = document.querySelector("#status");

    badge.classList.remove('bg-success');
    badge.classList.add('bg-info');
    badge.innerHTML = "Sending...";

    fetch(url, {
        method: method, 
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
          },
    }).then((response) => {
        if (response.ok) {
            badge.classList.remove('bg-info');
            badge.classList.add('bg-success');
            badge.innerHTML = "Ready";
        } else {
            badge.classList.remove('bg-info');
            badge.classList.add('bg-danger');
            badge.innerHTML = "Failed";

            window.setTimeout(() => {
                badge.classList.remove('bg-danger');
                badge.classList.add('bg-success');
                badge.innerHTML = "Ready";    
            }, 1000);
        }

        setInputsDisabled(false);
    })
} 

function updateHSK(data) {
    document.querySelector("#hue").value = data.hue;
    document.querySelector("#saturation").value = data.saturation;
    document.querySelector("#kelvin").value = data.kelvin;

    setLightBrightness();
}

function setLightBrightness() {
    let diningRoom = document.querySelector("#dining-room");
    let livingRoom = document.querySelector("#living-room");

    let hue = document.querySelector("#hue");
    let saturation = document.querySelector("#saturation");
    let kelvin = document.querySelector("#kelvin");

    let common = {
        "hue": parseInt(hue.value),
        "saturation": parseInt(saturation.value),
        "kelvin": parseInt(kelvin.value)
    }

    let lr = {
        "brightness": parseInt(livingRoom.value),
        ...common
    }

    let dr = {
        "brightness": parseInt(diningRoom.value),
        ...common
    } 

    request = {
        "lr1": lr,
        "lr2": lr,
        "dr1": dr,
        "dr2": dr
    }

    makeRequest("/api/v1/lights", 'put', request);
}

document.addEventListener("DOMContentLoaded", function() {
    // continuously update the backlight slider
    updateSlider();
    document.querySelectorAll("button.make-request").forEach(btn => {
        btn.addEventListener('click', () => makeRequest(btn.dataset.url, btn.dataset.method, btn.dataset));
    })

    function setBacklight(e) {
        let data = e.target.dataset;
        makeRequest(data.url, data.method, {
            "backlight": parseInt(e.target.value)
        });
    }

    document.querySelector('#backlight-slider').onmouseup = setBacklight;
    document.querySelector('#backlight-slider').ontouchend = setBacklight;

    document.querySelectorAll("input.light-slider").forEach(ls => {
        ls.addEventListener('mouseup', setLightBrightness);
        ls.addEventListener('touchend', setLightBrightness);
    })

    document.querySelectorAll("button.btn-light").forEach(lb => {
        lb.addEventListener('click', () => updateHSK(lb.dataset));
    })

    document.querySelectorAll("button").forEach(b => {
        b.addEventListener('click', b.blur);
    })
});

