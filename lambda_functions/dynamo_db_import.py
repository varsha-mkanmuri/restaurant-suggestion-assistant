import json
import csv
import boto3
import time


def lambda_handler(event, context):
    try:

        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        bucket = event["Records"][0]["s3"]["bucket"]['name']
        key = event["Records"][0]["s3"]["object"]["key"]

        #print("bucket", bucket, "key", key)

        csv_file = s3.get_object(Bucket=bucket, Key=key)

        record_list = csv_file["Body"].read().decode('utf-8').split("\n")

        csv_reader = csv.reader(record_list)
        table = dynamodb.Table('yelp-restaurants')
        for row in csv_reader:
            add_to_db = table.put_item(

                TableName='yelp-restaurants',
                Item={
                    'insertedAtTimestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    'BusinessID': row[0],
                    'Name': row[1],
                    'Cuisine': row[2],
                    'Address': row[3],
                    'Coordinates': row[4],
                    'NumberOfReviews': row[5],
                    'Rating': row[6],
                    'ZipCode': row[7]
                })

        print("Successfully Uploaded")

    except Exception as e:
        print(str(e))