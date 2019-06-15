import boto3
import os
import requests

current_ip = list()

current_ip.append(requests.get('https://api.ipify.org?format=json').json()['ip']+"/32")


def remove_sg_permissions(security_group, permissions, client):
    try:
        client.revoke_security_group_ingress(
            GroupId=security_group,
            IpPermissions=permissions
        )
    except Exception as error:
        print(error)


def add_sg_permissions(security_group, permissions, client):
    try:
        client.authorize_security_group_ingress(
            GroupId=security_group,
            IpPermissions=permissions
        )
    except Exception as error:
        print(error)


def update_sg(all_ips, security_group, region):
    client = boto3.client('ec2', region_name=region)

    response = client.describe_security_groups(
        GroupIds=[security_group]
        )

    if not response['SecurityGroups'][0]['IpPermissions']:
        raise Exception("No rules in security group to append new public IP to")
    permissions = response['SecurityGroups'][0]['IpPermissions']

    combined_ips = all_ips

    add_permissions = []
    remove_permissions = []

    for permission in permissions:
        sg_ips = []
        if permission["IpRanges"]:
            for sg_ip in permission["IpRanges"]:
                sg_ips.append(sg_ip['CidrIp'])

        permission['UserIdGroupPairs'] = []

        ips_to_add = list(set(combined_ips).difference(sg_ips))
        ips_to_remove = list(set(sg_ips).difference(combined_ips))

        if not ips_to_add == ips_to_remove:
            if ips_to_add:
                temp_add_permission = permission.copy()
                temp_add_permission["IpRanges"] = [{"CidrIp":s} for s in ips_to_add]
                add_permissions.append(temp_add_permission)

            if ips_to_remove:
                temp_remove_permission = permission.copy()
                temp_remove_permission["IpRanges"] = [{"CidrIp":s}  for s in ips_to_remove]
                remove_permissions.append(temp_remove_permission)

    if add_permissions:
        print("Updated the SecurityGroup to allow traffic from: {}".format(ips_to_add))
        add_sg_permissions(security_group, add_permissions, client)

    if remove_permissions:
        print("Removed the IP Address {} from the SecurityGroup".format(ips_to_remove))
        remove_sg_permissions(security_group, remove_permissions, client)


update_sg(current_ip, os.environ['SecurityGroup'], os.environ['Region'])
