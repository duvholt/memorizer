// Simple ajax wrapper. Assumes all data is objects/json

var Ajax = function(options, callback) {
    var that = this;
    var defaults = function(standard, options) {
        var newSettings = standard;
        // Override specified options
        for(var key in options) {
            if (options.hasOwnProperty(key)) {
                newSettings[key] = options[key];
            }
        }
        return newSettings;
    };  

    var settings = defaults({
        method: 'GET'
    }, options);

    // On ajax state change
    var response = function() {
        if(request.readyState !== 4) {
            return;
        }
        if(request.status === 200) {
            // Everything went well! At least let's hope so
            callback.success(JSON.parse(request.responseText));
        }
        else {
            // Oops
            callback.error(request.responseText);
        }
    };

    // Send data
    var params = [];
    // Converting object to key=value&key2=value2 string
    if(settings.data !== undefined) {
        for(var key in settings.data) {
            if(settings.data.hasOwnProperty(key)) {
                if(settings.data[key].constructor === Array) {
                    // Add the key several times if array
                    for (var i = 0; i < settings.data[key].length; i++) {
                        params.push(encodeURIComponent(key) + '=' + encodeURIComponent(settings.data[key][i]));
                    };
                }
                else {
                    params.push(encodeURIComponent(key) + '=' + encodeURIComponent(settings.data[key]));
                }
            }
        }
    }

    var url = settings.url;
    // Adding querystring if GET
    if(settings.method === 'GET') {
        url += '?' + params.join('&');
    }

    // Initiate ajax request
    var request = new XMLHttpRequest();
    request.onreadystatechange = response;
    // HTTP method and URL from settings
    request.open(settings.method, url);

    var postData = null;
    // Add content type if post request
    if(['POST', 'PUT'].indexOf(settings.method) !== -1) {
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        postData = params.join('&');
    }

    request.send(postData);
};
