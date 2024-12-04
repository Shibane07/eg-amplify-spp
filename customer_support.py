import json
import boto3

# Initialize S3 client
s3_client = boto3.client('s3')

# Constants for S3 bucket and file
BUCKET_NAME = 'your-bucket-name'
STORAGE_UNITS_FILE = 'storage_units.json'

def lambda_handler(event, context):
    """AWS Lambda function entry point."""
    
    action = event.get('action')
    
    if action == 'list_storages':
        status = event.get('status')
        return list_storages(status)
    
    elif action == 'update_status':
        unit_id = event.get('unit_id')
        new_status = event.get('new_status')
        return update_unit_status(unit_id, new_status)
    
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid action specified.')
        }

def get_storage_units():
    """Retrieve storage units from S3."""
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=STORAGE_UNITS_FILE)
        storage_units = json.loads(response['Body'].read())
        return storage_units
    except Exception as e:
        print(f"Error retrieving storage units: {e}")
        return []

def list_storages(status):
    """List storages with a specific status."""
    storage_units = get_storage_units()
    
    if status not in ["Available", "Reserved", "Cancelling", "Problem", "Unavailable"]:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid status specified.')
        }
    
    available_units = list(filter(lambda unit: unit['status'] == status, storage_units))
    return {
        'statusCode': 200,
        'body': json.dumps(available_units)
    }

def update_unit_status(unit_id, new_status):
    """Change the status of a storage unit."""
    valid_statuses = ['Available', 'Unavailable', 'Reserved', 'Cancelling', 'Problem']
    
    if new_status not in valid_statuses:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid status change.')
        }
    
    storage_units = get_storage_units()
    
    for unit in storage_units:
        if unit['unit_id'] == unit_id:
            old_status = unit['status']
            unit['status'] = new_status
            
            # Save updated units back to S3
            s3_client.put_object(Bucket=BUCKET_NAME, Key=STORAGE_UNITS_FILE, Body=json.dumps(storage_units))
            
            return {
                'statusCode': 200,
                'body': json.dumps(f"Status of unit {unit_id} changed from {old_status} to {new_status}.")
            }
    
    return {
        'statusCode': 404,
        'body': json.dumps('Unit not found.')
    }