=============================
djangocms-oscar-news
=============================

Simple news app for Oscar E-Commerce sites based on Django-CMS.

Documentation
-------------

The full documentation will be at https://django-oscar-news.readthedocs.org sometimes :)

Quickstart
----------

Install djangocms-oscar-news::

    pip install -e git+https://github.com/okfish/django-oscar-news#egg=django-oscar-news

Then use it in a project::

    INSTALLED_APPS = [ ..., 'oscar_news' ]

    ./manage.py migrate oscar_news

Features
--------

* Taggable and categorised news models based on Django-CMS placeholder and djangocms_text_ckeditor HTMLField
* Each news entry can be linked to any product, product's categories or classes
* Images via django-filer
* Generic views and templates for news details and listings
* Django-CMS app hook
* Django-CMS plugins for latest filtered news, for category tree and for tags cloud
* Django-CMS front-editable fields for news title and description
* Django-CMS toolbar

* TODO:
    * django-meta
    * feeds
    * Tests-tests-tests


Running Tests
--------------

Sorry, no test yet :( But you are welcome :)

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

Credits
---------

This code is based on the excellent @yakky plugin djangocms-blog https://github.com/nephila/djangocms-blog
It was simplified to decrease the number of dependencies (aldryn etc) and also linked to some Oscar's entities.

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
