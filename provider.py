import textwrap

def provider_block_script(subscription_id = None, client_id = None, client_secret = None, tenant_id = None, service_principal = False):
    provider_block = textwrap.dedent(f'''
    # Terraform and provider versions required
    terraform {{
      required_version = ">= 1.0.0"
      required_providers {{
        azurerm = {{
          source = "hashicorp/azurerm"
          version = ">= 3.0.0" 
        }}
      }}
    }}
    
    provider "azurerm" {{
      features {{
        resource_group {{
          prevent_deletion_if_contains_resources = false
        }}
      }}
    ''')
    if(service_principal):
        provider_block = provider_block + textwrap.dedent(f'''
          subscription_id = "{subscription_id}"
          client_id       = "{client_id}"
          client_secret   = "{client_secret}"
          tenant_id       = "{tenant_id}"
        ''')
    provider_block = provider_block + '}'
    return provider_block
