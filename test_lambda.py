from lambda_locust import handler
lambda_payload = {
    'locustfile': 'locust_test_file.py',
    'host': 'https://forms-staging.cdssandbox.xyz',
    'num_users': 2,
    'spawn_rate': 1,
    'run_time': "10s"
}

lambda_results = handler(event=lambda_payload)

print("Invocation of locust complete")
print(lambda_results)
