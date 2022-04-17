from fastapi import FastAPI
import os, subprocess, shutil
from classes import *
from functions import *
from provider import provider_block_script

app = FastAPI(title="Draw and Deploy API")


@app.post('/api/create_user')
def create_user(username):
    if not os.path.exists(f'/terraform_api_dirs/{username}/'):
        os.makedirs(f'/terraform_api_dirs/{username}/init_user/')
        os.system(f'touch /terraform_api_dirs/{username}/init_user/init.txt')
        os.system(f'aws s3 cp /terraform_api_dirs/{username}/ s3://arquivosterraform/{username}/ --recursive')
        return {"Status": "User created!"}
    else:
        return {"Error": "User already exists!"}


@app.delete('/api/delete_user')
def delete_user(username):
    shutil.rmtree(f'/terraform_api_dirs/{username}')
    os.system(f'aws s3 rm s3://arquivosterraform/{username}/ --recursive')
    return {"Status": "User deleted!"}


@app.get('/api/get_s3_users')
def get_s3_users():
    users_list = str(subprocess.check_output('aws s3 ls s3://arquivosterraform', shell=True)).split('PRE ')
    for item in range(len(users_list)):
        users_list[item] = users_list[item].strip().replace('\\n', '').replace("'", "").replace('/', '')
    users_list.pop(0)
    return users_list


@app.get('/api/get_s3_projects/{username}')
def get_s3_projects(username):
    projects_list = str(subprocess.check_output(f'aws s3 ls s3://arquivosterraform/{username}/', shell=True)).split('PRE ')
    for item in range(len(projects_list)):
        projects_list[item] = projects_list[item].strip().replace('\\n', '').replace("'", "").replace('/', '')      
    projects_list.pop(0)
    projects_list.remove('init_user')
    return projects_list


@app.post('/api/create_project/{username}/{project_name}')
def create_new_project(username, project_name):
    global project_path, user, project
    user, project = username, project_name
    if project_name != "init_project":
        if not os.path.exists(f'/terraform_api_dirs/{user}/{user}/'):
            project_path = f'/terraform_api_dirs/{username}/{project_name}'
            os.makedirs(f'{project_path}/init_project/')
            os.system(f'touch /terraform_api_dirs/{username}/{project_name}/init_project/init.txt')
            os.system(f'aws s3 cp {project_path}/ s3://arquivosterraform/{username}/{project}/ --recursive --exclude ".terraform*"')
            return {"Status": "Project created!"}
        else:
            return {"Error": "Project already exists!"}
    else:
        return {"Error": "You cannot create an project named 'init_project'"}


@app.delete('/api/delete_project/{username}/{project_name}')
def delete_existing_project(username, project_name):
    shutil.rmtree(f'/terraform_api_dirs/{username}/{project_name}')
    os.system(f'aws s3 rm s3://arquivosterraform/{username}/{project_name} --recursive')
    return {"Status": "Project deleted!"}


@app.put('/api/use_existing_local_project/{username}/{project_name}')
def use_existing_project(username, project_name):
    global project_path, user, project
    user, project = username, project_name
    project_path = f'/terraform_api_dirs/{username}/{project_name}'
    return {"Status": "Done!"}


@app.post('/api/pull_existing_project')
def pull_existing_project_in_s3(username, project):
    os.system(f'aws s3 sync s3://arquivosterraform/{username}/{project}/ /terraform_api_dirs/{username}/{project}/ --exclude "init_project"')
    return {"Status": "File pulled from S3 Bucket!"}


@app.post('/api/account_credentials')
def set_account_credentials(useracc: UserAccount):
    if(useracc.not_student_account):
        os.system(f'az login -u {useracc.user_email} -p {useracc.user_password}')
        account_settings = provider_block_script(service_principal = False)
    elif(useracc.service_principal):
        account_settings = provider_block_script(useracc.subscription_id, useracc.client_id, useracc.client_secret, useracc.tenant_id, service_principal=True)
    else:
        account_settings = provider_block_script()
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(account_settings)
    return {"Status": "Account authenticated!"}


@app.delete('/api/clear_script')
def delete_script():
    try:
        os.remove(f'{project_path}/main.tf')
        os.remove(f'{project_path}/terraform.tfstate')
    except:
        pass
    return {"Status": "Script deleted!"}


@app.post('/api/resource_group')
def create_resource_group(rg: ResourceGroup):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(resource_group_script(rg))
    return {"Status": "Resource Group created!"}


@app.post('/api/virtual_network')
def create_virtual_network(vnet: VirtualNetwork):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(virtual_network_script(vnet))
    return {"Status": "Virtual Network created!"}


@app.post('/api/subnet')
def create_subnet(subnet: Subnet):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(vnet_subnets_script(subnet))
    return {"Status": "Subnet created"}


@app.post('/api/security_group')
def create_security_group(sg: SecurityGroup):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(security_group_script(sg))
    return {"Status": "Security Group created!"}


@app.post('/api/ssh_public_key')
def set_ssh_public_key(key: PublicKey):
    if not os.path.exists(f'/terraform_api_dirs/{user}/ssh-keys/'):
        os.makedirs(f'/terraform_api_dirs/{user}/ssh_keys/')
    ssh_file = open(f'/terraform_api_dirs/{user}/ssh_keys/key_{key.key_name}', 'w+')
    ssh_file.write(key.public_key)
    return {"Status": "SSH Public Key set!"}


@app.post('/api/nat_gateway')
def create_nat_gateway(nat_gtw: NatGateway):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(nat_gateway_script(nat_gtw))
    return {"Status": "NAT Gateway created!"}


@app.post('/api/virtual_machine')
def create_virtual_machine(vm: VirtualMachine):
    terraform_file = open(f'{project_path}/main.tf', 'a+')
    terraform_file.write(virtual_machine_script(vm, user))
    return {"Status": "Virtual Machine created!"}


@app.post('/api/upload_file_to_s3/{username}/{project}')
def upload_file_s3(username, project):
    os.system(f'aws s3 cp {project_path}/ s3://arquivosterraform/{username}/{project} --recursive --exclude ".terraform*"')
    return {"Status": "Your file was uploaded!"}


@app.post('/api/apply')
def apply_infrastructure():
    os.chdir(f'{project_path}')
    os.system('terraform init')
    os.system('terraform apply --auto-approve')
    return {"Status": "Infrastructure deployed!"}


@app.delete('/api/destroy')
def destroy_infrastructure():
    os.chdir(f'{project_path}')
    os.system('terraform apply -destroy --auto-approve')
    return {"Status": "Infrasctructure and files destroyed"}
