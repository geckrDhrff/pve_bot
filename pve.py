import requests

# self-sign CA warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Pve_api(object):

    def __init__(self, ip, username = None, password = None, port = '8006'):
        self.ip = ip
        self.username = username
        self.password = password
        self.port = port
        self.ticket = None


    def get_ticket(self):
        path = '/api2/json/access/ticket'
        url = 'https://' + self.ip + ':' + self.port + path
        r = requests.post(url=url, json={"username": self.username, "password": self.password}, verify=False)
        self.ticket = r.json() # dict rather than string
        return r.json()

    def ticket_node_list(self):
        path = '/api2/json/nodes'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'CSRFPreventionToken': self.ticket['data']['CSRFPreventionToken'], 'Cookie': 'PVEAuthCookie=' + self.ticket['data']['ticket']}
        r = requests.get(url=url, headers=headers, verify=False)
        return r.json()
    
    def pve_status(self):
        path = f'/api2/json/nodes/pve/status'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'CSRFPreventionToken': self.ticket['data']['CSRFPreventionToken'], 'Cookie': 'PVEAuthCookie=' + self.ticket['data']['ticket']}
        r = requests.get(url=url, headers=headers, verify=False)
        return r.json()

    def ticket_vm_list(self, node):
        path = f'/api2/json/nodes/{node}/qemu'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'CSRFPreventionToken': self.ticket['data']['CSRFPreventionToken'], 'Cookie': 'PVEAuthCookie=' + self.ticket['data']['ticket']}
        r = requests.get(url=url, headers=headers, verify=False)
        return r.json()

    def ticket_vm_current(self, node, vmid):
        path = f'/api2/json/nodes/{node}/qemu/{vmid}/status/current'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'CSRFPreventionToken': self.ticket['data']['CSRFPreventionToken'], 'Cookie': 'PVEAuthCookie=' + self.ticket['data']['ticket']}
        r = requests.get(url=url, headers=headers, verify=False)
        return r.json()

    def ticket_vm_start(self, node, vmid):
        path = f'/api2/json/nodes/{node}/qemu/{vmid}/status/start'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'CSRFPreventionToken': self.ticket['data']['CSRFPreventionToken'], 'Cookie': 'PVEAuthCookie=' + self.ticket['data']['ticket']}
        r = requests.post(url=url, headers=headers, verify=False)
        return r.json()

    def token_vm_stop(self, node, vmid, token):
        path = f'/api2/json/nodes/{node}/qemu/{vmid}/status/stop'
        url = 'https://' + self.ip + ':' + self.port + path
        headers = {'Authorization': 'PVEAPIToken=' + token}
        r = requests.post(url=url, headers=headers, verify=False)
        return r.json()
    