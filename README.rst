Graphite AWS Cleaner
====================

Delete old graphite data based on instance name pattern and current
running AWS instances.

This is very useful if you have AWS instances that are terminated and
you no longer need their metrics, so you can just remove their stats.

It is required to have AWS credentials set via environment variables
(``AWS_ACCESS_KEY_ID`` and ``AWS_SECRET_ACCESS_KEY``) or IAM roles.

Installation
------------

::

    $ pip install graphite_aws_cleaner

Usage
-----

::

    # aws context
    web_i-123 # running
    web_i-456 # running
    web_i-789 # terminated


    $ graphite-aws-cleaner '*web*' /opt/graphite/storage

This is going to delete all graphite data related to ``web_i-789``,
since the instance is no longer runnning.

Patterns
~~~~~~~~

Anything that matches Python's
`fnmatch.fnmatch <http://docs.python.org/2/library/fnmatch.html>`_
works as a pattern:

+-------------+------------------------------------+
| Pattern     | Meaning                            |
+=============+====================================+
| \*          | matches everything                 |
+-------------+------------------------------------+
| ?           | matches any single character       |
+-------------+------------------------------------+
| [seq]       | matches any character in seq       |
+-------------+------------------------------------+
| [!seq]      | matches any character not in seq   |
+-------------+------------------------------------+

Development
-----------

::

    $ make setup

Running tests
~~~~~~~~~~~~~

::

    $ make test

