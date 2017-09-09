#!/usr/bin/env python

from __future__ import print_function
import boto3
import json
import traceback
import os

ddb_table = os.environ['ModuleTable']


def create_modules():
    try:
        with open('modulelist.json') as modulelist:
            modlist = json.load(modulelist)
        ddb = boto3.client('dynamodb')
        for mod in modlist:
            res = ddb.put_item(TableName=ddb_table, Item=mod)
            print('Response for the insertion of module:' + mod['module']['S'])
            print(res)
    except:
        print('Failed! Debug further.')
        traceback.print_exc()


if __name__ == '__main__':
    create_modules()
