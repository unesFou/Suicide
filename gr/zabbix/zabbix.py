
# hostnames = ["BT AIN DORREJ"]

import requests
import json

# Zabbix API URL and credentials
zabbix_url = 'http://10.102.0.116:8080/api_jsonrpc.php'
username = 'CNE-JOUNHI'
password = 'sct@2024'

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

# Get the list of hosts with additional details
def get_hosts(auth_token):
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

def get_host_state_by_hostid(auth_token, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "status"],
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
        raise Exception(f"Failed to get host state: {result}")


def get_hosts_state_by_name(auth_token, hostnames):
    payload = {
        "jsonrpc": "2.0",
        "method": "host.get",
        "params": {
            "output": ["hostid", "host", "status"],
            "filter": {
                "host": hostnames
            }
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
        raise Exception(f"Failed to get host state: {result}")
   
def get_host_status(auth_token, hostid):
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
     
# Get items monitoring a specific host
def get_items(auth_token, hostid):
    payload = {
        "jsonrpc": "2.0",
        "method": "item.get",
        "params": {
            "output": ["itemid", "name", "lastvalue"],
            "hostids": hostid,
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
    
# Main function
def main():
    try:
        # Get authentication token
        auth_token = get_auth_token()
        print("Authentication successful. Auth token:", auth_token)
        
        service_name='State of service "Intel(P)" (Intel(P) Graphics Command Center Service)'
        # Get the list of hosts
        hosts = get_hosts(auth_token)
        # Print the list of hosts with IP addresses
        print("Supervised Services:")
        for host in hosts:
            ip_addresses = ', '.join(interface['ip'] for interface in host['interfaces'])
            print(f"### Host ID: {host['hostid']}, Host: {host['host']}, Name: {host['name']}, IP: {ip_addresses}, status: {host['status']}")
            if host['status'] != "0":
                print(1)
        
        
            # items = get_items(auth_token, host['hostid'])
            items = get_items_by_service(auth_token, host['hostid'],service_name)
            
            # Print the supervised service names
            for item in items:
                # print(f"Service Item: {item['name']} (Last Value: {item['lastvalue']})")
                print(f"Service Item : {item}")
    
            
        # host_names=[line['name'] for line in hosts ]
        hostids=[line['hostid'] for line in hosts ]
        for hosts_state in get_host_state_by_hostid(auth_token,hostids):
            print(hosts_state)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

