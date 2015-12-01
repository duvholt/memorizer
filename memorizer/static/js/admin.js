(function() {
    var Form = function(form, list) {
        this.element = form;
        this.url = form.dataset.url;
        this.create = form.dataset['new'] !== undefined;
        this.method =  this.create ? 'POST' : 'PUT';

        this.list = list;
        
        // Form submit
        this.element.addEventListener('submit', this.save.bind(this), false);
    };

    Form.prototype.save = function(e) {
        e.preventDefault();
        var data = {};
        // Loop through all input fields and get name, value pairs
        this.forEachInput(function(input) {
            if(input.type === 'checkbox' && !input.checked) {
                // Do not send data for checkboxes that aren't checked. Silly HTML standard.
                return;
            }
            data[input.name] = input.value;
        });
        // Send post request
        Ajax({url: this.url, data: data, method: this.method}, {
            success: function(data) {
                if(data.success) {
                    // Form was successfully submitted
                    this.forEachInput(function(input) {
                        if(input.type == 'hidden') {
                            // Ignore hidden fields
                            return;
                        }
                        this.emptyField(input.parentNode);
                        if(this.create) {
                            // Empty fields for creation of new objects
                            if(input.type === 'checkbox') {
                                // Only uncheck the checkbox.
                                // If value is empty then the checkbox will be treated as unchecked even if checked.
                                input.checked = false;
                            }
                            else if(input.tagName !== 'SELECT') {
                                input.value = '';
                            }
                        }
                    }.bind(this));
                    if(this.list !== undefined) {
                        this.list.update();
                    }
                    Alert('Fullført', 'success');
                }
                else {
                    // Show valiations status
                    var errors = data.errors;
                    this.forEachInput(function(input) {
                        var field = input.parentNode;
                        var exists = this.emptyField(field);
                        if(!exists) {
                            return;
                        }
                        var errorList = field.getElementsByClassName('errors')[0];
                        if(input.name in errors) {
                            // Validation failed for field
                            field.classList.add('error');
                            // Add errors
                            errors[input.name].forEach(function(error) {
                                var li = document.createElement('li');
                                li.textContent = error;
                                errorList.appendChild(li);
                            });
                        }
                        else {
                            // Validation passed for field
                            field.classList.add('success');
                        }
                    }.bind(this));
                }
            }.bind(this),
            error: function() {
                Alert('Noe gikk forferdelig galt', 'error');
            }
        });
    };
    Form.prototype.inputs = function() {
        return this.element.querySelectorAll('input, select');
    };
    // Helper method to loop input elements with a callback function
    Form.prototype.forEachInput = function(callback) {
        var inputs = this.inputs();
        for(var i in inputs) {
            var input = inputs[i];
            if(input.name !== undefined && input.name !== '') {
                callback(input);
            }
        }
    };
    Form.prototype.emptyField = function(field) {
        if(field === undefined || !field.classList.contains('field')) {
            return false;
        }
        field.classList.remove('success', 'error');
        var errorList = field.getElementsByClassName('errors')[0];
        if(errorList === undefined) {
            // The field is missing an errorlist element and is probably hidden
            return false;
        }
        // Empty error list
        while(errorList.lastChild) {
            errorList.removeChild(errorList.lastChild);
        }
        return true;
    };

    var List = function(adminList) {
        this.element = adminList;
        this.api = adminList.dataset.api;
        this.url = adminList.dataset.url;
        this.filter = adminList.dataset.filter ? adminList.dataset.filter : "";
    };

    List.prototype.empty = function() {
        while(this.element.lastChild) {
            this.element.removeChild(this.element.lastChild);
        }
    };
    List.prototype.li = function(content, id) {
        var li = document.createElement('li');
        // Delete button
        var del = document.createElement('a');
        del.href = '#';
        del.className = 'delete';
        del.innerHTML = '<i class="fa fa-times fa-fw"></i> Slett';
        del.id = id;
        del.onclick = this.deleteObject();

        // Link to edit element
        var a = document.createElement('a');
        a.textContent = content;
        a.href = this.url + id;
        a.className = 'link';

        li.appendChild(a);
        li.appendChild(del);
        return li;
    };
    List.prototype.deleteObject = function(e) {
        var that = this;
        var deleteFunction = function(e) {
            // `this` refers to the object that was clicked
            e.preventDefault();
            Ajax({url: that.api + this.id, method: 'DELETE'}, {
                success: function(data) {
                    Alert('Slettet', 'success');
                    that.update();
                },
                error: function(data) {
                    Alert('Sletting feilet', 'error');
                }
            });
        };
        return deleteFunction;
    };
    List.prototype.update = function() {
        Ajax({url: this.api + this.filter}, {
            success: function(data) {
                this.empty();
                for (var i = 0; i < data.length; i++) {
                    this.element.appendChild(this.li(data[i].str, data[i].id));
                }
            }.bind(this),
            error: function(data) {
                console.error('Failed to fetch admin list data');
            }
        });
    };

    // Initialize admin forms
    var forms = document.getElementsByClassName('form-admin');
    var object = document.getElementsByClassName('admin-list')[0];
    if(object !== undefined) {
        var list = new List(object);
        list.update();
    }
    for (var i = 0; forms[i]; i++) {
        var form = new Form(forms[i], list);
    }
})();
