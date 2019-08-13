# Requires Python3, TextFSM, Netmiko and PyYAML

import yaml
from netmiko import Netmiko

# import username and password
import creds
username = creds.login['username']
password = creds.login['password']

# definitions
switches = [];
interfaces = [];

# open the devices doc
with open('devices.yaml', 'r') as f:
    doc = yaml.load(f)

# import a list of devices
for c in doc['switch'].keys():
    switches.append(doc['switch'][c])

#import list of interfaces
for c in doc['interface'].keys():
    interfaces.append(doc['interface'][c])

for swif, intf in zip (switches, interfaces):

    # connect to switch
    myDevice = {
    'host': swif,
    'username': username,
    'password': password,
    'device_type': 'cisco_ios'
    }
    net_connect = Netmiko(**myDevice)
    net_connect.enable()

    # issue show int status
    shvlan = net_connect.send_command("show interface status", use_textfsm=True)

    # iterate over the list and grab the dict with intf
    for i in shvlan:
        if i['port'] == intf:
            # grab VLAN from dict
            vlan = i['vlan']

    # seperate the VLAN into digits
    splitvlan = list(str(vlan))
    # first digit of the vlan
    netvlan = int(splitvlan[0])
    # second digit of the vlan
    intvlan = int(splitvlan[1])

    # reset number back to 0
    if intvlan == 9:
        intvlan = 0
    # skip 7
    elif intvlan == 6:
        intvlan += 2
    # increment VLAN
    else:
        intvlan += 1

    # combine both integers
    newvlan = str(netvlan) + str(intvlan)

    # send commands
    config_commands = [
    'int '+intf,
    'swi acc vlan '+newvlan
    ]

    net_connect.send_config_set(config_commands)
