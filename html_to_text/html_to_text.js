/* 
FILE: html_to_text.js

DESCRIPTION: 

	Converts HTML email file to plain text while retaining hyperlink locations within brackets.
			 
	Before: "<a href="http://foo.com">bar</a>"
	After: "bar [http://foo.com/]"
	 
REQUIREMENTS: PhantomJS <http://phantomjs.org/>

USAGE:

	$ phantomjs .\html_to_text.js
	>> You must pass a .html file (from your working folder).
	$ phantomjs .\html_to_text.js test.html
	>> created file: .\test.html.txt
*/

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
		var links = document.body.getElementsByTagName("A");
		for (i=0; i < links.length; i++) {
			var link = links[i];
			if (link.text === "") { // skip if no immediate child text value.
				continue;
			}
			if (link.href.substr(0,4) !== "http") { // skip if href value doesn't start with "http".
				continue;
			}
			if (link.text === link.href) { // skip if href value equals immediate child text value.
				continue;
			}
			link.innerText = link.innerText + " [" + link.href + "]";
		}
		return;		
	});
	
// write plain text version to file.
var txt = system.args[1] + ".txt";
fs.write(txt, page.plainText, "w");

// report; exit.
console.log("created file: " + txt);
phantom.exit(); 
});
