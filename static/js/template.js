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
        print: /\{\$\s*(.*?)\s*\}/g,
        printSafe: /\{\_\s*(.*?)\s*\}/g
        
    };
    var cache = {};


    this.scoop = function(str, context) {
        // Caching
        if(!cache[str]) {
            cache[str] = scoop.compile(str);
        }
        fn = cache[str];
        return fn(context);
    };

    // Compile template code into HTML
    scoop.compile = function(str) {
        if(s.idMatch.test(str)) {
            return scoop.compile(document.getElementById(str));
        }
        function_code = 'return \'';
        function_code += str.
        replace(
            s.print, function(match, value) {
                return '\' + scoop.encode(scoop.lookup(context, \'' + value + '\')) + \'';
            }
        ).replace(
            s.printSafe, function(match, value) {
                return '\' + scoop.lookup(context, \'' + value + '\') + \'';
            }
        );
        function_code += '\';';
        return new Function('context', function_code);
    };


    // HTML encoding http://stackoverflow.com/a/15348311
    scoop.encode = function(text) {
        return document.createElement('i').appendChild( 
        document.createTextNode(text)).parentNode.innerHTML;
    };

    // Tries to find key like person.name in an object
    scoop.lookup = function(data, key) {
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
})();
