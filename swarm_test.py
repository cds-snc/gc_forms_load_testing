import json
from boto3.session import Session
from botocore.client import Config

session = Session()
config = Config(connect_timeout=10, read_timeout=310, retries={'max_attempts': 2})
client = session.client('lambda', config=config)

lambda_payload = {
    'locustfile': 'locust_test_file.py',
    'host': 'https://forms-staging.cdssandbox.xyz',
    'num_users': 20,
    'spawn_rate': 10,
    'run_time':'2m'
}

response = client.invoke(FunctionName='LoadTesting', Payload=json.dumps(lambda_payload))
print(json.loads(response['Payload'].read()))
