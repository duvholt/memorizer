/*
    "When I'm not longer rapping, I want to open up an ice cream parlor and call myself Scoop Dogg."
    - Snoop Dogg

    Scoop, because what the world needs right now is yet another JavaScript templating engine

    {$ var } - print with escaping
    {_ var } - print without escaping
    {+ for var in vars } - foreach loop
*/

(function() {
    // Settings
    var s = {
        idMatch: /^[\w-]+$/,
        print: /\{\$\s*(.*?)\s*\$\}/g,
        printSafe: /\{\_\s*(.*?)\s*\_\}/g
        
    };
    // Some day...
    var cache = {};

    // Render template code into HTML
    var render = function(str, context) {
        if(s.idMatch.test(str)) {
            return render(document.getElementById(str));
        }
        str = str.
        replace(
            s.print, function(match, value) {
                return encode(lookup(context, value));
            }
        ).replace(
            s.printSafe, function(match, value) {
                return lookup(context, value);
            }
        );
        return str;
    };

    // HTML encoding http://stackoverflow.com/a/15348311
    var encode = function(text) {
        return document.createElement('i').appendChild( 
        document.createTextNode(text)).parentNode.innerHTML;
    };

    // Tries to find key like person.name in an object
    var lookup = function(data, key) {
        var props = key.split('.');
        while(props.length) {
            var prop = props.pop();
            if(data.hasOwnProperty(prop)) {
                data = data[prop];
            }
            else {
                // Key not found
                return "";
            }
        }
        return data;
    };

    this.scoop = function(str, context) {
        // TODO: Add caching
        return render(str, context);
    };
})();
