import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError
import datetime

REGION = 'us-east-1'
HOST = 'search-restaurants-zudew6giovmcocmzjutiea3vd4.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'


def lambda_handler(event, context):
    print("Event triggered by Cloud Watch", event)
   
    sqs = boto3.client('sqs')
    sqs_res = sqs.get_queue_url(QueueName='SQS')
    sqs_url = sqs_res['QueueUrl']

    received_message = sqs.receive_message(
        QueueUrl=sqs_url,
        MaxNumberOfMessages=1,
        MessageAttributeNames=['All']
    )
    
    print('received_message', received_message)
    
    if 'Messages' not in received_message:
        print("SQS queue has no messages currently.")
        return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
        }
        
    sqs_message = received_message['Messages'][0]

    print('Received message from sqs queue ', sqs_message)
    receipt_handle = sqs_message['ReceiptHandle']

    response = sqs.delete_message(
        QueueUrl= sqs_url,
        ReceiptHandle=receipt_handle
    )
    
    location = sqs_message['MessageAttributes']['location']['StringValue']
    dining_date = sqs_message['MessageAttributes']['dining_date']['StringValue']
    dining_time = sqs_message['MessageAttributes']['dining_time']['StringValue']
    num_people = sqs_message['MessageAttributes']['num_people']['StringValue']
    email = sqs_message['MessageAttributes']['email']['StringValue']
    cuisine = sqs_message['MessageAttributes']['cuisine']['StringValue']
    
    
    results = query(cuisine)
    
    selected_business_ids = []
    for result in results:
        selected_business_ids.append(result['restaurant_id'])
    
    sns_response_data = []
    #replace time and num of people from sqs queue input
    sns_response_msg = 'Hello! Here are my 5 ' + cuisine +' restaurant suggestions for ' + num_people +\
    ' people, for ' +  dining_date + ' at ' + dining_time + ':\n'
    for business_id in selected_business_ids:
        sns_response_data.append(lookup_data_dynamodb({'BusinessID': business_id}))
    
    suggestion_num = 1  
    for data in sns_response_data:
        
        restaurant_name = data['Name']
        restaurant_address = data['Address']
        number_of_reviews = data['NumberOfReviews']
        overall_rating = data['Rating']
        sns_response_msg += str(suggestion_num) + '. ' + restaurant_name + ', located at ' + restaurant_address + ".\n"
        suggestion_num += 1
    
    sns_response_msg += 'Enjoy your meal!'
    
    print(sns_response_msg)
    #comment out later
    send_ses(sns_response_msg, 'Restaurant recommendations for you!', email)
    store_user_search(email, cuisine, location, dining_date, dining_time, num_people)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda 2!')
    }


def query(term):
    q = {'size': 5, 'query': {'multi_match': {'query': term}}}
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
        http_auth=get_awsauth(REGION, 'es'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    #print(res)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])
    return results


def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
                    
                    

def lookup_data_dynamodb(key, db=None, table='yelp-restaurants'):
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table(table)

    try:
        response = table.get_item(Key=key)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return

    '''else:
        print(response['Item'])
        return response['Item']'''
    
    return response['Item'] 
    
def send_ses(message, subject, email):
    try:
        #replace ToAddress in ses from sqs
        ses_client = boto3.client('ses', region_name='us-east-1')
        response = ses_client.send_email(
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Body': {
                'Text': {
                    'Charset': 'UTF-8',
                    'Data': message,
                }
            },
            'Subject': {
                'Charset': 'UTF-8',
                'Data': subject,
            },
        },
        Source='smrithip23@gmail.com'
        )
    
    except ClientError:
        print('Error', e.response['Error']['Message'])
        return
    
    print(response)
    
    
def store_user_search(email, cuisine, location, dining_date, dining_time, num_people, db= None):
    insertedAtTimestamp =  str(datetime.datetime.now().timestamp())
    search_event = {
        'SearchID': email + '.' + str(insertedAtTimestamp),
        'UserEmail': email,
        'Cuisine': cuisine,
        'Location': location,
        'DiningDate': dining_date,
        'DiningTime': dining_time,
        'NumofPeople': num_people,
        'insertedAtTimestamp': insertedAtTimestamp
    }
    
    if not db:
        db = boto3.resource('dynamodb')
    table = db.Table('users-search')
    try:
        response = table.put_item(Item=search_event)
    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return None
    print("Search results saved successfully for ", email)
    return response