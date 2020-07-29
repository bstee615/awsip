#!/bin/python3

import boto3
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from datetime import datetime


def get_ip():
    '''
    Return this computer's public IP
    '''

    ip_svc_url = 'https://api.ipify.org'

    with urlopen(ip_svc_url) as response:
        ip = response.read().decode('utf-8')

        if ip:
            return ip
        else:
            raise Exception(f"Could not get IP from {ip_svc_url}")


def get_comment(ip):
    '''
    Return a comment to document when the route change was sent in
    '''

    now = datetime.now()
    comment = f'Updated IP to {ip} on {now.strftime("%m/%d/%Y-%H:%M:%S")}'

    if comment:
        return comment
    else:
        raise Exception(f"Error forming comment. IP={ip}, now={now}")


HOSTED_ZONE_ID = 'Z2BTS599RFFOO'  # benjijang.com, from the AWS mgmt console
RECORD_NAME = 'crib.benjijang.com'
RECORD_TYPE = 'A'


def get_boto3_client():
    '''
    Get a boto3 client with Route 53 access.
    '''

    session = boto3.Session(profile_name='awsip')
    return session.client('route53')


def update_record_ip(client, ip, comment):
    '''
    Update the record's IP with a comment.
    '''

    response = client.change_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        ChangeBatch={
            'Comment': comment,
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': RECORD_NAME,
                        'Type': RECORD_TYPE,
                        'TTL': 300,
                        'ResourceRecords': [{'Value': ip}]
                    }
                }]
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception(f'Error updating record. response={response}')


def get_record_ip(client):
    '''
    Get the IP of the currently existing record.
    '''

    response = client.list_resource_record_sets(
        HostedZoneId=HOSTED_ZONE_ID,
        StartRecordName=RECORD_NAME,
        StartRecordType=RECORD_TYPE,
        MaxItems='1'
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        records = response['ResourceRecordSets']
        crib_record = records[0]
        crib_resource_records = crib_record['ResourceRecords']
        crib_primary_resource_record = crib_record['ResourceRecords'][0]
        crib_ip = crib_primary_resource_record['Value']
        return crib_ip
    else:
        raise Exception(
            f'Error getting the current record. response={response}')


if __name__ == '__main__':

    current_ip = get_ip()

    print(f'My public IP is {current_ip}')

    client = get_boto3_client()
    record_ip = get_record_ip(client)
    print(
        f'Got existing record for {RECORD_NAME}({RECORD_TYPE}). IP={record_ip}')

    if record_ip != current_ip:
        comment = get_comment(current_ip)
        print(f'Submitting comment: "{comment}"')

        update_record_ip(client, current_ip, comment)
        print('Successfully changed record')
    else:
        print(f'No need to update IP. IP={record_ip}')
