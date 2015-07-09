# blackboard-selenium-python
Framework for tedious web-based tasks in Blackboard for python.

You'll need to install Python, Selenium for python ( https://pypi.python.org/pypi/selenium ), and a compatible (old) version of Firefox.  All these methods should support the HTMLUnit Driver that runs inside the "Selenium Standalone Server" from http://www.seleniumhq.org/download/ , but you'll want to do your testing/development with Firefox.

Selenium has an annoying issue that it can't connect to an existing browser.  So instead of restarting Firefox every few seconds for incremental development, I wrote a starting point called BbGateway.py that constantly reloads testModule.py and runs a method from there against the existing Firefox window.  That way you can have testModule.py open in an editor, and every time you save it, you just type in your test name into BbGateway and it will reload your changes and run your test.  That's way better than compiling java, I think.

Test case names are at the bottom of testModule.py.  The server, username, and password go in a file called BbWebCredentials-${BbEnvironment}.py.  To delete /internal/courses content from Firefox, you do:

$ BbEnvironment=example ./BbGateway.py
Waiting for Signal
Do Test? delUploads

and hopefully it works for you.

I didn't write this to be shared originaly, so it's super sloppy and could use some real reorganization.  Feel free to apply for a push request and help me add to this and clean it up.


