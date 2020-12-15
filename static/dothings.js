function updateBacklightSlider() {
    fetch("/api/v1/tv/backlight").then((response) => {
        if (response.ok) {
            response.json().then(json => {
                document.querySelector('#backlight-slider').value = json['current'];
            })
        }
    });
}

function avg(...xs) {
    return xs.reduce((a, b) => a + b) / xs.length;
}

function updateLightBrightnessSlider() {
    fetch("/api/v1/lights").then(response => {
        if (response.ok) {
            response.json().then(json => {
                let lrAvg = avg(json['lr1']['brightness'], json['lr2']['brightness']);
                let drAvg = avg(json['dr1']['brightness'], json['dr2']['brightness']);

                document.querySelector("#living-room").value = lrAvg;
                document.querySelector("#dining-room").value = drAvg;

                let hue = avg(...Object.keys(json).map(k => json[k]['hue']));
                let saturation = avg(...Object.keys(json).map(k => json[k]['saturation']));
                let kelvin = avg(...Object.keys(json).map(k => json[k]['kelvin']));

                document.querySelector("#hue").value = hue;
                document.querySelector("#saturation").value = saturation;
                document.querySelector("#kelvin").value = kelvin;
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

function setBacklight(e) {
    let data = e.target.dataset;
    makeRequest(data.url, data.method, {
        "backlight": parseInt(e.target.value)
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // update sliders
    updateBacklightSlider();
    updateLightBrightnessSlider();

    // make a generic request when certain buttons are pressed
    document.querySelectorAll("button.make-request").forEach(btn => {
        btn.addEventListener('click', () => makeRequest(btn.dataset.url, btn.dataset.method, btn.dataset));
    })

    // listen for changes on backlight slider
    document.querySelector('#backlight-slider').addEventListener('mouseup', setBacklight);
    document.querySelector('#backlight-slider').addEventListener('touchend', setBacklight);

    // listen for changes on light sliders
    document.querySelectorAll("input.light-slider").forEach(ls => {
        ls.addEventListener('mouseup', setLightBrightness);
        ls.addEventListener('touchend', setLightBrightness);
    });

    // listen for clicks to lights that control buttons
    document.querySelectorAll("button.btn-light").forEach(lb => {
        lb.addEventListener('click', () => updateHSK(lb.dataset));
    });

    // try to stop buttons from being highlighted when clicking
    document.querySelectorAll("button").forEach(b => {
        b.addEventListener('click', b.blur);
    });

    // super special developer settings
    document.querySelector("#toggle-debug").addEventListener('click', () => {
        var x = document.querySelector("#debug-options");
        if (x.style.display === "none") {
          x.style.display = "block";
        } else {
          x.style.display = "none";
        }
    });

    // keep track of focus so that focus events are debounced
    window.addEventListener('blur', () => focused = false);

    // onfocus, update sliders
    window.addEventListener('focus', function() {
        if (!focused) {
            // update sliders on focus
            updateBacklightSlider();
            updateLightBrightnessSlider();
            focused = true;
        }
    })

    // set the current tab based on the tab before reload
    let currentTab = localStorage.getItem('currentTab') || "tv-tab";
    var tab = new bootstrap.Tab(document.querySelector(`#${currentTab}`));
    tab.show();

    // track current tab when switched
    document.querySelectorAll('a[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (event) {
            localStorage.setItem('currentTab', event.target.id);
        });
    });
});

