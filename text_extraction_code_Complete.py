import os
import json
import logging
import boto3


# Python trp module is Amazon textract result parser
# https://pypi.org/project/textract-trp/
# You have uploaded module using Lambda Layer.
from trp import Document
from urllib.parse import unquote_plus

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Boto3 - s3 Client
# More Info: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rekognition.html
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DynamoDB_Table_Name')
table_key_column = os.environ.get('Table_Key_Column')


# Declare output file path and name
output_key = "output/textract_response.json"

def load_record_table(pdata_header,pitem_data):
    item_index = 0
    data_item = ""
    payload_text = ""
    key_column_value = pitem_data[1]+"_"+pitem_data[2]
    table_row = {}
    table_row[table_key_column]=key_column_value
    print(table_name)
    for item in pdata_header:
        data_item=pitem_data[item_index]
        if item != "":
            table_row[item]=data_item
            #payload_text=payload_text+"'"+item+"':'"+data_item+"',"
        item_index=item_index + 1
    table_row.update(payload_text)
    
    print(table_row)
    dyntable = dynamodb.Table(table_name)
    response = dyntable.put_item(Item=table_row)
    print(response)
    
    
    
    
def lambda_handler(event, context):
    
    logger.info(event)
    # Iterate through the event
    for record in event['Records']:
        # Get the bucket name and key for the new file
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        # Using Amazon Textract client
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html
        textract = boto3.client('textract', region_name='us-east-1')

        # Analyze document
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/textract.html#Textract.Client.analyze_document
        try:
            response = textract.analyze_document(   # You are calling analyze_document API
                Document={                          # to analyzing document Stored in an Amazon S3 Bucket
                    'S3Object': {
                        'Bucket': bucket,
                        'Name': key
                    }
                },
                FeatureTypes=['TABLES',  # FeatureTypes is a list of the types of analysis to perform.
                              ])                            # Add TABLES to the list to return information about
                                                            # the tables that are detected in the input document.
                                                            # Add FORMS to return detected form data. To perform both
                                                            # types of analysis, add TABLES and FORMS to FeatureTypes .

            doc = Document(response)  # You are parsing the textract response using Document.
        
            # The below code reads the Amazon Textract response and
            # prints the Key and Value
            # for page in doc.pages:
            #     # Print fields
            #     print("Fields:")
            #     for field in page.form.fields:
            #         print("Key: {}, Value: {}".format(field.key, field.value))
            
            # The below code reads the Amazon Textract response and
            # prints the Table data. Uncomment below to use the code.
            data_header=[]
            table_processed=1
            
            for page in doc.pages:
                 print("\nTable details:")
                 for table in page.tables:
                     if table_processed<=1:
                        for r, row in enumerate(table.rows):
                            item_data=[]
                            for c, cell in enumerate(row.cells):
                                if r==0:
                                    data_header.append(cell.text.strip())
                                else:
                                    item_data.append(cell.text.strip())
                                print("Table[{}][{}] = {}".format(r, c, cell.text))
                            print(data_header)
                            print(item_data)
                            if r>=1:
                                print("Loading Row # "+str(r))
                                load_record_table(data_header,item_data)
                     table_processed = table_processed+1          

            

            return_result = {"Status": "Success"}
        
            # Finally the response file will be written in the S3 bucket output folder.
            s3.put_object(
                    Bucket=bucket,
                    Key=output_key,
                    Body=json.dumps(response, indent=4)
                    )            
        
        except Exception as error:
                return {"Status": "Failed", "Reason": json.dumps(error, default=str)}
        
    return {
        'statusCode': 200,
        'body': json.dumps(str(return_result))
        }                