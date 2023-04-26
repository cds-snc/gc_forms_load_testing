import logging
import json
from invokust.aws_lambda import LambdaLoadTest, results_aggregator

logging.basicConfig(level=logging.INFO)

###
# SETTINGS
###

# How long should the test run for in minutes?
# Note that Lambda invokations that are started cannot be stopped.
# Test times will actually be run in intervals of 3 minutes.
test_time = 6
# How many concurrent users to test for?
# threads x 25 = num of concurrent users
threads = 20
# What test file are we using?
test_file_name = 'locust_test_mail_list.py'

def print_stat(type, name, req_count, median, avg, min, max, rps):
    return "%-7s %-50s %10s %9s %9s %9s %9s %10s" % (
        type,
        name,
        req_count,
        median,
        avg,
        min,
        max,
        rps,
    )


def print_stats_exit(load_test_state):
    summ_stats = load_test_state.get_summary_stats()
    agg_results = results_aggregator(load_test_state.get_locust_results())
    agg_results["request_fail_ratio"] = summ_stats["request_fail_ratio"]
    agg_results["invocation_error_ratio"] = summ_stats["invocation_error_ratio"]
    agg_results["locust_settings"] = load_test_state.lambda_payload
    agg_results["lambda_function_name"] = load_test_state.lambda_function_name
    agg_results["threads"] = load_test_state.threads
    agg_results["ramp_time"] = load_test_state.ramp_time
    agg_results["time_limit"] = load_test_state.time_limit
    logging.info("Aggregated results: {0}".format(json.dumps(agg_results)))

    logging.info(
        "\n============================================================"
        f"\nRamp up time: {agg_results['ramp_time']}s"
        f"\nStarted ramp down after {agg_results['time_limit']}s (time_limit)"
        f"\nThread count: {agg_results['threads']}"
        f"\nLambda invocation count: {agg_results['lambda_invocations']}"
        f"\nLambda invocation error ratio: {agg_results['invocation_error_ratio']}"
        f"\nCumulative lambda execution time: {agg_results['total_lambda_execution_time']}ms"
        f"\nTotal requests sent: {agg_results['num_requests']}"
        f"\nTotal requests failed: {agg_results['num_requests_fail']}"
        f"\nTotal request failure ratio: {agg_results['request_fail_ratio']}\n"
    )
    logging.info(
        "==========================================================================================================================="
    )
    logging.info(
        print_stat(
            "TYPE", "NAME", "#REQUESTS", "MEDIAN", "AVERAGE", "MIN", "MAX", "#REQS/SEC"
        )
    )
    logging.info(
        "==========================================================================================================================="
    )

    reqs = agg_results["requests"]
    for k in reqs.keys():
        k_arr = k.split("_")
        type = k_arr[0]
        del k_arr[0]
        name = "_".join(k_arr)
        logging.info(
            print_stat(
                type,
                name,
                reqs[k]["num_requests"],
                round(reqs[k]["median_response_time"], 2),
                round(reqs[k]["avg_response_time"], 2),
                round(reqs[k]["min_response_time"], 2),
                round(reqs[k]["max_response_time"], 2),
                round(reqs[k]["total_rps"], 2) * agg_results["threads"],
            )
        )
    total_rps = sum(
        [
            reqs[path]["total_rps"]
            for path in reqs
        ]
    ) * agg_results["threads"]
    logging.info(
        print_stat(
            "Total",
            f"Concurrent Users: {agg_results['threads']*25}",
            agg_results["num_requests"],
            "",
            "",
            "",
            "",
            round(total_rps, 2),
        )
    )

    logging.info("Exiting...")

if __name__ == "__main__":

    lambda_runtime = f"{test_time}m" if test_time < 3 else "3m"


    lambda_payload = {
        'locustfile': f"./tests/{test_file_name}",
        'host': 'https://forms-staging.cdssandbox.xyz',
        'num_users': 25,
        'spawn_rate': 5,
        'run_time': lambda_runtime
    }

    load_test = LambdaLoadTest(
    lambda_function_name='LoadTesting',
    threads=threads,
    ramp_time=0,
    time_limit=test_time*60,
    lambda_payload=lambda_payload
    )

    load_test.run()
    print_stats_exit(load_test)

    output_file = open("threads_output.json", "w")
    thread_output = {"threads": load_test.get_locust_results() }
    json.dump(thread_output, output_file)
    output_file.close()