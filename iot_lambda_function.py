import json, os, time, uuid, boto3, datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE'])

RAW_BUCKET = os.environ['RAW_BUCKET']
PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']

def lambda_handler(event, context):
    # event is from API Gateway Proxy
    body = json.loads(event.get("body", "{}"))
    
    vehicle_id = body.get("vehicle_id")
    speed = body.get("speed")
    battery = body.get("battery")
    temperature = body.get("temperature")
    
    if not vehicle_id:
        return {"statusCode": 400, "body": json.dumps({"error": "vehicle_id required"})}
    
    ts = datetime.datetime.utcnow().isoformat()
    
    record = {
        "vehicle_id": vehicle_id,
        "speed": speed,
        "battery": battery,
        "temperature": temperature,
        "ingest_time": ts
    }
    
    # 1) write RAW event file
    date_prefix = datetime.datetime.utcnow().strftime("year=%Y/month=%m/day=%d")
    raw_key = f"{date_prefix}/{vehicle_id}-{uuid.uuid4().hex}.json"
    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=raw_key,
        Body=json.dumps(body)  # original payload
    )
    
    # 2) append PROCESSED event (newline-delimited JSON)
    processed_key = f"{date_prefix}/events.json"
    s3.put_object(
        Bucket=PROCESSED_BUCKET,
        Key=processed_key,
        Body=(json.dumps(record) + "\n").encode("utf-8")
    )
    
    # 3) update DynamoDB with latest state
    table.put_item(
        Item={
            "vehicle_id": vehicle_id,
            "event_time": ts,
            "speed": speed,
            "battery": battery,
            "temperature": temperature
        }
    )
    
    return {"statusCode": 200, "body": json.dumps({"message": "ok", "ingest_time": ts})}