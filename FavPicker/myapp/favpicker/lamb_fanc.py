import boto3
import json

def lambda_invoke(user_id):

    input_event = {
        "param1": user_id,
    }

    Payload = json.dumps(input_event)

    client = boto3.client("lambda", region_name="ap-northeast-1")
    response = client.invoke(
        FunctionName="s3_zip",
        InvocationType='RequestResponse',
        Payload=Payload
    )

    lambda_response = json.loads(response["Payload"].read())

    print(lambda_response)
    
    return lambda_response