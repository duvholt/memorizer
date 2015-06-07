var Sidebar = function() {
    this.nav = document.querySelector('nav.sidebar');
    this.icon = document.querySelector('nav.top .logo i');
    this.closedIcon = 'fa-navicon';
    this.openIcon = 'fa-times';
    this.closedClass = ' closed';

    this.icon.addEventListener('click', function(e) {
        this.toggle(e);
    }.bind(this), false);

};

Sidebar.prototype.isClosed = function() {
    return this.nav.className.indexOf('closed') > -1;
};

Sidebar.prototype.close = function() {
    this.icon.className = this.icon.className.replace(this.openIcon, this.closedIcon);
    this.nav.className += this.closedClass;
};

Sidebar.prototype.open = function() {
    this.nav.className = this.nav.className.replace(this.closedClass, '');
    this.icon.className = this.icon.className.replace(this.closedIcon, this.openIcon);
};

Sidebar.prototype.toggle = function(e) {
    if(this.isClosed()) {
        this.open();
    }
    else {
        this.close();
    }
};

var sidebar = new Sidebar();
