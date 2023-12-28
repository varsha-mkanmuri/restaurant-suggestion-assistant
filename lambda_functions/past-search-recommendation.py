import json
import boto3
from botocore.exceptions import ClientError
import datetime
from boto3.dynamodb.conditions import Attr
from collections import defaultdict
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = 'us-east-1'
HOST = 'search-restaurants-zudew6giovmcocmzjutiea3vd4.us-east-1.es.amazonaws.com'
INDEX = 'restaurants'

def lambda_handler(event, context):
    
    print("called from LF1", event)
    email = event['Email']
    most_searched_cusine, second_searched_cuisine = fetch_favourite_cuisines(email)
    print(most_searched_cusine, second_searched_cuisine)

    response_msg = ''
    if most_searched_cusine is None and second_searched_cuisine is None:
        # return accordingly to lex
        response_msg = "We see that you have no past searches. Please enter 'Dining' to get recommendations!"
    elif second_searched_cuisine is None and most_searched_cusine is not None:
        response_msg = history_based_recommendation(most_searched_cusine, 'first')
        response_msg += '\n If you want to look for more options please enter "Dining"!'
    elif second_searched_cuisine is not None and most_searched_cusine is not None:
        response_msg = history_based_recommendation(most_searched_cusine, 'first')
        response_msg += history_based_recommendation(second_searched_cuisine, 'second')
        response_msg += '\n If you want to look for more options please enter "Dining"!'
    print(response_msg)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!'),
        'message': response_msg
    }


def fetch_favourite_cuisines(email):
    db = boto3.resource('dynamodb')
    table = db.Table('users-search')
    try:
        response = table.scan(
            FilterExpression=Attr('UserEmail').eq(email)
        )

        searched_cuisines = dict()
        for search in response['Items']:
            current_cuisine = search['Cuisine']
            if current_cuisine in searched_cuisines:
                searched_cuisines[current_cuisine] += 1
            else:
                searched_cuisines[current_cuisine] = 1
        print(searched_cuisines)

        if len(searched_cuisines) < 1:
            return None, None
        most_searched_cusine = max(searched_cuisines, key=searched_cuisines.get)
        del searched_cuisines[most_searched_cusine]

        if len(searched_cuisines) < 1:
            return most_searched_cusine, None
        second_searched_cuisine = max(searched_cuisines, key=searched_cuisines.get)
        return most_searched_cusine, second_searched_cuisine

    except ClientError as e:
        print('Error', e.response['Error']['Message'])
        return None, None


def history_based_recommendation(cuisine, tag=''):
    results = query(cuisine)

    selected_business_ids = []
    for result in results:
        selected_business_ids.append(result['restaurant_id'])

    response_data = []
    # replace time and num of people from sqs queue input
    response_msg = 'Here are my 5 restaurant suggestions for your ' + tag + ' favourite cusine - ' + cuisine + ':\n'
    for business_id in selected_business_ids:
        response_data.append(lookup_data_dynamodb({'BusinessID': business_id}))

    suggestion_num = 1
    for data in response_data:
        restaurant_name = data['Name']
        restaurant_address = data['Address']
        number_of_reviews = data['NumberOfReviews']
        overall_rating = data['Rating']
        response_msg += str(suggestion_num) + '. ' + restaurant_name + ', located at ' + restaurant_address + ".\n"
        suggestion_num += 1

    return response_msg

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