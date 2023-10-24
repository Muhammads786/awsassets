import json
def calculateFactorial(num):
    if num<1:
        return 1
    else:
        return num * calculateFactorial(num-1)

def lambda_handler(event, context):
    result = calculateFactorial(9)
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Calculated Factorial is '+ str(result))
    }
