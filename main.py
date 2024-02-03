import json
import os

def config(json_data, output):
    os.makedirs(output, exist_ok=True)
    border_router=["i6","i7","i8","i9"]
    for AS in json_data['autonomous_systems']: 
        
        for router, config in AS['routers'].items():
            
            with open(f"{output}/{router}_startup-config.cfg", 'w') as file:
                file.write("!\n!\n!\n!\n!\nLast configuration change at 17:44:33 UTC Thu Dec 21 2023\n!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\n")
                file.write(f"hostname {router}\n")
                file.write("!\nboot-start-marker\nboot-end-marker\n!\n!\nno aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n!\nno ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n!\nmultilink bundle-name authenticated\n!\n!\nip tcp synwait-time 5\n!\n!\n!\n")
                for interface in config['interfaces']: 
                    file.write(f"interface {interface['interface_id']}\n")
                    file.write(" no ip address\n negotiation full\n")
                    file.write(f" ipv6 address {interface['ip_address']}\n")
                    file.write(f" ipv6 enable\n")

                    if config.get('protocol') == 'RIP':
                        if not ((router == "i6" and interface['interface_id'] == "GigabitEthernet2/0") or (router == "i7" and interface['interface_id'] == "GigabitEthernet1/0")):
                            file.write (f" ipv6 rip fadia enable\n!\n")
                          
                if 'protocol' in config and config['protocol'] == 'OSPF':
                    router_id = config.get('router_id')
                    file.write(f"ipv6 router ospf 1\n")
                    file.write(f" router-id {router_id}\n")
                    file.write(" exit\n")
                    for interface in config['interfaces']:
                        file.write(f"interface {interface['interface_id']}\n")
                        area_id = config.get('area', '0')  # Default to area 0 if not specified
                        file.write(f" ipv6 ospf 1 area {area_id}\n")
                        file.write(" exit\n!\n")
                

                as_number = AS['as_id']
                if 'iBGP' in config:
                    router_id= config.get('router_id')
                    list_neighbors_loopback=AS['neighbors_loopback']
                    file.write(f"router bgp {as_number}\n")
                    file.write(f" bgp router-id {router_id}\n")
                    file.write(" bgp log-neighbor-changes\n no bgp default ipv4-unicast\n")
                    if router in border_router:
                        neighbor=config['iBGP']['non_loopback_neighbor']
                        if as_number==1:
                             file.write(f" neighbor {neighbor} remote-as 2\n")
                        elif as_number==2:
                             file.write(f" neighbor {neighbor} remote-as 1\n")
                        
                    for neighbor in list_neighbors_loopback:
                        if neighbor != config['iBGP']['ipv6_address']:
                            file.write(f" neighbor {neighbor} remote-as {as_number}\n")
                            file.write(f" neighbor {neighbor} update-source Loopback0\n")
                    
                file.write("!\naddress-family ipv6\n")   

                if 'eBGP' in config:
                    conf_ebgp = config['eBGP']
                    networks = conf_ebgp.get('networks')
                    for network in networks:
                        file.write(f"  network {network}\n")

                for neighbor in list_neighbors_loopback:
                    if neighbor != config['iBGP']['ipv6_address']:
                        file.write(f"  neighbor {neighbor} activate\n")
                if router in border_router:
                    neighbor=config['iBGP']['non_loopback_neighbor']  
                    file.write(f"  neighbor {neighbor} activate\n")             
                file.write("exit-address-family\n!\n")

                if config.get('protocol') == 'RIP':
                    file.write("ipv6 router rip fadia\n")
                    file.write(f" redistribute connected\n!\n")

                if config.get('protocol') == 'OSPF':  
                    if router in ['i8','i9']:
                        for interface in config['interfaces']:
                            if 'link_to' in interface and interface['link_to'] in ['i6','i7']:
                                file.write('ipv6 router ospf 1\n')
                                file.write(f' router-id {router_id}\n')
                                file.write(f' passive-interface {interface["interface_id"]}\n!\n')
                    file.write(f"router bgp {as_number}\n")
                    file.write(" address-family ipv6 unicast\n")
                    file.write(" redistribute ospf 1 \n")
                    file.write("exit-address-family\n")
                    file.write("exit\n!\n")


                file.write("!\n")
                file.write("!\ncontrol-plane\n!\n!\nline con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n!\n!\nend")



       



output_directory = './configs'

with open('intent_file_big_network.json', 'r') as file:
    json = json.load(file)


config(json, output_directory)
