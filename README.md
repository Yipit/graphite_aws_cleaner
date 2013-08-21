# Graphite AWS Cleaner

Delete old graphite data based on instance name pattern and current running AWS instances.

This is very useful if you have AWS instances that are terminated and you no
longer need their metrics, so you can just remove their stats.

It is required to have AWS credentials set via environment variables or IAM roles.


## Installation

    $ pip install graphite_aws_cleaner


## Usage

    # aws context
    web_i-123 # running
    web_i-456 # running
    web_i-789 # terminated


    $ graphite-aws-cleaner '*web*' /graphite/storage

This is going to delete all graphite data related to `web_i-789`,
since the instance is no longer runnning.


## Development

    $ pip install -r development.txt


### Running tests

    $ py.test -v