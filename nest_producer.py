

import yaml
import requests
import http.client
from urllib.parse import urlparse
import boto3
import datetime
import hashlib
import time

#Load Configs
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

#AWS Info
ACCESS_KEY= cfg['aws']['access_key']
SECRET_KEY = cfg['aws']['secret_key']

#S3 Info
S3_REGION= cfg['aws']['region']
BUCKET = cfg['aws']['bucket']


credentials = {"aws_access_key_id" : ACCESS_KEY, "aws_session_access_key" : SECRET_KEY}


#Nest Cam Info
TOKEN = cfg['nest']['token']
DEVICE_ID= cfg['nest']['device_id']

HEADERS =  {'authorization': "Bearer {0}".format(TOKEN)}

#returns live stream url
def live_stream(device_id, token, headers):
    uri = "/devices/cameras/{0}/web_url".format(device_id)
    conn = http.client.HTTPSConnection("developer-api.nest.com")
    conn.request("GET", uri, headers = headers)
    response = conn.getresponse()

    if response.status == 307:
        redirectLocation = urlparse(response.getheader("location"))
        conn = http.client.HTTPSConnection(redirectLocation.netloc)
        conn.request("GET", uri, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception("Redirect with non 200 response")

    data = response.read()
    data = data.decode("utf-8")
    return(data)


#returns snapshot url
def snapshot_url(device_id, token, headers):
    uri = "/devices/cameras/{0}/snapshot_url".format(device_id)
    conn = http.client.HTTPSConnection("developer-api.nest.com")
    conn.request("GET", uri,  headers=headers)
    response = conn.getresponse()

    if response.status == 307:
        redirectLocation = urlparse(response.getheader("location"))
        conn = http.client.HTTPSConnection(redirectLocation.netloc)
        conn.request("GET", uri, headers=headers)
        response = conn.getresponse()
        if response.status != 200:
            raise Exception("Redirect with non 200 response")

    data = response.read()
    data = data.decode("utf-8")
    return(data)



#take a snapshot every {delay} seconds
def get_snap(s3):
    url = snapshot_url(DEVICE_ID, TOKEN, HEADERS)
    url = url.strip("\"")
    img_data = requests.get(url).content
    #unique hash for image name from current time
    hash = hashlib.sha1()
    cur_time = str(time.time())
    cur_time = cur_time.encode("utf-8")
    hash.update(cur_time)
    name = hash.hexdigest()
    img_name = 'snap_' + name + '.jpg'
    s3.put_object(Bucket=BUCKET, Key=img_name, Body=img_data)
    print('oh snapshot taken!')




#producer of snapshots from video
def snap_producer(delay,max,file):
    for snap in range(1,max+1):
        get_snap(file)
        time.sleep(delay)
    print('finished')


if __name__ == "__main__":
    #create connection s3 bucket to store snaps
    s3 = boto3.client(service_name ='s3', region_name = S3_REGION, aws_access_key_id = ACCESS_KEY,
                      aws_secret_access_key = SECRET_KEY)
    snap_producer(1, 25, s3)


