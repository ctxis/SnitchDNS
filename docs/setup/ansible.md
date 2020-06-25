# Ansible

**WARNING**: The Ansible scripts have been tested only against clean installations of the supported operating systems. Be careful if you run them against an environment with non-standard configuration.

Ansible scripts are provided in the `./setup/ansible` directory.

Rename the `vars.yml.template` file to `vars.yml`, follow the instructions within the file to set the appropriate variables, and run against your host:

```
cd ./setup/ansible
ansible-playbook -K snitch.yml -v --user <USER_TO_LOGIN_WITH> --ask-pass -i <IP_OR_HOSTNAME_OF_MACHINE>,
```