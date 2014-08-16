========================
Evolutek simulator webui
========================

Build with the pantograph library.

Install
=======

.. codeblock:: bash

    # If you want to run it inside a virtualenv:
    $ virtualenv venv
    $ source venv/bin/activate

    # Else just use:
    $ pip install -r requirements

Use
===

You can configure the listening address and port of the application by setting
the ADDR and PORT variables in ``app.py``.

Start the simulator:

.. codeblock:: bash

    $ python app.py

Then in your browser go to (default url): http://127.0.0.1:8080
