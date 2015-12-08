#!/usr/bin/python
from ansible.module_utils.basic import *
import json

DOCUMENTATION = '''
---
module: glassfish_properties
author: "Evgeny Khmelenko"
version_added: "0.0.1"
short_description: Configuration of system-property in glassfish server
description:
    - Module can to create system-property to glassfish server
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
    cluster_config:
        description:
            - cluster config name
        required: true
    property_file:
        description:
            - file path which contains system properties
            - for example:
            - key1=value1
            - key2=value2
        required: true
'''


def main():
    module = AnsibleModule(
        argument_spec=dict(
            asadmin_path=dict(default='/opt/glassfish3/glassfish/bin/asadmin'),
            glassfish_user=dict(default='admin'),
            glassfish_password_file=dict(
                default='/home/glassfish/.glassfishlogin'),
            glassfish_port=dict(default='4848'),
            cluster_config=dict(required=True),
            property_file=dict(required=True)
        )
    )

    asadmin_sysprop_list_cmd = create_asadmin_sysprop_list_cmd(module)
    rc, asadm_cl_list, err = module.run_command(asadmin_sysprop_list_cmd,
                                                check_rc=True)

    current_properties = {}
    for raw_property in asadm_cl_list.split("\n"):
        if "=" in raw_property:
            key, value = raw_property.split("=")
            current_properties[key] = value

    new_properties = {}
    with open(module.params['property_file']) as fp:
        for line in iter(fp.readline, ''):
            if "=" in line:
                key, value = line.split("=")
                new_properties[key] = value.replace("\n", "")

    updated_properties = {}
    for property_key in new_properties:
        if property_key in current_properties.keys():
            if new_properties[property_key] != current_properties[property_key]:
                module.run_command(create_asadmin_sysprop_delete_cmd(module, property_key))
                module.run_command(create_asadmin_sysprop_add_cmd(module, property_key, new_properties[property_key]))
                updated_properties[property_key] = new_properties[property_key]
        else:
            module.run_command(create_asadmin_sysprop_add_cmd(module, property_key, new_properties[property_key]))
            updated_properties[property_key] = new_properties[property_key]

    if len(updated_properties) >= 1:
        print json.dumps({
            'changed': True,
            'properties': updated_properties
        })
    else:
        module.exit_json(changed = False)


# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin
def create_asadmin_base_cmd(module):
    asadmin_args = []
    asadmin_args.extend([module.params['asadmin_path']])
    asadmin_args.extend(['--user', module.params['glassfish_user']])
    if module.params['glassfish_password_file'] is not None:
        asadmin_args.extend(['--passwordfile',
                            module.params['glassfish_password_file']])
    if module.params['glassfish_port'] is not None:
        asadmin_args.extend(["--port",
                            module.params['glassfish_port']])

    return asadmin_args


# returns:
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   list-system-properties default_cluster-config
def create_asadmin_sysprop_list_cmd(module):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["list-system-properties",
                        module.params['cluster_config']])

    return asadmin_args

# returns
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   delete-system-property \
#   --target default_cluster-config \
#   property_key
def create_asadmin_sysprop_delete_cmd(module, property):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["delete-system-property"])
    asadmin_args.extend(["--target",
                        module.params['cluster_config']])
    asadmin_args.extend([property])

    return asadmin_args

# returns
# /opt/glassfish3/glassfish/bin/asadmin --user admin \
#   --passwordfile /home/glassfish/.glassfishlogin \
#   create-system-properties \
#   --target default_cluster-config \
#   property_key=property_value
def create_asadmin_sysprop_add_cmd(module, property, value):
    asadmin_args = create_asadmin_base_cmd(module)
    asadmin_args.extend(["create-system-properties"])
    asadmin_args.extend(["--target",
                         module.params['cluster_config']])
    asadmin_args.extend([property + "=" + value])

    return asadmin_args

if __name__ == '__main__':
    main()
