from fastapi import FastAPI
import os, subprocess, shutil
from classes import *
from functions import *
from provider import provider_block_script
from fastapi.middleware.cors import CORSMiddleware
import boto3

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

session = boto3.Session(profile_name='default')
s3 = session.resource('s3')

bucket = s3.Bucket('drawanddeploy')


@app.post('/api/create_user/')
def create_user(user: User):
    if not os.path.exists(f'/drawanddeploy/{user.username}/'):
        os.makedirs(f'/drawanddeploy/{user.username}/init_user/')
        os.system(f'touch /drawanddeploy/{user.username}/init_user/init.txt')
        os.system(f'aws s3 cp /drawanddeploy/{user.username}/ s3://drawanddeploy/{user.username}/ --recursive --region=us-east-1')
        return {"Status": "User created!"}
    else:
        return {"Error": "User already exists!"}


@app.delete('/api/delete_user/{username}/')
def delete_user(username):
    try:
        shutil.rmtree(f'/drawanddeploy/{username}')
    except:
        pass
    os.system(f'aws s3 rm s3://drawanddeploy/{username}/ --region=us-east-1 --recursive')
    return {"Status": "User deleted!"}


@app.get('/api/get_users/')
def get_s3_users():
    output = subprocess.Popen(['aws', 's3', 'ls', 's3://drawanddeploy', '--region=us-east-1'], stdout=subprocess.PIPE)
    response, error = output.communicate()
    users_list = str(response).split('PRE')
    for item in range(len(users_list)):
        users_list[item] = users_list[item].strip().replace('\\n','').replace('/','').replace("'",'')
    users_list.pop(0)
    try:
        return users_list
    except:
        return {"Error": f"{error}"}


@app.get('/api/get_projects/{username}/')
def get_s3_projects(username):
    output = subprocess.Popen(['aws', 's3', 'ls', f's3://drawanddeploy/{username}/', '--region=us-east-1'], stdout=subprocess.PIPE)
    response, error = output.communicate()
    projects_list = str(response).split('PRE')
    for item in range(len(projects_list)):
        projects_list[item] = projects_list[item].strip().replace('\\n','').replace('/','').replace("'", '')
    projects_list.pop(0)
    projects_list.remove('init_user')
    try:
        projects_list.remove('ssh_keys')
    except:
        pass
    return projects_list


@app.post('/api/create_project/')
def create_new_project(project: Project):
    project_path = f'/drawanddeploy/{project.username}/{project.project_name}'
    if project.project_name != "init_project":
        if not os.path.exists(f'/drawanddeploy/{project.username}/{project.project_name}/'):
            os.makedirs(f'{project_path}/init_project/')
            os.system(f'touch /drawanddeploy/{project.username}/{project.project_name}/init_project/init.txt')
            os.system(f'aws s3 cp {project_path}/ s3://drawanddeploy/{project.username}/{project.project_name}/ --recursive --region=us-east-1 --exclude ".terraform*"')
            return {"Status": "Project created!"}
        else:
            return {"Error": "Project already exists!"}
    else:
        return {"Error": "You cannot create an project named 'init_project'"}


@app.delete('/api/delete_project/{username}/{project_name}/')
def delete_existing_project(username, project_name):
    try:
        shutil.rmtree(f'/drawanddeploy/{username}/{project_name}')
    except:
        pass
    os.system(f'aws s3 rm s3://drawanddeploy/{username}/{project_name} --region=us-east-1 --recursive')
    return {"Status": "Project deleted!"}


@app.put('/api/edit_existing_project/')
def edit_existing_project_in_s3(project: Project):
    os.system(f'aws s3 sync s3://drawanddeploy/{project.username}/{project.project_name}/ /drawanddeploy/{project.username}/{project.project_name}/ --region=us-east-1 --exclude "init_project"')
    os.system(f'aws s3 sync s3://drawanddeploy/{project.username}/ssh_keys/ /drawanddeploy/{project.username}/ssh_keys/ --region=us-east-1')
    return {"Status": "File pulled from S3 Bucket!"}


@app.post('/api/account_credentials/')
def set_account_credentials(useracc: UserAccount, project: Project):
    if(useracc.subscription_id == None):
        os.system(f'az login -u {useracc.user_email} -p {useracc.user_password}')
        account_settings = provider_block_script()
    else:
        account_settings = provider_block_script(useracc.subscription_id, useracc.client_id, useracc.client_secret, useracc.tenant_id)
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/provider.tf', 'a+')
    terraform_file.write(account_settings)
    return {"Status": "Account authenticated!"}


@app.post('/api/resource_group/')
def create_resource_group(rg: ResourceGroup, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(resource_group_script(rg))
    return {"Status": "Resource Group created!"}


@app.post('/api/virtual_network/')
def create_virtual_network(vnet: VirtualNetwork, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(virtual_network_script(vnet))
    return {"Status": "Virtual Network created!"}


@app.post('/api/subnet/')
def create_subnet(subnet: Subnet, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(vnet_subnets_script(subnet))
    return {"Status": "Subnet created"}


@app.post('/api/security_group/')
def create_security_group(sg: SecurityGroup, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(security_group_script(sg))
    return {"Status": "Security Group created!"}


@app.get('/api/get_existing_keys/{username}/')
def get_existing_keys(username):
    ssh_list = []
    for object in bucket.objects.filter(Prefix=f'{username}/ssh_keys/'):
        key_list = str(object).split(f"s3.ObjectSummary(bucket_name='drawanddeploy', key='{username}/ssh_keys/")
        key = key_list[1].replace("')",'')
        if '.pub' in key:
            pass
        else:
            ssh_list.append(key)
    return ssh_list


@app.post('/api/create_ssh_key/')
def create_ssh_key(key: PublicKey, user: User):
    if not os.path.exists(f'/drawanddeploy/{user.username}/ssh_keys/'):
        os.makedirs(f'/drawanddeploy/{user.username}/ssh_keys/')
    os.system(f'ssh-keygen -b 2048 -t rsa -f /drawanddeploy/{user.username}/ssh_keys/{key.key_name}.pem -q -N ""')
    os.system(f'aws s3 cp /drawanddeploy/{user.username}/ssh_keys/ s3://drawanddeploy/{user.username}/ssh_keys --region=us-east-1 --recursive')
    output = subprocess.Popen(['aws', 's3', 'presign', f's3://drawanddeploy/{user.username}/ssh_keys/{key.key_name}.pem', '--expires-in', '90', '--region=us-east-1'], stdout=subprocess.PIPE)
    response, error = output.communicate()
    temporary_link = str(response)
    temporary_link = temporary_link[2:-3]
    try:
        return {"Link": f"{temporary_link}"}
    except:
        return {"Error": f"{error}"}


@app.post('/api/nat_gateway/')
def create_nat_gateway(nat_gtw: NatGateway, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(nat_gateway_script(nat_gtw))
    return {"Status": "NAT Gateway created!"}


@app.post('/api/windows_virtual_machine/')
def create_virtual_machine(vm: WindowsVirtualMachine, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(windows_virtual_machine_script(vm))
    return {"Status": "Virtual Machine created!"}


@app.post('/api/linux_virtual_machine/')
def create_virtual_machine(vm: LinuxVirtualMachine, project: Project):
    terraform_file = open(f'/drawanddeploy/{project.username}/{project.project_name}/main.tf', 'a+')
    terraform_file.write(linux_virtual_machine_script(vm))
    return {"Status": "Virtual Machine created!"}


@app.get('/api/get_script/{username}/{project}/')
def get_script_terraform(username, project):
    os.system(f'aws s3 cp /drawanddeploy/{username}/{project}/ s3://drawanddeploy/{username}/{project} --region=us-east-1 --recursive --exclude ".terraform*"')
    output = subprocess.Popen(['aws', 's3', 'presign', f's3://drawanddeploy/{username}/{project}/main.tf', '--expires-in', '3600', '--region=us-east-1'], stdout=subprocess.PIPE)
    response, error = output.communicate()
    script_link = str(response)
    script_link = script_link[2:-3]
    return {"Link": f"{script_link}"}


@app.post('/api/apply/')
def apply_infrastructure(project: Project):
    os.chdir(f'/drawanddeploy/{project.username}/{project.project_name}')
    os.system('terraform init')
    os.system('terraform apply --auto-approve')
    os.system(f'aws s3 cp /drawanddeploy/{project.username}/{project.project_name}/ s3://drawanddeploy/{project.username}/{project.project_name} --region=us-east-1 --recursive --exclude ".terraform*"')
    output = subprocess.Popen(['aws', 's3', 'presign', f's3://drawanddeploy/{project.username}/{project.project_name}/main.tf', '--expires-in', '3600', '--region=us-east-1'], stdout=subprocess.PIPE)
    response, error = output.communicate()
    script_link = str(response)
    script_link = script_link[2:-3]
    try:
        return {"Link": f"{script_link}"}
    except:
        return {"Error": f"{error}"}


@app.delete('/api/destroy/{username}/{project_name}/')
def destroy_infrastructure(username, project_name):
    os.chdir(f'/drawanddeploy/{username}/{project_name}/')
    os.system('terraform apply -destroy --auto-approve')
    return {"Status": "Infrasctructure and files destroyed"}
