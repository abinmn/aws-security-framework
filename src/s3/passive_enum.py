
import os
import requests
import boto3
from argparse import ArgumentParser
from botocore.exceptions import ClientError


targetStem = ""
inputFile = ""

parser = ArgumentParser()
parser.add_argument("-t", "--target", dest="targetStem",
                    help="Select a target stem name (e.g. 'shopify')", metavar="targetStem", required="True")
parser.add_argument("-f", "--file", dest="inputFile",
                    help="Select a bucket permutation file (default: bucket-names.txt)", default="bucket-names.txt", metavar="inputFile")
args = parser.parse_args()

with open(args.inputFile, 'r') as f:
    bucketNames = [line.strip() for line in f]
    lineCount = len(bucketNames)

print(
    "[*] Commencing enumeration of '%s', reading %i lines from '%s'." %
     (args.targetStem, lineCount, f.name))

s3_client = boto3.client('s3')

for name in bucketNames:
    r = requests.head("http://%s%s.s3.amazonaws.com" % (args.targetStem, name))
    if r.status_code != 404:
        print("[+] Checking potential match: %s%s --> %s" %
              (args.targetStem, name, r.status_code))

        try:
            bucket = f'{args.targetStem}{name}'
            print(bucket)
            response = s3_client.list_objects(
                Bucket=bucket)
            print(response)

        except ClientError as error:
            code = error.response['Error']['Code']


print("[*] Enumeration of '%s' buckets complete." % (args.targetStem))
