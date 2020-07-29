#!/bin/python3

import boto3
from urllib.request import urlopen
from xml.etree import ElementTree as ET
from datetime import datetime

import logging

STARTTIME = datetime.now()

LOG_PATH = 'log'
LOG_FILENAME = STARTTIME.strftime('%m%d%Y-%H%M%S')

# Expects to find this defined in the user's ~/.aws/config
BOTO3_PROFILE_NAME = 'awsip'

# ID for benjijang.com, from the AWS mgmt console
HOSTED_ZONE_ID = 'Z2BTS599RFFOO'
RECORD_NAME = 'crib.benjijang.com'
RECORD_TYPE = 'A'


def initialize_logging():
    '''
    Set up a logger for console and file output.
    '''

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("lastrun.log"),
            logging.StreamHandler()
        ]
    )


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


def get_comment(prev_ip, current_ip):
    '''
    Return a comment to document when the route change was sent in
    '''

    return f'Updated IP {prev_ip} -> {current_ip} on {STARTTIME.strftime("%m/%d/%Y-%H:%M:%S")}'


def get_boto3_client():
    '''
    Get a boto3 client with Route 53 access.
    '''

    session = boto3.Session(profile_name=BOTO3_PROFILE_NAME)
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
    initialize_logging()
    logging.info('This is an info message')
    logging.info(f'Starting up')

    try:
        current_ip = get_ip()

        logging.info(f'Public IP={current_ip}')

        client = get_boto3_client()
        record_ip = get_record_ip(client)
        logging.info(
            f'Got existing record for {RECORD_NAME}({RECORD_TYPE}). Record IP={record_ip}')

        if record_ip != current_ip:
            comment = get_comment(record_ip, current_ip)
            logging.info(f'Submitting comment: "{comment}"')

            update_record_ip(client, current_ip, comment)
            logging.info('Successfully changed record')
        else:
            logging.info(f'No need to update IP.')
    except Exception as ex:
        logging.error(ex)

    logging.info(f'Shutting down')
