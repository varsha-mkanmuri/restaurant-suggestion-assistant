import boto3
from datetime import datetime
import pytz
import re
import json
eastern = pytz.timezone('US/Eastern')

def validation(location, cuisine, num_people, email, dining_date, dining_time, intent, slots):
    if location:
        words = location.split()
        lowercase_words = [word.lower() for word in words]
        if 'manhattan' not in lowercase_words and ('new' not in lowercase_words or 'york' not in lowercase_words):
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'Location',
                        'message': "We have recommendations for Manhattan and New York. Enter a valid location"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'Location'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "We have recommendations for Manhattan and New York. Enter a valid location"
                }]
            }
    
    if cuisine:
        words = cuisine.split()
        lowercase_words = [word.lower() for word in words]
        if 'chinese' not in lowercase_words and \
        'indian' not in lowercase_words and \
        'japanese' not in lowercase_words and \
        'mexican' not in lowercase_words and \
        'italian' not in lowercase_words and \
        'thai' not in lowercase_words:
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'Cuisine',
                        'message': "We have recommendations for Manhattan and New York. Enter a valid location"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'Cuisine'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "We have recommendations for Chinese, Indian, Japanese, Mexican, Italian, and Thai cuisines. Enter a valid cuisine"
                }]
            }
    
    if num_people:
        words = num_people.split()
        lowercase_words = [word.lower() for word in words]
        if 'minus' in lowercase_words:
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'NumPeople',
                        'message': "We have recommendations for Manhattan and New York. Enter a valid location"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'NumPeople'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "I didn't understand that. Enter a valid number"
                }]
            }
        else:
            try:
                num = int(num_people)
                if num < 0:
                    return {
                        "sessionState": {
                            "dialogAction": {
                                "type": "ElicitSlot",
                                "slots": slots,
                                'slotToElicit': 'NumPeople',
                                'message': "We have recommendations for Manhattan and New York. Enter a valid location"
                            },
                            "intent": {
                                'name': intent,
                                'slots': slots,
                                'slotToElicit': 'NumPeople'
                            },
                        },
                        "messages": [{
                            "contentType": "PlainText",
                            "content": "I didn't understand that. Enter a valid number"
                        }]
                    }
            except:
                return {
                    "sessionState": {
                        "dialogAction": {
                            "type": "ElicitSlot",
                            "slots": slots,
                            'slotToElicit': 'NumPeople',
                            'message': "We have recommendations for Manhattan and New York. Enter a valid location"
                        },
                        "intent": {
                            'name': intent,
                            'slots': slots,
                            'slotToElicit': 'NumPeople'
                        },
                    },
                    "messages": [{
                        "contentType": "PlainText",
                        "content": "I didn't understand that. Enter a valid number"
                    }]
                }
    
    if dining_date:
        date = slots['DiningDate']['value']['interpretedValue']
        given_date = datetime.strptime(date, "%Y-%m-%d")
        today = datetime.now(eastern)
        if given_date.date() < today.date():
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'DiningDate',
                        'message': "Enter today's date or a future date"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'DiningDate'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "Enter today's date or a future date"
                }]
            }
    
    if dining_time:
        time = slots['DiningTime']['value']['interpretedValue']
        given_time = datetime.strptime(date + " " + time, "%Y-%m-%d %H:%M")
        given_time = eastern.localize(given_time)
        print("given", given_time.date(), given_time.time(), given_time.timestamp())
        today = datetime.now(eastern)
        print("today", today.date(), today.time(), today.timestamp())
        if given_time.timestamp() < today.timestamp():
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'DiningTime',
                        'message': "Enter a present time or a time in the future"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'DiningTime'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "Enter a present time or a time in the future"
                }]
            }
            
    if email:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, email)):
            pass
        else:
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'Email',
                        'message': "Enter a valid email id"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'Email'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "Enter a valid email id"
                }]
            }
    
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
                
            },
            "intent": {
                'name': intent,
                'slots': slots
            }
        }
    }
    
def validateEmail(email, intent, slots):
    if email:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if(re.fullmatch(regex, email)):
            pass
        else:
            return {
                "sessionState": {
                    "dialogAction": {
                        "type": "ElicitSlot",
                        "slots": slots,
                        'slotToElicit': 'Email',
                        'message': "Enter a valid email id"
                    },
                    "intent": {
                        'name': intent,
                        'slots': slots,
                        'slotToElicit': 'Email'
                    },
                },
                "messages": [{
                    "contentType": "PlainText",
                    "content": "Enter a valid email id"
                }]
            }
    return {
        "sessionState": {
            "dialogAction": {
                "type": "Delegate"
            },
            "intent": {
                'name': intent,
                'slots': slots
            }
        }
    }

def getValueIfPopulated(field):
    if field:
        return field['value']['originalValue']
    else:
        return field

def SearchHistory(event, intent, invocationSource, slots):
    email = getValueIfPopulated(slots['Email'])
    if invocationSource == "DialogCodeHook":
        return validateEmail(email, intent, slots)

    elif invocationSource == "FulfillmentCodeHook":
        print("inside search history FulfillmentCodeHook: ", slots)
        inputForInvoker = {'Email': email}
        client = boto3.client('lambda')
        
        print("Calling child")
        
        response = client.invoke(
            FunctionName='arn:aws:lambda:us-east-1:252225289072:function:past-search-recommendation',
    	    InvocationType='RequestResponse',
    	    Payload=json.dumps(inputForInvoker)
    	)
    	
        print("response", response)
        responseJson = json.load(response['Payload'])
        message = responseJson['message']
        print("responseJson", responseJson)
        print('message', message)
        
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent,
                    "slots": slots,
                    "state": "Fulfilled"
                }
            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": message
                }
            ]
        }

def DiningSuggestion(event, intent, invocationSource, slots):
    print("Inside DiningSuggestion function")
    location = getValueIfPopulated(slots['Location'])
    cuisine = getValueIfPopulated(slots['Cuisine'])
    num_people = getValueIfPopulated(slots['NumPeople'])
    dining_date =  getValueIfPopulated(slots['DiningDate'])
    dining_time =  getValueIfPopulated(slots['DiningTime'])
    email = getValueIfPopulated(slots['Email'])
    print(location, cuisine, num_people, email, dining_date, dining_time)
    
    if invocationSource == "DialogCodeHook":
        print("inside DialogCodeHook: ", location, cuisine, num_people, email, dining_date, dining_time)
        return validation(location, cuisine, num_people, email, dining_date, dining_time, intent, slots)
        
    elif invocationSource == "FulfillmentCodeHook":
        print("inside FulfillmentCodeHook: ", location, cuisine, num_people, email, dining_date, dining_time)
        sqs = boto3.client('sqs')
        sqs_res = sqs.get_queue_url(QueueName='SQS')
        sqs_url = sqs_res['QueueUrl']
        # send message to sqs queue
        sqs.send_message(
            QueueUrl=sqs_url,
            MessageAttributes={
                'location': {
                    'DataType': 'String',
                    'StringValue': str(location)
                },
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': str(cuisine)
                },
                'dining_date': {
                    'DataType': 'String',
                    'StringValue': str(slots['DiningDate']['value']['originalValue'])
                },
                'dining_time': {
                    'DataType': 'String',
                    'StringValue': str(slots['DiningTime']['value']['originalValue'])
                },
                'num_people': {
                    'DataType': 'Number',
                    'StringValue': str(num_people)
                },
                'email': {
                    'DataType': 'String',
                    'StringValue': str(email)
                }
            },
            MessageBody=(
                'Sending user input to SQS queue'
            )
        )
        
        print("Message sent to SQS")
        
        return {
            "sessionState": {
                "dialogAction": {
                    "type": "Close"
                },
                "intent": {
                    "name": intent,
                    "slots": slots,
                    "state": "Fulfilled"
                }

            },
            "messages": [
                {
                    "contentType": "PlainText",
                    "content": "Your request has been received. You will be notified over email with a list of restaurant suggestions."
                }
            ]
        }

def lambda_handler(event, context):
    
    # get intent type
    intent = event['sessionState']['intent']['name']
    invocationSource = event['invocationSource']
    
    print("INTENT:", intent)
    print("INVOCATIONSOURCE", invocationSource)
    print("EVENT:", event)
    print("CONTEXT", context)

    if intent == "DiningSuggestionsIntent":
        slots = event['sessionState']['intent']['slots']
        return DiningSuggestion(event, intent, invocationSource, slots)
        
    elif intent == "SearchHistoryIntent":
        slots = event['sessionState']['intent']['slots']
        return SearchHistory(event, intent, invocationSource, slots)
    else:
        print("FallBackIntent")
    
    print("Intent", intent)