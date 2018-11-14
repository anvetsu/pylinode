# -*- coding: utf-8 -*-

import time
import click
from urls import *
from base_request import Linode, print_table, CONTEXT_SETTINGS

SIZES = {'1':20480, '2':30720, '3': 48, '4':96, '5': 192, '6':384, '7':768, '8':1152, '9':1536}
DATACENTERS = {'2': 'Dallas, TX, USA', '3': 'Fremont, CA, USA', '4': 'Atlanta, GA, USA', '6': 'Newark, NJ, USA', '7': 'London, England, UK', '8': 'Tokyo, JP', '9': 'Singapore, SG', '10': 'Frankfurt, DE'}
PLANS = {'1': 'Linode 1024', '2': 'Linode 2048', '4': 'Linode 4096', '6': 'Linode 8192', '7': 'Linode 16384', '8': 'Linode 32768', '9': 'Linode 49152', '10': 'Linode 65536', '12': 'Linode 98304'}

@click.group()
def linode_create_group():
    """
    account command group
    """
    pass


def validate(dic, option_list):
    """
    linode create command validation
    """
    for option in option_list:
        if not dic[option]:
            raise click.UsageError('required option %s is missing' %(option))

    return True

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--datacenter', '-d', type=click.Choice(['2','3','4','6','7','8','9','10']), help='datacenter id to create linode', metavar='<default=2>', default='9')
@click.option('--plan', '-p', type=click.Choice(['1', '2','4','6','7','8','9','10','12']), help='plan id to create linode', metavar='<default=1>', default='1')
@click.option('--os', '-o', type=click.Choice(['142','129','130','140','141','137','135','117','124','139','138','60','127','78','122','134','118','120','87','126','133','86']), help='distribution id to create linode', metavar='<default=140>', default='140')
@click.option('--clone', '-c', type=int, help='create new linode from given linode id')
@click.option('--image', '-i', type=int, help='create new linode disk from given image id')
@click.option('--label', '-l', type=str, help='linode disk label')
@click.option('--rootpass', '-r', type=str, help='root password for linode')
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.pass_context
def create(ctx, datacenter, plan, os, clone, image, label, rootpass, token, proxy):
    """
    create new linode
    """
    if (not label and not rootpass):
        return click.echo(ctx.get_help())

    option_list = ['label', 'rootpass']

    if validate(ctx.params, option_list):
        method = 'GET'
        params = {'DATACENTERID': datacenter, 'PLANID': plan}
        url = LINODE_CREATE
        msg = 'Creating Linode in datacenter %s with plan %s' %(DATACENTERS[datacenter], PLANS[plan])
        click.echo(msg)
        result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
        if result['ERRORARRAY']:
            msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
            return click.echo('Error: %s' %(msg))
        else:
            linode_id = result['DATA']['LinodeID']

        if image:
            msg = 'Creating disk for linode %d from image %d' % (linode_id, image)
            click.echo(msg)
            size = SIZES[plan] - 512
            params = {'LINODEID': linode_id, 'IMAGEID': image, 'LABEL': label, 'ROOTPASS': rootpass , 'SIZE': size}
            url = LINODE_DISK_FROM_IMAGE
            result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
            if result['ERRORARRAY']:
                msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
                return click.echo('Error: %s' %(msg))
            else:
                main_disk_id = result['DATA']['DISKID']
                main_job_id = result['DATA']['JOBID']

            job_done = False
            while not job_done:
                url = JOB_LIST
                params = {'LINODEID': linode_id, 'JOBID': main_job_id}
                result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
                if result['DATA'][0]['HOST_SUCCESS']:
                    job_done = True
                else:
                    time.sleep(3)
        elif clone:
            msg = 'Cloning linode from linode %d' % (clone)
            click.echo(msg)
            size = SIZES[plan] - 512
            params = {'LINODEID': clone, 'DATECENTERID': datacenter, 'PLANID': plan, 'LABEL': label, 'ROOTPASS': rootpass,
                      'SIZE': size}
            url = LINODE_CLONE
            result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
            print 'Result =>',result
            if result['ERRORARRAY']:
                msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
                return click.echo('Error: %s' %(msg))
            else:
                main_job_id = result['DATA']['JOBID']

            job_done = False
            while not job_done:
                url = JOB_LIST
                params = {'LINODEID': linode_id, 'JOBID': main_job_id}
                result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
                if result['DATA'][0]['HOST_SUCCESS']:
                    job_done = True
                else:
                    time.sleep(3)           
            
        else:
            msg = 'Creating disk for linode %d' % (linode_id)
            click.echo(msg)
            size = SIZES[plan] - 512
            params = {'LINODEID': linode_id, 'FROMDISTRIBUTIONID': os, 'LABEL': label, 'ROOTPASS': rootpass, 'SIZE': size, 'TYPE': 'ext4'}
            url = LINODE_DISK_CREATE
            result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
            if result['ERRORARRAY']:
                msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
                return click.echo('Error: %s' %(msg))
            else:
                main_disk_id = result['DATA']['DiskID']
                main_job_id = result['DATA']['JobID']

            job_done = False
            while not job_done:
                url = JOB_LIST
                params = {'LINODEID': linode_id, 'JOBID': main_job_id}
                result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
                if result['DATA'][0]['HOST_SUCCESS']:
                    job_done = True
                else:
                    time.sleep(3)

        msg = 'Creating swap disk for linode %d' %(linode_id)
        click.echo(msg)
        size = 256
        swap_label ='swap'
        params = {'LINODEID': linode_id, 'LABEL': swap_label, 'SIZE': size, 'TYPE': 'swap'}
        url = LINODE_DISK_CREATE
        result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
        if result['ERRORARRAY']:
            msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
            return click.echo('Error: %s' %(msg))
        else:
            swap_disk_id = result['DATA']['DiskID']
            swap_job_id = result['DATA']['JobID']

        job_done = False
        while not job_done:
            url = JOB_LIST
            params = {'LINODEID': linode_id, 'JOBID': swap_job_id}
            result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
            if result['DATA'][0]['HOST_SUCCESS']:
                job_done = True
            else:
                time.sleep(3)

        msg = 'Creating config for linode %d' %(linode_id)
        click.echo(msg)
        config_label = 'label for ',linode_id
        url = LINODE_CREATE_CONFIG
        disk_list = '{0},{1}'.format(main_disk_id,swap_disk_id)
        params = {'LINODEID': linode_id, 'KERNELID': 138, 'LABEL': config_label, 'DISKLIST': disk_list}
        result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
        if result['ERRORARRAY']:
            msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
            return click.echo('Error: %s' %(msg))
        else:
            config_id = result['DATA']['ConfigID']

        msg = 'Booting linode %d' %(linode_id)
        click.echo(msg)
        url = LINODE_BOOT
        params = {'LINODEID': linode_id, 'CONFIGID': config_id}
        result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
        if result['ERRORARRAY']:
            msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
            return click.echo('Error: %s' %(msg))
        else:
            boot_job_id = result['DATA']['JobID']

        job_done = False
        while not job_done:
            url = JOB_LIST
            params = {'LINODEID': linode_id, 'JOBID': boot_job_id}
            result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
            if result['DATA'][0]['HOST_SUCCESS']:
                job_done = True
            else:
                time.sleep(3)

        url = LINODE_IP
        params = {'LINODEID': linode_id}
        result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
        if result['ERRORARRAY']:
            msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
            return click.echo('Error: %s' %(msg))
        else:
            suc_msg = 'Your linode %d created successfully' %(linode_id)
            click.echo(suc_msg)
            ip_msg = 'Ip Address of this linode is %s' %(result['DATA'][0]['IPADDRESS'])
            click.echo(ip_msg)

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def os(ctx, token, proxy, tablefmt):
    """
    list of linode distributions
    """
    method = 'GET'
    url = AVAIL_DISTRIBUTION
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        record = 'os'
        headers = ['Distribution ID', 'Label']
        table = []
        for each in result['DATA']:
            table.append([each['DISTRIBUTIONID'], each['LABEL']])
        data = {'headers': headers, 'table_data': table}
        print_table(tablefmt, data, record)


@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def plan(ctx, token, proxy, tablefmt):
    """
    list of linode plans
    """
    method = 'GET'
    url = AVAIL_PLANS
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        record = 'plan'
        headers = ['Plan ID', 'Label', 'Ram', 'Cores', 'Disk', 'Price']
        table = []
        for each in result['DATA']:
            table.append([each['PLANID'], each['LABEL'], each['RAM'], each['CORES'], each['DISK'], each['PRICE']])
        data = {'headers': headers, 'table_data': table}
        print_table(tablefmt, data, record)


@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def datacenter(ctx, token, proxy, tablefmt):
    """
    list of linode datacenters
    """
    method = 'GET'
    url = AVAIL_DATACENTER
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        record = 'datacenter'
        headers = ['Data Center ID', 'Location']
        table = []
        for each in result['DATA']:
            table.append([each['DATACENTERID'], each['LOCATION']])
        data = {'headers': headers, 'table_data': table}
        print_table(tablefmt, data, record)


@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def image(ctx, token, proxy, tablefmt):
    """
    list of linode user's images
    """
    method = 'GET'
    url = AVAIL_IMAGE
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        record = 'image'
        headers = ['Image ID', 'Status', 'Label', 'FS Type']
        table = []
        for each in result['DATA']:
            table.append([each['IMAGEID'], each['STATUS'], each['LABEL'], each['FS_TYPE']])
        data = {'headers': headers, 'table_data': table}
        print_table(tablefmt, data, record)


@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--linode', '-l', type=str, help='delete linode', metavar='<linode id>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def delete(ctx, linode, token, proxy, tablefmt):
    """
    delete linode
    """
    if not linode:
        return click.echo(ctx.get_help()) 
    method = 'GET'
    url = DELETE_LINODE
    params = {'LINODEID': linode, 'SKIPCHECKS': True}
    result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        msg = "Linode {0} is deleted.".format(linode)
        click.echo()
        click.echo(msg)

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def list(ctx, token, proxy, tablefmt):
    """
    List linodes
    """

    method = 'GET'
    url = LINODE_LIST
    
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        url = LINODE_IP
        result_ip = Linode.do_request(method, url, token=token, proxy=proxy)
        ip_dict = {}
        
        if result_ip['ERRORARRAY']:
            ip_available = False
        else:
            ip_available = True
            for each in result_ip['DATA']:
                ip_dict[each['LINODEID']] = each['IPADDRESS']
    
        record = 'linode'

        if ip_available:
            headers = ['Id', 'Label', 'IP', 'Group', 'Plan', 'Datacenter']
            table = []
            for each in result['DATA']:
                linode_id = each['LINODEID']
                ip_address = ip_dict[linode_id]
                table.append([linode_id, each['LABEL'], ip_address, each['LPM_DISPLAYGROUP'], each['PLANID'], each['DATACENTERID']])
        else:
            headers = ['Id', 'Label', 'Group', 'Plan', 'Datacenter']
            table = []
            for each in result['DATA']:
                table.append([each['LINODEID'], each['LABEL'], each['LPM_DISPLAYGROUP'], each['PLANID'], each['DATACENTERID']])         
            
        data = {'headers': headers, 'table_data': table}
        print_table(tablefmt, data, record) 
        

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--group', '-g', type=str, help='new group', metavar='<linode group>')
@click.option('--label', '-L', type=str, help='new label', metavar='<linode label>')
@click.option('--linode', '-l', type=str, help='update linode', metavar='<linode id>')
@click.option('--tablefmt', '-f', type=click.Choice(['fancy_grid', 'simple', 'plain', 'grid', 'pipe', 'orgtbl', 'psql', 'rst', 'mediawiki', 'html', 'latex', 'latex_booktabs', 'tsv']), help='output table format', default='fancy_grid', metavar='<format>')
@click.pass_context
def update(ctx, linode, label, group, token, proxy, tablefmt):
    """
    update linode
    """
    if not linode:
        return click.echo(ctx.get_help()) 

    method = 'GET'
    # We need config id for this
    #url = LINODE_GET_CONFIG
    
    # params = {'LINODEID': linode}
    # result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
    #if result['ERRORARRAY']:
    #    msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
    #    click.echo('Error: %s' %(msg))
    #    sys.exit(1)
    #else:
    #    config_id = result['DATA'][0]['ConfigID']
        
    url = LINODE_UPDATE
    # print label, group
    
    params = {'LINODEID': linode, 'Label': label, 'lpm_displayGroup': group}

    # method = 'POST'
    result = Linode.do_request(method, url, params=params, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        msg = "Linode {0} is updated.".format(linode)
        click.echo()
        click.echo(msg)

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--linode', '-l', type=str, help='linode info', metavar='<linode id>')
@click.pass_context
def info(ctx, linode, token, proxy):
    """ Given a linode ID return its label,group,IP and other details """
    

    method = 'GET'
    url = LINODE_LIST
    
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        url = LINODE_IP
        result_ip = Linode.do_request(method, url, token=token, proxy=proxy)
        ip_address = ''
        
        if result_ip['ERRORARRAY']:
            ip_available = False
        else:
            ip_available = True
            for each in result_ip['DATA']:
                if str(each['LINODEID']) == linode:
                    ip_address = each['IPADDRESS']
                    break
    
    for each in result['DATA']:
        linode_id = str(each['LINODEID'])
        if linode_id == linode:
            print 'Label    :',each['LABEL']
            if ip_available:
                print 'IP       :',ip_address
            print 'Group    :',each['LPM_DISPLAYGROUP']
            print 'Plan     :',each['PLANID']
            print 'Location :',each['DATACENTERID']
            break
            

@linode_create_group.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', type=str, help='linode authentication token', metavar='<token>')
@click.option('--proxy', '-x', help='proxy url to be used for this call', metavar='<http://ip:port>')
@click.option('--skip', '-s', type=str, help='linode to skip', metavar='<skip linode>')
@click.option('--group', '-g', type=str, help='linode group name', metavar='<linode group>')
@click.pass_context
def find(ctx, group, skip, token, proxy):
    """ Given a linode group name, print information for all linodes in that group """

    method = 'GET'
    url = LINODE_LIST
    
    result = Linode.do_request(method, url, token=token, proxy=proxy)
    if result['ERRORARRAY']:
        msg = ' '.join([err['ERRORMESSAGE'] for err in result['ERRORARRAY'] ])
        click.echo('Error: %s' %(msg))
    else:
        url = LINODE_IP
        result_ip = Linode.do_request(method, url, token=token, proxy=proxy)
        ip_dict = {}
        
        if result_ip['ERRORARRAY']:
            ip_available = False
        else:
            ip_available = True
            for each in result_ip['DATA']:
                ip_dict[each['LINODEID']] = each['IPADDRESS']

    linode_skip = skip
    template = "%s,%s,%s,%s,%s"
    for each in result['DATA']:
        lgroup = str(each['LPM_DISPLAYGROUP'])
        label = each['LABEL']
        if linode_skip != None and (label.lower() == linode_skip.lower()):
            continue
        
        if lgroup.lower() == group.lower():
            linode_id = each['LINODEID']            
            crtd_dt = each['CREATE_DT']
            tstamp = time.mktime(time.strptime(crtd_dt, "%Y-%m-%d %H:%M:%S.%f"))            
            print template % (ip_dict.get(linode_id), each['DATACENTERID'], each['LINODEID'], tstamp, tstamp)

            
