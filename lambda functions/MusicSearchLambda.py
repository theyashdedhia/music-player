import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
music_table = dynamodb.Table('music')

S3_BUCKET = 'task2-music-images-bucket'  

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    title = body.get('title', '')
    artist = body.get('artist', '')
    album = body.get('album', '')
    year = body.get('year', '')
    

    if not any([title, artist, album, year]):
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': 'At least one search criterion is required'
            })
        }
    
    try:
        filter_expression = None
        
        if title:
            filter_expression = Attr('title').contains(title)
        
        if artist:
            artist_filter = Attr('artist').contains(artist)
            filter_expression = artist_filter if filter_expression is None else filter_expression & artist_filter
        
        if album:
            album_filter = Attr('album').contains(album)
            filter_expression = album_filter if filter_expression is None else filter_expression & album_filter
        
        if year:
            year_filter = Attr('year').eq(year)
            filter_expression = year_filter if filter_expression is None else filter_expression & year_filter
        
        response = music_table.scan(
            FilterExpression=filter_expression
        )
        
        results = []
        for music in response.get('Items', []):
            try:
                image_url = s3.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': S3_BUCKET,
                        'Key': f"images/{music['artist'].title().rstrip('.').replace(' ', '')}.jpg"  # Added images/ prefix
                    },
                    ExpiresIn=3600
                )
            except Exception as e:
                print(f"Error generating image URL for {music['artist']}: {str(e)}")
                image_url = None
            
            results.append({
                'title': music['title'],
                'artist': music['artist'],
                'album': music.get('album', 'Unknown'),
                'year': music['year'],
                'image_url': image_url
            })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'results': results
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'message': f'Error during search: {str(e)}'
            })
        }