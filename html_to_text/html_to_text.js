/* 
FILE: html_to_text.js

DESCRIPTION: 

    Converts HTML email file to plain text while retaining hyperlink locations within brackets.
             
    Before: "<a href="http://foo.com">bar</a>"
    After: "bar <http://foo.com/>"
	 
REQUIREMENTS: PhantomJS <http://phantomjs.org/>

USAGE:

    $ phantomjs .\html_to_text.js
    >> You must pass a .html file (from your working folder).
    $ phantomjs .\html_to_text.js test.html
    >> created file: .\test.html.txt; processing time (seconds): 0
*/

// get current time (to test script speed).
var _DATE = new Date();
var time_in = _DATE.getTime();

// includes.
var fs = require("fs");
var webpage = require("webpage");
var system = require("system");

// test for file argument.
if (system.args.length === 1) {
    console.log("You must pass a .html file (from your working folder).");
    phantom.exit(); 
} 

// create browser path to HTML file.
var html = "file:///" + fs.workingDirectory + "/" + system.args[1];

// rewrite "A" tag values for plain text version.
var page = webpage.create();
page.open(html, function (status) {
    var modify = page.evaluate(function() {
        var children = document.body.getElementsByTagName("A");
        for (i=0; i < children.length; i++) {
            var child = children[i];
            child.innerText = child.innerText + " <" + child.href + ">";
        }
        return;        
    });
  
// write plain text version to file.
var txt = system.args[1] + ".txt";
fs.write(txt, page.plainText, "w");

// get script completion speed; report.
var time_out = _DATE.getTime();
var time_results = time_out - time_in;
var report = "created file: " + txt + "; processing time (seconds): " + time_results; 
console.log(report);

// exit.
phantom.exit(); 
});
