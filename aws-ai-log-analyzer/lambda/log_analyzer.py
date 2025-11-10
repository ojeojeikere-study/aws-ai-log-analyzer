import os
import json
import boto3
import requests
from summarize_logs import summarize_text

def lambda_handler(event, context):
    log_group = os.environ.get('LOG_GROUP_NAME')
    s3_bucket = os.environ.get('S3_BUCKET_NAME')
    llm_api_url = os.environ.get('LLM_API_URL', 'https://api.llm-endpoint.com/v1/analyze')
    llm_api_key = os.environ.get('LLM_API_KEY')

    logs_client = boto3.client('logs')
    s3 = boto3.client('s3')
    sns = boto3.client('sns')

    try:
        response = logs_client.filter_log_events(logGroupName=log_group, limit=20)
        log_messages = [event['message'] for event in response.get('events', [])]
        combined_logs = '\n'.join(log_messages)

        payload = {'text': combined_logs, 'task': 'summarize'}
        headers = {'Authorization': f'Bearer {llm_api_key}', 'Content-Type': 'application/json'}
        llm_response = requests.post(llm_api_url, headers=headers, json=payload)
        llm_output = llm_response.json()

        summary = summarize_text(llm_output)
        filename = f"analysis_{context.aws_request_id}.json"
        s3.put_object(Bucket=s3_bucket, Key=filename, Body=json.dumps(summary))

        if summary.get('anomaly_score', 0) > 0.7:
            sns.publish(
                TopicArn=os.environ.get('SNS_TOPIC_ARN'),
                Message=f"High anomaly detected in logs. Summary: {summary}",
                Subject="AWS AI Log Analyzer Alert"
            )

        return {'statusCode': 200, 'body': 'Log analysis complete.'}

    except Exception as e:
        print(f"Error: {e}")
        return {'statusCode': 500, 'body': str(e)}
