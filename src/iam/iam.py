import json
import datetime
import boto3
import botocore
from botocore.client import Config

# from multiprocessing.dummy import Pool as ThreadPool
def remove_metadata(boto_response):
    if isinstance(boto_response, dict):
        boto_response.pop('ResponseMetadata', None)

    return boto_response

def json_encoder(o):
    if type(o) is datetime.date or type(o) is datetime.datetime:
        return o.isoformat()

    # if isinstance(o, unicode):
    #     return o.encode('utf-8', errors='ignore')

    # if isinstance(o, str):
    #     return o.encode('utf-8', errors='ignore')


def enumerate_using_iam(access_key, secret_key):
    output = dict()

    # Connect to the IAM API and start testing.
    print('Starting permission enumeration for access-key-id "%s"', access_key)
    iam_client = boto3.client(
        'iam',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    try:
        everything = iam_client.get_account_authorization_details()
    except (botocore.exceptions.ClientError,
            botocore.exceptions.EndpointConnectionError,
            botocore.exceptions.ReadTimeoutError):
        pass
    else:
        print('get_account_authorization_details worked!')

        res = remove_metadata(everything)
        output['iam.get_account_authorization_details'] = res['UserDetailList']

        with open('log.json','w') as f:
            json.dump(output, f, indent=4, default=json_encoder)


# def enumerate_using_bruteforce(access_key, secret_key, session_token, region):
#     """
#     Attempt to brute-force and check if iam is available.
#     """
#     output = dict()


#     # pool = ThreadPool(MAX_THREADS)
#     # args_generator = generate_args(access_key, secret_key, session_token, region)

#     try:
#         results = pool.map(check_one_permission)
#     except KeyboardInterrupt:
#         print('')

#         results = []


#         try:
#             pool.close()
#             pool.join()
#         except KeyboardInterrupt:
#             print('')
#             return output

#     for thread_result in results:
#         if thread_result is None:
#             continue

#         key, action_result = thread_result
#         output[key] = action_result

#     pool.close()
#     pool.join()

#     return output

def enumerate_iam(access_key, secret_key):
    """IAM Account Enumerator.

    This code provides a mechanism to attempt to validate the permissions assigned
    to a given set of AWS tokens.
    """
    output = dict()

    output['iam'] = enumerate_using_iam(access_key, secret_key)
    # output['bruteforce'] = enumerate_using_bruteforce(access_key, secret_key, session_token, region)

    return output



access_key = ''
secret_key = ''
enumerate_iam(access_key,secret_key)