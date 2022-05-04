from typing import Optional
from pydantic import BaseModel

class UserAccount(BaseModel):
    not_student_account: Optional[bool] = False
    user_email: Optional[str] = 'useremail@example.com'
    user_password: Optional[str] = 'password'
    
    service_principal: Optional[bool] = False
    subscription_id: Optional[str] = '0x10x01x-0x10-1x0x-110x-x0110xx011x0'
    client_id: Optional[str] = '0287381x-0t1d-1x0y-1y0x-xy210yz001x0'
    client_secret: Optional[str] = 'YBshj1826bsBusJsbsk91m'
    tenant_id: Optional[str] = '2yzx001x-0x10-1yzx-221x-x0110x2837x0'


class ResourceGroup(BaseModel):
    name: str
    location: str = 'East US'


class SecurityGroup(BaseModel):
    name: str
    rg: str
    rule_name: Optional[str] = 'PermitInboundWEBandSSH'
    rule_priority_list: Optional[list] = ['100','110','120']
    rule_dest_port_range_list: Optional[list] = ['22','80','443']
    rule_direction: str = 'Inbound'
    rule_access: str = 'Allow'
    rule_protocol: Optional[str] = 'Tcp'
    rule_source_port_range: Optional[str] = '*'
    rule_source_address_prefix: Optional[str] = '*'
    rule_dest_address_prefix: Optional[str] = '*'


class VirtualNetwork(BaseModel):
    name: str
    rg: str
    cidr_block: str = '10.0.0.0/16'
    dns_servers: Optional[list] = None


class Subnet(BaseModel):
    name: str
    vnet: str
    cidrblock: str = '10.0.1.0/24'
    resource_group: str = 'ExampleRG'


class NatGateway(BaseModel):
    name: str
    resource_group: str


class PublicKey(BaseModel):
    key_name: str = "ExamplePublicKey"
    public_key: str = 'ssh-rsa haNsak192s-anomad9267382nsjkn...'


class WindowsVirtualMachine(BaseModel):
    name: str
    rg: str
    nsg: Optional[str] = "ExampleSG"
    subnet: str = 'ExampleSubnet'
    size: Optional[str] = 'Standard_DS1_v2'
    username: Optional[str] = 'rootuser'
    password: Optional[str] = '********'
    hostname: Optional[str] = 'azurevm'
    nic: Optional[str] = 'mynic'
    os_disk_name: Optional[str] = 'osdisk'
    os_caching: Optional[str] = 'ReadWrite'
    storage_account_type: Optional[str] = 'Standard_LRS'
    image: Optional[list] = ['MicrosoftWindowsServer', 'WindowsServer', '2016-Datacenter', 'latest']


class LinuxVirtualMachine(BaseModel):
    name: str
    rg: str
    nsg: Optional[str] = "ExampleSG"
    subnet: str = 'ExampleSubnet'
    public_key: Optional[str] = 'ExamplePublicKey'
    size: Optional[str] = 'Standard_DS1_v2'
    username: Optional[str] = 'rootuser'
    password: Optional[str] = '********'
    hostname: Optional[str] = 'azurevm'
    nic: Optional[str] = 'mynic'
    os_disk_name: Optional[str] = 'osdisk'
    os_caching: Optional[str] = 'ReadWrite'
    storage_account_type: Optional[str] = 'Standard_LRS'
    image: Optional[list] = ['Canonical', '0001-com-ubuntu-server-focal', '20_04-lts-gen2', 'latest']
    custom_data: Optional[str] = None

