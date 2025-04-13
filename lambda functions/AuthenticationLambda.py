import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
login_table = dynamodb.Table('login')

def lambda_handler(event, context):
    operation = event.get('path', '').split('/')[-1]
    
    if operation == 'login':
        return handle_login(event)
    elif operation == 'register':
        return handle_register(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Invalid operation'
            })
        }

def handle_login(event):
    body = json.loads(event.get('body', '{}'))
    email = body.get('email')
    password = body.get('password')
    
    if not email or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Email and password are required'
            })
        }
    
    try:
        response = login_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        
        if response['Items'] and response['Items'][0]['password'] == password:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'user_name': response['Items'][0]['user_name']
                })
            }
        else:
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid email or password'
                })
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Login error: {str(e)}'
            })
        }

def handle_register(event):
    body = json.loads(event.get('body', '{}'))
    email = body.get('email')
    user_name = body.get('user_name')
    password = body.get('password')
    
    if not email or not user_name or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Email, username, and password are required'
            })
        }
    
    try:
        response = login_table.query(
            KeyConditionExpression=Key('email').eq(email)
        )
        
        if response['Items']:
            return {
                'statusCode': 409,
                'body': json.dumps({
                    'success': False,
                    'message': 'Email already exists. Please use a different email address.'
                })
            }
        
        login_table.put_item(
            Item={
                'email': email,
                'user_name': user_name,
                'password': password
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Registration successful'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Registration error: {str(e)}'
            })
        }