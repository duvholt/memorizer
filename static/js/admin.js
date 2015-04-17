(function() {
    var Form = function(form) {
        var that = this;
        this.element = form;
        this.url = form.dataset.url;
        
        // Form submit
        this.element.addEventListener('submit', function(e) {
            that.save(e);
        }, false);
    };

    Form.prototype.save = function(e) {
        e.preventDefault();
        var data = {};
        // Loop through all input fields and get name, value pairs
        var inputs = this.element.querySelectorAll('input');
        for(var i in inputs) {
            var input = inputs[i];
            if(input.name !== undefined) {
                data[input.name] = input.value;
            }
        }
        // Send post request
        Ajax({url: this.url, data: data, method: 'POST'}, {
            success: function(data) {
                console.log(data);
            }
        });
    };
    var formElement = document.getElementById('new-form');
    var form = new Form(formElement);
})();
