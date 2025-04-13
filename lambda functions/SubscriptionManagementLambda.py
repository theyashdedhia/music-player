import json
import boto3
import decimal
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
subscription_table = dynamodb.Table('subscription')

S3_BUCKET = 'task2-music-images-bucket' 


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    http_method = event.get('httpMethod', '')
    path = event.get('path', '').split('/')[-1]
    
    if http_method == 'GET' and path == 'subscriptions':
        return get_subscriptions(event)
    elif http_method == 'POST' and path == 'subscriptions':
        return add_subscription(event)
    elif http_method == 'DELETE' and path == 'subscriptions':
        return remove_subscription(event)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Invalid operation'
            })
        }

def get_subscriptions(event):
    query_params = event.get('queryStringParameters', {}) or {}
    email = query_params.get('email')
    
    if not email:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Email parameter is required'
            })
        }
    
    try:
        response = subscription_table.scan(
            FilterExpression=Attr('email').eq(email)
        )
        
        subscriptions = []
        for item in response.get('Items', []):
            try:
                image_url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': S3_BUCKET,
                        'Key': f"images/{item['artist'].title().rstrip('.').replace(' ', '')}.jpg"
                    },
                    ExpiresIn=3600
                )
            except Exception as e:
                print(f"Error generating image URL for {item['artist']}: {str(e)}")
                image_url = None 
            
            
            subscriptions.append({
                'title': item['title'],
                'artist': item['artist'],
                'album': item.get('album', 'Unknown'),
                'year': item['year'], 
                'image_url': image_url
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'subscriptions': subscriptions
            }, cls=DecimalEncoder)  
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error fetching subscriptions: {str(e)}'
            })
        }

def add_subscription(event):
    body = json.loads(event.get('body', '{}'))
    email = body.get('email')
    title = body.get('title')
    artist = body.get('artist')
    album = body.get('album', 'Unknown')
    year = body.get('year')
    image_url = body.get('image_url', '')
    
    if not all([email, title, artist, year]):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Email, title, artist, and year are required'
            })
        }
    
    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('title').eq(title) & Key('year').eq(year),
            FilterExpression=Attr('email').eq(email)
        )
        
        if response.get('Items'):
            return {
                'statusCode': 409,
                'body': json.dumps({
                    'success': False,
                    'message': 'Subscription already exists'
                })
            }
        
        subscription_table.put_item(
            Item={
                'email': email,
                'year': year,
                'title': title,
                'artist': artist,
                'album': album,
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Subscription added successfully'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error adding subscription: {str(e)}'
            })
        }

def remove_subscription(event):
    body = json.loads(event.get('body', '{}'))
    email = body.get('email')
    title = body.get('title')
    year = body.get('year')
    
    if not all([email, title, year]):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'Email, title, and year are required'
            })
        }
    
    try:
        response = subscription_table.query(
            KeyConditionExpression=Key('title').eq(title) & Key('year').eq(year),
            FilterExpression=Attr('email').eq(email)
        )
        
        if not response.get('Items'):
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'success': False,
                    'message': 'Subscription not found or does not belong to this user'
                })
            }
            
        subscription_table.delete_item(
            Key={
                'title': title,
                'year': year
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'message': 'Subscription removed successfully'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error removing subscription: {str(e)}'
            }, cls=DecimalEncoder)
        }