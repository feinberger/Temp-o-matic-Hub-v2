from __future__ import print_function
  
import json
import boto3
  
print('Loading function')
  
def lambda_handler(event, context):
    # Convert message into serialized msg
    received_message = event
    
    # Get the payload of the message
    payload = received_message['Payload']
    
    # Determine which action to do
    
    # Reading/Data Entry goes to SQS
    if payload['Command'] == 'Reading':
        print('Received a reading')
        data_handler(payload)
    elif payload['Command'] == 'Temperature Alarm':
        print('Received Temperature Alarm!')
        send_temperature_alarm(payload)
    elif payload['Command'] == 'Humidity Alarm':
        print('Received Humidity Alarm!')
        send_humidity_alarm(payload)


def send_temperature_alarm(payload):
    # Create an SNS client
    sns = boto3.client('sns')
    
    # Extract data from payload
    temperature = payload['Temperature']
    units = payload['Units']
    trigger = payload['Trigger']
  
    # Publish a message to the specified topic
    response = sns.publish (
      TopicArn = 'arn:aws:sns:us-east-1:723839298742:TemperatureTopic',
      Message = f'Warning! Temperature is over {trigger} degrees {units}. It is at {temperature} degrees {units}!'
    )
  
    print(response)


def send_humidity_alarm(payload):
    # Create an SNS client
    sns = boto3.client('sns')
    
    # Extract data from payload
    humidity = payload['Humidity']
    trigger = payload['Trigger']
  
    # Publish a message to the specified topic
    response = sns.publish (
      TopicArn = 'arn:aws:sns:us-east-1:723839298742:TemperatureTopic',
      Message = f'Warning! Humidity is over {trigger}%. It is at {humidity}%!'
    )
  
    print(response)
    

def data_handler(payload):
    
    # Create an SQS client
    sqs = boto3.client('sqs')
    
    # Get the queue
    sqs_queue_url = 'https://sqs.us-east-1.amazonaws.com/723839298742/Tempomatic_Queue'
    
    # Create queue message
    queue_message = {}
    
    # Extract data from payload
    queue_message['Temperature'] = payload['Temperature']
    queue_message['Units'] = payload['Units']
    queue_message['Humidity'] = payload['Humidity']
    queue_message['Timestamp'] = payload['Timestamp']
    
    queue_string = json.dumps(queue_message)
    
    # Create a new message
    response = sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=queue_string)
    
    print('Storing data in SQS')
