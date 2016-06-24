var Sidebar = function() {
    this.nav = document.querySelector('nav.sidebar');
    this.menu = document.querySelector('nav.top .menu');
    this.icon = this.menu.querySelector('i');
    this.closedIcon = 'fa-navicon';
    this.openIcon = 'fa-times';
    this.closedClass = ' closed';

    this.menu.addEventListener('click', function(e) {
        this.toggle(e);
    }.bind(this), false);
};

Sidebar.prototype.isClosed = function() {
    return this.nav.className.indexOf('closed') > -1;
};

Sidebar.prototype.close = function() {
    this.icon.className = this.icon.className.replace(this.openIcon, this.closedIcon);
    this.nav.className += this.closedClass;

    document.removeEventListener('click', this.clickEvent);
};

Sidebar.prototype.open = function() {
    this.nav.className = this.nav.className.replace(this.closedClass, '');
    this.icon.className = this.icon.className.replace(this.closedIcon, this.openIcon);

    this.clickEvent = function(e) {
        if(this.menu == e.target) {
            e.stopPropagation();
        }
        else if(document.documentElement == e.target) {
            this.close();
        }
    }.bind(this);

    document.addEventListener('click', this.clickEvent);
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
