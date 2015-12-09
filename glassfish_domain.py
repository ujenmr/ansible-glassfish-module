#!/usr/bin/python
from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: glassfish_domain
author: "Evgeny Khmelenko"
version_added: "0.0.1"
short_description: Configuration of domain in glassfish server
description:
    - Module can to create domain to glassfish
options:
    asadmin_path:
        description:
            - full path to asadmin
        required: false
        default: /opt/glassfish3/glassfish/bin/asadmin
    glassfish_user:
        description:
            - username to asadmin
        required: false
        default: admin
    glassfish_password_file:
        description:
            - file which containt password for glassfish_user
            - AS_ADMIN_PASSWORD=__your_password__
        required: false
        default: /home/glassfish/.glassfishlogin
    glassfish_port:
        description:
            - glassfish asadmin port
        required: false
        default: 4848
    glassfish_domain:
        desctipriton:
            - name of glassfish domain
        requered: true
        default: domain1
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            asadmin_path=dict(default='/opt/glassfish3/glassfish/bin/asadmin'),
            glassfish_user=dict(default='admin'),
            glassfish_password_file=dict(
                default='/home/glassfish/.glassfishlogin'),
            glassfish_port=dict(default='4848'),
            glassfish_domain=dict(default='domain1')
        )
    )

    asadmin_domain_list_cm = create_asadmin_cluster_list_cmd(module)
    rc, out, err = module.run_command(asadmin_domain_list_cm, check_rc=True)

    updated_environment = False
    if rc >= 1:
        if module.params['glassfish_domain'] is not 'domain1':
            module.run_command(create_asadmin_domain_add_cmd(module),
                               check_rc=True)
        updated_environment = True
        module.run_command(create_asadmin_domain_start_cmd(module),
                           check_rc=True)
        module.run_command(create_asadmin_enable_secure_admin_cmd(module),
                           check_rc=True)
        module.run_command(create_asadmin_domain_restart_cmd(module),
                           check_rc=True)

    module.exit_json(changed=updated_environment)


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --port 4848
def create_asadmin_base_cmd(module):
    asadmin_args = []
    asadmin_args.extend([module.params['asadmin_path']])
    asadmin_args.extend(['--user', module.params['glassfish_user']])
    if module.params['glassfish_password_file'] is not None:
        asadmin_args.extend(['--passwordfile',
                            module.params['glassfish_password_file']])
    if module.params['glassfish_port'] is not None:
        asadmin_args.extend(["--port", module.params['glassfish_port']])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --port 4848 \
#   list-clusters
def create_asadmin_cluster_list_cmd(module):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["list-clusters"])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin \
#   create-domain \
#   --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --portbase 4848 \
#   domain1
def create_asadmin_domain_add_cmd(module):
    asadmin_args = []
    asadmin_args.extend([module.params['asadmin_path']])
    asadmin_args.extend(["create-domain"])
    asadmin_args.extend(['--user', module.params['glassfish_user']])
    if module.params['glassfish_password_file'] is not None:
        asadmin_args.extend(['--passwordfile',
                            module.params['glassfish_password_file']])
    if module.params['glassfish_port'] is not None:
        asadmin_args.extend(["--portbase", module.params['glassfish_port']])
    asadmin_args.extend([module.params['glassfish_domain']])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --port 4848 \
#   domain1
def create_asadmin_domain_start_cmd(module):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["start-domain"])
    asadmin_args.extend([module.params['glassfish_domain']])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --port 4848 \
#   restart-domain \
#   domain1
def create_asadmin_domain_restart_cmd(module):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["restart-domain"])
    asadmin_args.extend([module.params['glassfish_domain']])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   --port 4848 \
#   enable-secure-admin
def create_asadmin_enable_secure_admin_cmd(module):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["enable-secure-admin"])
    asadmin_args.extend([module.params['glassfish_domain']])

    return asadmin_args


if __name__ == '__main__':
    main()
