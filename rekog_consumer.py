#!/usr/bin/env python

ACCESS_KEY= "AKIAJVR3DFLUAJLFZKWA"
SECRET_KEY = "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"

import json
import boto3
from pprint import pprint
import time

REGION="us-east-1"

BUCKET = 'e88-final'

QUEUE = 'https://sqs.us-east-1.amazonaws.com/095045241365/new_s3_event'

SQS = boto3.client(service_name='sqs', region_name=REGION, aws_access_key_id=ACCESS_KEY,
						  aws_secret_access_key=SECRET_KEY)



credentials = {"aws_access_key_id" : ACCESS_KEY, "aws_session_access_key" : SECRET_KEY}
token = "c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J"

headers = {'authorization': "Bearer {0}".format(token)}
DB = boto3.resource(service_name='dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY,
						  aws_secret_access_key=SECRET_KEY)

# creates a data stream to recieve data from producer
def create_stream(device_name, stream_name, media_type, hours):
	kinesis = boto3.client(service_name = 'kinesis', region_name = REGION, aws_access_key_id = ACCESS_KEY,
                  aws_secret_access_key = SECRET_KEY)
	response = kinesis.create_stream(DeviceName = device_name,streamName = stream_name, MediaType=media_type, DataRetentionInHOurs=hours)
	return response['Labels']






#submits image to aws recognition
def rekonize(bucket, key, max_labels):
	image = {'Bucket': bucket, 'Name': key}
	rek = boto3.client(service_name='rekognition', region_name=REGION, aws_access_key_id=ACCESS_KEY,
					   aws_secret_access_key=SECRET_KEY)

	response = rek.detect_labels(Image = {'S3Object' : image}, MaxLabels = max_labels )
	return(response)

def label_dict(labels):
	label_d = {}
	for label in labels:
		label_d.update({'label': label})
	return(label_d)



#stores image in dynamo db with their respective labels
def db_index(image, bucket, labels, verbose=False):
	#index to main table
	labels= [label.get('Name') for label in labels]
	table = DB.Table('camera_labels')
	for label in labels:
		table.put_item(
			Item={
				'label': label,
				'name' : "https://s3.amazonaws.com/" + bucket + "/" + image,

			}
		)

	if verbose:
		print('writing....')
		print('name:', image)
		print('labels:',labels)

def get_message():

	response = SQS.receive_message(QueueUrl = QUEUE,
								   MaxNumberOfMessages = 1)
	return (response)



def poll_SQS():
	'''
	Polls SQS continuously for new S3 Images
	'''
	while True:
		try:
			response = get_message()
			# convert to json  response to dictionary
			receipt_handle = response['Messages'][0]['ReceiptHandle']
			response = json.loads(response['Messages'][0]['Body'])
			# build s3 file name
			message = response['Message']
			message = json.loads(message)
			bucket = message['detail']['requestParameters']['bucketName']
			key = message['detail']['requestParameters']['key']
			# delete message from queue
			SQS.delete_message(QueueUrl=QUEUE, ReceiptHandle= receipt_handle)
			return(bucket, key)
		except:
			print('queue empty, polling...')
			time.sleep(2)


def main(verbose=False):
	while True:
		bucket, key = poll_SQS()
		#send to aws recognition
		response = rekonize(bucket, key, 10)
		labels = response['Labels']
		db_index(image = key, bucket=bucket, labels =labels, verbose=True)
		if verbose:
			pprint(labels, indent=2)


if __name__ == "__main__":
	main(verbose=True)







