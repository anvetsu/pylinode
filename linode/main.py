# -*- coding: utf-8 -*-

import os
import click
from commands.linode_create import linode_create_group
from commands.base_request import CONTEXT_SETTINGS

sources_list = [linode_create_group]

def config_file(file, reconfigure=False):
	"""
	create configuration file
	"""
	value = click.prompt('Enter linode access token', type=str)
	f = open(file, 'w')
	f.write('[linode]\nauth_token='+value)
	f.close()
	if not reconfigure:
		bashrc = os.path.expanduser('~/.bashrc')
		bash_profile = os.path.expanduser('~/.bash_profile')
		profile = os.path.expanduser('~/.profile')
		if os.path.isfile(bashrc):
			bashrc_file = open(bashrc, 'a')
			bashrc_file.write('\neval "$(_LINODE_COMPLETE=source linode)"')
			bashrc_file.close()
			click.echo("apply changes by running 'source ~/.bashrc' without ''")
		elif os.path.isfile(bash_profile):
			bash_profile_file = open(bash_profile, 'a')
			bash_profile_file.write('\neval "$(_LINODE_COMPLETE=source linode)"')
			bash_profile_file.close()
			click.echo("apply changes by running 'source ~/.bash_profile' without ''")
		elif os.path.isfile(profile):
			profile_file = open(profile, 'a')
			profile_file.write('\neval "$(_LINODE_COMPLETE=source linode)"')
			profile_file.close()
			click.echo("apply changes by running 'source ~/.profile' without ''")
		else:
			msg = 'Add following line to your bashrc.\n eval "$(_LINODE_COMPLETE=source linode)"'
			click.echo(msg)
	click.echo()
	click.echo("configuration completed.")


@click.command(cls=click.CommandCollection, sources=sources_list, context_settings=CONTEXT_SETTINGS, invoke_without_command=True, no_args_is_help=True)
@click.option('-c', '--configure', is_flag=True, help='configure linode access token')
@click.version_option(version=1.0, message=('Linode command line interface. \n%(prog)s, version %(version)s, by Yogesh panchal, yspanchal@gmail.com'))
def linode(configure):
	"""
	'linode' is Linode command line interfaces

	# To configure linode
	>>> linode --configure

	# To get list available commands
	>>> linode --help
	"""
	if configure:
		file = os.path.expanduser('~/.li.cfg')
		if not os.path.isfile(file):
			config_file(file)
		else:
			value = click.prompt('Do you want to reconfigure linode [y/n] ?', type=str, default='n')
			if value.lower() == 'y':
				reconfigure = True
				config_file(file, reconfigure)
			else:
				click.echo()
				click.echo('done..!!!')


if __name__ == '__main__':
	docli()