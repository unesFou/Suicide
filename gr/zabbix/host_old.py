# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import Warning

import requests
import json
from datetime import datetime

zabbix_url = 'http://10.102.0.116:8080/api_jsonrpc.php'
username = 'CNE-JOUNHI'
password = 'sct@2024'
service_name='State of service "Intel(P)" (Intel(P) Graphics Command Center Service)'

# Authenticate and get the auth token
def get_auth_token():
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": username,
            "password": password
        },
        "id": 1
    }

    headers = {
        'Content-Type': 'application/json-rpc'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()
    
    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to authenticate: {result}")
    
def get_all_hosts(auth_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name","status"],
            "selectInterfaces": ["ip"]
        },
        "id": 2,
        "auth": auth_token
    }

    headers = {
        'Content-Type': 'application/json-rpc'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()
    
    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to get hosts: {result}")
 
def get_host_status_by_hostid(auth_token, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "name", "status"],
            "hostids": hostid
        },
        "auth": auth_token,
        "id": 2
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result and result['result']:
        host_info = result['result'][0]  # Assuming only one host is returned
        host_status = host_info['status']
        return host_status
    else:
        raise Exception(f"Failed to get host status: {result}")

def get_ping_status_by_hostid(auth_token, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": "extend",
            "search": {
                "key_": "icmpping"
            },
            "hostids": hostid
        },
        "auth": auth_token,
        "id": 1
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result and result['result']:
        if result['result'][0]['status'] != '0':
            print(1)
        host_info = result['result'][0]  # Assuming only one host is returned
        host_status = host_info['status']
        return host_status
    else:
        raise Exception(f"Failed to get host status: {result}")
    
def get_host_groups(auth_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "hostgroup.get",
        "params": {
            "output": ["groupid", "name"]
        },
        "auth": auth_token,
        "id": 2
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to get host groups: {result}")
 
def get_items_by_service(auth_token, hostid, service_name):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemid", "name", "lastvalue"],
            "hostids": hostid,
            "search": {
                "name": service_name
            },
            "sortfield": "name"
        },
        "id": 3,
        "auth": auth_token
    }
    
    headers = {
        'Content-Type': 'application/json-rpc'
    }
    
    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()
    
    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to get items: {result}")
    
def get_hosts_by_group(auth_token, groupid):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "name", "status"],
            "groupids": groupid,
            "selectInterfaces": ["ip"]
        },
        "auth": auth_token,
        "id": 3
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to get hosts: {result}")   

def get_ping_status(auth_token, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemid", "name", "lastvalue"],
            "hostids": hostid,
            "search": {
                "key_": "icmpping"
            },
            "sortfield": "name"
        },
        "auth": auth_token,
        "id": 3
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result and result['result']:
        item_info = result['result'][0]  # Assuming only one item is returned
        ping_status = item_info['lastvalue']
        return ping_status
    else:
        raise Exception(f"Failed to get ping status: {result}")
  
def get_scripts(auth_token):
    payload = {
        "jsonrpc": "2.0",
        "method": "script.get",
        "params": {
            "output": "extend"
        },
        "auth": auth_token,
        "id": 2
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to get scripts: {result}")
   
def execute_script(auth_token, scriptid, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "script.execute",
        "params": {
            "scriptid": scriptid,
            "hostid": hostid
        },
        "auth": auth_token,
        "id": 2
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to execute script: {result}") 
   

def create_restart_action(auth_token, hostid, service_name):

    payload = {
        "jsonrpc": "2.0",
        "method": "action.create",
        "params": {
            "name": f"Restart {service_name} on {hostid}",
            "eventsource": 0,
            "status": 0,
            "esc_period": 60,  # Change to 60 seconds (1 minute)
            "evaltype": 0,  # And change to 0
            "conditions": [
                {
                    "conditiontype": 16,  # Trigger severity
                    "operator": 5,  # More than or equals
                    "value": 4  # Severity: Disaster
                },
                {
                    "conditiontype": 24,  # Trigger value
                    "operator": 0,  # Equals
                    "value": service_name  # Service name
                }
            ],
            "operations": [
                {
                    "operationtype": 1,
                    "opcommand_hst": [
                        {
                            "hostid": hostid
                        }
                    ],
                    "opcommand": {
                        "type": 0,
                        "command": f"systemctl restart {service_name}",
                        "execute_on": 0
                    }
                }
            ]
        },
        "auth": auth_token,
        "id": 1
    }

    headers = {
        'Content-Type': 'application/json-rpc'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to create restart action: {result}")
    
def get_start_action(auth_token, hostid, service_name):
    payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "selectOperations": "extend",
            # "filter": {
                # "name": f"Start {service_name} on {hostid}"
            # }
        },
        "auth": auth_token,
        "id": 4
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result and result['result']:
        return result['result'][0]  # Assuming only one action is returned
    else:
        return None
     
def get_restart_action(auth_token, hostid, service_name):
    payload = {
        "jsonrpc": "2.0",
        "method": "action.get",
        "params": {
            "output": "extend",
            "selectOperations": "extend",
            "filter": {
                "name": f"Restart {service_name} on {hostid}"
            }
        },
        "auth": auth_token,
        "id": 4
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result and result['result']:
        return result['result'][0]  # Assuming only one action is returned
    else:
        return None
     
def execute_restart_action(auth_token, action_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "action.execute",
        "params": {
            "actionid": action_id
        },
        "auth": auth_token,
        "id": 5
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(zabbix_url, headers=headers, data=json.dumps(payload))
    result = response.json()

    if 'result' in result:
        return result['result']
    else:
        raise Exception(f"Failed to trigger the action: {result}")
   
   
    
class aa_zabbix_host(models.Model):# models.TransientModel
    _name = 'aa.zabbix_host'
    _rec_name='name'
    _order = 'sequence'
    
    name = fields.Char("Name",required=True)
    camera_id = fields.Many2one('aa.camera',"Camera")
    hostid = fields.Char("host ID",required=True)
    ip = fields.Char("Addresse IP",required=True)
    active = fields.Boolean("Active",default=True)
    
    sequence = fields.Integer('Sequence')

    """ get and create all hosts get camera_id by host_ip"""
    """ cron to get yolo_service state (ex: every 2 minutes) if it's off end current notif and create notif with type service_down """
    
    @api.model
    def cron_get_zabbix_info(self):
        self.get_zabbix_info()
    
    def get_zabbix_info(self):
        auth_token = get_auth_token()
        host_ids = self.search([("camera_id","!=",False)])
        for host_id in host_ids:
            # if host_id.id == 135:
            #     print(1)
            if  host_id.name == "BT ZNATA":
                print(1)
            zabbix_state=''
            # res = get_host_status_by_hostid(auth_token,host_id.hostid)
            res=get_ping_status(auth_token, host_id.hostid)
            # scripts = get_scripts(auth_token)
            
            if res != '0':
                zabbix_state='ping_down'
                print("this case is pc down")
            else:
                items = get_items_by_service(auth_token, host_id.hostid,service_name)
                # it = get_items_by_service(auth_token, host_id.hostid,"icmpping")
                # it = get_ping_status_by_hostid(auth_token, host_id.hostid)
                try:
                    if items[0]['lastvalue'] != '0':
                        zabbix_state='service_down'
                        """run script to start this service"""
                        execution_result = execute_script(auth_token, '4', host_id.hostid)
                        # action = get_restart_action(auth_token, host_id.hostid, service_name)
                        # action = get_start_action(auth_token, host_id.hostid, service_name)
                except :
                    # with open("zabbix_log.txt", 'a') as file:
                        # file.write(f"cant get the service from hostid={host_id.hostid} ({host_id.name}) \n")
                    print(f"cant get the service from hostid={host_id.hostid} ({host_id.name}) ")
            if  zabbix_state:
                not_ids = self.env['aa.notification'].search([('camera_id','=',host_id.camera_id.id),('date_e','=',False)])
                for not_id  in not_ids:
                    not_id.write({'date_e': datetime.utcnow(),
                                  'descr':f"closed by zabbix : {zabbix_state}"})
                    
        print("end________cron_get_zabbix_info")
        # raise Warning("not yet created")
        
    @api.model
    def cron_stop_all_zabbix_services(self):
        self.stop_all_zabbix_services()
        
    def stop_all_zabbix_services(self):
        auth_token = get_auth_token()
        host_ids = self.search([])
        # host_ids = self.search([("camera_id","!=",False)])
        for host_id in host_ids:
            res=get_ping_status(auth_token, host_id.hostid)
            if res != '0':
                zabbix_state='ping_down'
                print("this case is pc down for %s "%host_id.name)
            else:
                try:
                    execution_result = execute_script(auth_token, '6', host_id.hostid)
                    print(execution_result)
                except :
                    # with open("zabbix_log.txt", 'a') as file:
                        # file.write(f"cant get the service from hostid={host_id.hostid} ({host_id.name}) \n")
                    print(f"cant get the service from hostid={host_id.hostid} ({host_id.name}) ")
                    
    def get_and_create_zabbix_hosts(self):

        auth_token = get_auth_token()
        """ get CAMERA-AI host_group"""
        groupId=''
        host_groups = get_host_groups(auth_token)
        for host_group in host_groups:
            if host_group['name']=='CAMERA-AI':
                groupId=host_group['groupid']
        # hosts = get_all_hosts(auth_token)
        if not groupId:
            raise Warning("hhh")
        
        """ get hosts by CAMERA-AI host_group"""
        hosts = get_hosts_by_group(auth_token,groupId)
        for host in hosts:
            host_ip = host['interfaces'][0]['ip']
            vals={'name':host['host'],
                  'hostid':host['hostid'],
                  'ip':host_ip
                  }
            parent_ip = '.'.join(host_ip.split('.')[:3])
            cam_ids = self.camera_id.search([('ip_nvr','ilike',parent_ip)])
            if cam_ids:
                print(1)
            cam_id=cam_ids.filtered(lambda x: '.'.join(x.ip_nvr.split('.')[:3]) == parent_ip)
            if cam_id:
                vals['camera_id']=cam_id.id
            host_id = self.search([('hostid','=',host['hostid'])])
            if not host_id :
                host_id=self.create(vals)
            else:
                self.write(vals)
            if cam_id:
                cam_id.write({'host_id':host_id.id})
                
        print("end_______get_and_create_zabbix_hosts")
            # print(1)
        # print("get_and_create_zabbix_hosts")