from fastapi import FastAPI
import os, subprocess, shutil
from classes import *
from functions import *
from provider import provider_block_script
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Draw and Deploy API")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/api/create_user/')
def create_user(user: User):
    if not os.path.exists(f'/terraform_api_dirs/{user.username}/'):
        os.makedirs(f'/terraform_api_dirs/{user.username}/init_user/')
        os.system(f'touch /terraform_api_dirs/{user.username}/init_user/init.txt')
        os.system(f'aws s3 cp /terraform_api_dirs/{user.username}/ s3://arquivosterraform/{user.username}/ --recursive')
        return {"Status": "User created!"}
    else:
        return {"Error": "User already exists!"}


@app.delete('/api/delete_user/')
def delete_user(user: User):
    try:
        shutil.rmtree(f'/terraform_api_dirs/{user.username}')
    except:
        pass
    os.system(f'aws s3 rm s3://arquivosterraform/{user.username}/ --recursive')
    return {"Status": "User deleted!"}


@app.get('/api/get_users/')
def get_s3_users():
    users_list = str(subprocess.check_output('aws s3 ls s3://arquivosterraform', shell=True)).split('PRE ')
    for item in range(len(users_list)):
        users_list[item] = users_list[item].strip().replace('\\n', '').replace("'", "").replace('/', '')
    users_list.pop(0)
    return users_list


@app.get('/api/get_projects/{username}/')
def get_s3_projects(username):
    projects_list = str(subprocess.check_output(f'aws s3 ls s3://arquivosterraform/{username}/', shell=True)).split('PRE ')
    for item in range(len(projects_list)):
        projects_list[item] = projects_list[item].strip().replace('\\n', '').replace("'", "").replace('/', '')      
    projects_list.pop(0)
    projects_list.remove('init_user')
    try:
        projects_list.remove('ssh_keys')
    except:
        pass
    return projects_list


@app.post('/api/create_project/')
def create_new_project(project: Project):
    project_path = f'/terraform_api_dirs/{project.username}/{project.project_name}'
    if project.project_name != "init_project":
        if not os.path.exists(f'/terraform_api_dirs/{project.username}/{project.project_name}/'):
            os.makedirs(f'{project_path}/init_project/')
            os.system(f'touch /terraform_api_dirs/{project.username}/{project.project_name}/init_project/init.txt')
            os.system(f'aws s3 cp {project_path}/ s3://arquivosterraform/{project.username}/{project.project_name}/ --recursive --exclude ".terraform*"')
            return {"Status": "Project created!"}
        else:
            return {"Error": "Project already exists!"}
    else:
        return {"Error": "You cannot create an project named 'init_project'"}


@app.delete('/api/delete_project/')
def delete_existing_project(project: Project):
    try:
        shutil.rmtree(f'/terraform_api_dirs/{project.username}/{project.project_name}')
    except:
        pass
    os.system(f'aws s3 rm s3://arquivosterraform/{project.username}/{project.project_name} --recursive')
    return {"Status": "Project deleted!"}


@app.put('/api/edit_existing_project/')
def edit_existing_project_in_s3(project: Project):
    os.system(f'aws s3 sync s3://arquivosterraform/{project.username}/{project.project_name}/ /terraform_api_dirs/{project.username}/{project.project_name}/ --exclude "init_project"')
    return {"Status": "File pulled from S3 Bucket!"}


@app.post('/api/account_credentials/')
def set_account_credentials(useracc: UserAccount, project: Project):
    if(useracc.not_student_account):
        os.system(f'az login -u {useracc.user_email} -p {useracc.user_password}')
        account_settings = provider_block_script(service_principal = False)
    elif(useracc.service_principal):
        account_settings = provider_block_script(useracc.subscription_id, useracc.client_id, useracc.client_secret, useracc.tenant_id, service_principal=True)
    else:
        account_settings = provider_block_script()
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(account_settings)
    return {"Status": "Account authenticated!"}


@app.post('/api/resource_group/')
def create_resource_group(rg: ResourceGroup, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(resource_group_script(rg))
    return {"Status": "Resource Group created!"}


@app.post('/api/virtual_network/')
def create_virtual_network(vnet: VirtualNetwork, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(virtual_network_script(vnet))
    return {"Status": "Virtual Network created!"}


@app.post('/api/subnet/')
def create_subnet(subnet: Subnet, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(vnet_subnets_script(subnet))
    return {"Status": "Subnet created"}


@app.post('/api/security_group/')
def create_security_group(sg: SecurityGroup, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(security_group_script(sg))
    return {"Status": "Security Group created!"}


@app.post('/api/use_ssh_public_key/')
def use_ssh_public_key(key: PublicKey, project: Project):
    if not os.path.exists(f'/terraform_api_dirs/{project.username}/ssh-keys/'):
        os.makedirs(f'/terraform_api_dirs/{project.username}/ssh_keys/')
    ssh_file = open(f'/terraform_api_dirs/{project.username}/ssh_keys/{key.key_name}', 'w+')
    ssh_file.write(key.public_key)
    os.system(f'aws s3 cp /terraform_api_dirs/{project.username}/ssh_keys/ s3://arquivosterraform/{project.username}/ssh_keys --recursive"')
    return {"Status": "SSH Public Key set!"}


@app.post('/api/create_ssh_public_key/')
def create_ssh_public_key(key: PublicKey, project: Project):
    if not os.path.exists(f'/terraform_api_dirs/{project.username}/ssh_keys/'):
        os.makedirs(f'/terraform_api_dirs/{project.username}/ssh_keys/')
    os.system(f'ssh-keygen -b 2048 -t rsa -f /terraform_api_dirs/{project.username}/ssh_keys/{key.key_name} -q -N ""')
    os.system(f'aws s3 cp /terraform_api_dirs/{project.username}/ssh_keys/ s3://arquivosterraform/{project.username}/ssh_keys --recursive')
    return {"Status": "SSH Public Key created!"}


@app.post('/api/nat_gateway/')
def create_nat_gateway(nat_gtw: NatGateway, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(nat_gateway_script(nat_gtw))
    return {"Status": "NAT Gateway created!"}


@app.post('/api/windows_virtual_machine/')
def create_virtual_machine(vm: WindowsVirtualMachine, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(windows_virtual_machine_script(vm))
    return {"Status": "Virtual Machine created!"}


@app.post('/api/linux_virtual_machine/')
def create_virtual_machine(vm: LinuxVirtualMachine, project: Project):
    terraform_file = open(f'/terraform_api_dirs/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(linux_virtual_machine_script(vm))
    return {"Status": "Virtual Machine created!"}


@app.post('/api/upload_files_to_s3/')
def upload_file_s3(project: Project):
    os.system(f'aws s3 cp /terraform_api_dirs/{project.username}/{project.project_name}/ s3://arquivosterraform/{project.username}/{project.project_name} --recursive --exclude ".terraform*"')
    return {"Status": "Your file was uploaded!"}


@app.post('/api/apply/')
def apply_infrastructure(project: Project):
    os.chdir(f'/terraform_api_dirs/{project.username}/{project.project_name}')
    os.system('terraform init')
    os.system('terraform apply --auto-approve')
    return {"Status": "Infrastructure deployed!"}


@app.delete('/api/destroy/')
def destroy_infrastructure(project: Project):
    os.chdir(f'/terraform_api_dirs/{project.username}/{project.project_name}/')
    os.system('terraform apply -destroy --auto-approve')
    return {"Status": "Infrasctructure and files destroyed"}
