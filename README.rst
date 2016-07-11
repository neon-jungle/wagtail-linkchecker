===============
wagtail-linkchecker
===============

A tool/plugin to assist with finding broken links on your wagtail site.

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

Conducting a scan
-----------------
Conducting a scan will scan all of your wagtail pages, and detect all images and anchors with a ``src`` or ``href`` respectively.
Utilising the ``requests`` and ``BeautifulSoup`` libraries, requests will be made to each link to make sure an appropriate response
is received, and if no appropriate response is received, once the scan is complete, all broken links along with their status codes and
reasons will appear.

Configuration
-------------
Currently you can configure a time for the scanning script to wait between URLs in seconds with the django setting ``LINKCHECKER_DELAY``.

Automated Scanning
------------------
If you want automated scanning to work you **HAVE** to set up a cron job. The cron job will need to run the management command ``linkchecker`` at
an interval of your choosing.
The automated scans will do the same as manually conducting a scan, but instead will email the last person to edit the page with broken links/images.
