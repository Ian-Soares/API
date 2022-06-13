from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
    username: Optional[str] = "username"


class Project(BaseModel):
    username: Optional[str] = "username"
    project_name: Optional[str] = "project"


class UserAccount(BaseModel):
    user_email: Optional[str] = 'useremail@example.com'
    user_password: Optional[str] = 'password'
    
    subscription_id: Optional[str] = '0x10x01x-0x10-1x0x-110x-x0110xx011x0'
    client_id: Optional[str] = '0287381x-0t1d-1x0y-1y0x-xy210yz001x0'
    client_secret: Optional[str] = 'YBshj1826bsBusJsbsk91m'
    tenant_id: Optional[str] = '2yzx001x-0x10-1yzx-221x-x0110x2837x0'


class ResourceGroup(BaseModel):
    name: str
    location: str = 'East US'


class SecurityGroup(BaseModel):
    name: str = 'ExampleSG'
    rg: str = 'ExampleRG'
    rule_name: Optional[str] = 'PermitPorts'
    rule_priority_list: Optional[str] = '100,110,120'
    rule_dest_port_range_list: Optional[str] = '22,88,443'
    rule_direction: str = 'Inbound'
    rule_access: str = 'Allow'
    rule_protocol: Optional[str] = 'Tcp'
    rule_source_port_range: Optional[str] = '*'
    rule_source_address_prefix: Optional[str] = '*'
    rule_dest_address_prefix: Optional[str] = '*'


class VirtualNetwork(BaseModel):
    name: str = 'VNET-DnD'
    rg: str = 'ExampleRG'
    cidr_block: str = '10.0.0.0/16'


class Subnet(BaseModel):
    name: str = 'ExampleSubnet'
    vnet: str = 'VNET-DnD'
    cidrblock: str = '10.0.1.0/24'
    resource_group: str = 'ExampleRG'


class NatGateway(BaseModel):
    name: str
    resource_group: str


class WindowsVirtualMachine(BaseModel):
    name: str = 'WINSRV'
    rg: str = 'ExampleRG'
    nsg: Optional[str] = 'ExampleSG'
    subnet: str = 'ExampleSubnet'
    size: Optional[str] = 'Standard_DS1_v2'
    username: Optional[str] = 'rootuser'
    password: Optional[str] = '********'
    hostname: Optional[str] = 'azurevm'
    image: Optional[list] = ['MicrosoftWindowsServer', 'WindowsServer', '2016-Datacenter', 'latest']


class LinuxVirtualMachine(BaseModel):
    name: str = 'LNXSRV'
    rg: str = 'ExampleRG'
    nsg: Optional[str] = "ExampleSG"
    subnet: str = 'ExampleSubnet'
    size: Optional[str] = 'Standard_DS1_v2'
    username: Optional[str] = 'rootuser'
    image: Optional[list] = ['Canonical', '0001-com-ubuntu-server-focal', '20_04-lts-gen2', 'latest']
