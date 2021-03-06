
# -*- coding: utf-8 -*-

import os
import logging
import requests
import ConfigParser

import click
from tabulate import tabulate

try:
	requests.packages.urllib3.disable_warnings()
except:
	requests_log = logging.getLogger("requests")
	requests_log.setLevel(logging.CRITICAL)


class Linode(object):
	"""
	Basic api requests class for linode
	"""
	
	api_url = "https://api.linode.com/?"

	@classmethod
	def do_request(self, method, url, *args, **kwargs):

		auth_token = kwargs.get('token', None)
		params = kwargs.get('params', None)
		headers = kwargs.get('headers', None)
		proxy = kwargs.get('proxy', None)

		if not auth_token:
			try:
				config = ConfigParser.ConfigParser()
				config.read(os.path.expanduser('~/.li.cfg'))
				auth_token = config.get('linode', 'auth_token') or os.getenv('li_auth_token')
			except:
				auth_token = None

		if not auth_token:
			data = {'ERRORARRAY':[{'ERRORMESSAGE':'Authentication token not provided.'}]}
			return data

		if proxy:
			proxy = {'http': proxy}

		request_method = {'GET':requests.get, 'POST': requests.post, 'PUT': requests.put, 'DELETE': requests.delete}

		request_url = self.api_url + 'api_key=' + auth_token + url

		req = request_method[method]

		try:
			res = req(request_url, headers=headers, params=params,  proxies=proxy)
		except (requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
			data = {'ERRORARRAY':[{'ERRORMESSAGE': e.message}]}
			return data

		if res.status_code == 204:
			data = {'ERRORARRAY':[]}
			return data_dict

		try:
			data = res.json()
			data.update({'ERRORARRAY':''})
		except ValueError as e:
			msg = "Cannot read response, %s" %(e.message)
			data = {'ERRORARRAY':[{'ERRORMESSAGE': e.message}]}

		return data


def print_table(tablefmt, data_dict={}, record=None):

	"""
	returns colored table output
	"""
	headers = []
	table = []

	if not data_dict:
		return click.echo('Invalid data !!!')

	if data_dict['headers']:
		headers = data_dict['headers']

		if not isinstance(headers, list):
			return click.echo('Invalid headers !!!')

		headers = [click.style(str(each_element), bold=True, fg='red') for each_element in headers]

	if data_dict['table_data']:
		table_data = data_dict['table_data']

		if not all(isinstance(each_list, list) for each_list in table_data):
			return click.echo("Invlaid table data !!!")

		table = [[click.style(str(each_element), fg='green') for each_element in each_list] for each_list in table_data]

		return click.echo(tabulate(table, headers, tablefmt=tablefmt))
	click.echo()
	return click.echo("No %s records found for your account" % record)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])