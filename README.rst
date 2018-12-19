===============
wagtail-linkchecker
===============

A tool/plugin to assist with finding broken links on your wagtail site.
This tool works asynchronously using celery.

Installing
==========

Install using pip::

    pip install wagtail-linkchecker

It works with Wagtail 1.0 and upwards.

Using
=====

To use, firstly you will need to add ``wagtaillinkchecker`` to your ``INSTALLED_APPS`` and run the migrations.
There will now be an extra item on the settings panel of the wagtailadmin. Inside here you can enable or disable automated
scanning (See below for more detail) or conduct a scan.

For scans to be conducted, you must be running a celery daemon.
You can run the celery worker with ``celery -A wagtaillinkchecker worker -l info``. See the `Celery Documentation <http://docs.celeryproject.org/en/latest/index.html>`_ for more information.
For production you'll want to run celery as a daemon using something like systemd. See `Celery Daemonization <http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#daemonizing>`_ for more information.

Conducting a scan
-----------------
Conducting a scan will scan all of your wagtail pages, and detect all images and anchors with a ``src`` or ``href`` respectively.
Utilising the ``requests`` and ``BeautifulSoup`` libraries, requests will be made to each link to make sure an appropriate response
is received, and if no appropriate response is received, once the scan is complete, all broken links along with their status codes and
reasons will appear.

Scan results will be stored.

Automated Scanning
------------------
If you want automated scanning to work you **HAVE** to set up a cron job. The cron job will need to run the management command ``linkchecker`` at
an interval of your choosing.
The automated scans will do the same as manually conducting a scan, but instead will email the last person to edit the page with broken links/images.
