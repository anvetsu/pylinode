## PyLinode

This provides an API and a command line tool named `linode` to interface with the [Linode](http://linode.com) API.
This requires Python2 and does not run on Python3 yet.

## Installation

Clone this repo.

    $ git clone git@github.com:anvetsu/pylinode.git

Install requirements.

    $ cd pylinode
    $ pip install -r requirements.txt

Run setup.

    $ python setup.py install

## Linode Auth

Login to your linode account and create an API token.

Create a file in your `$HOME` directory named `.li.cfg` with the following contents.

```
[linode]
auth_token=<your linode API key>
```

Or you can run the `linode --configure` command.

## Usage

To configure Linode API key.

    $ linode --configure

To get help.

    $ linode --help

To get specific command help.

    $ linode `command` --help

    e.g: linode create --help
 
