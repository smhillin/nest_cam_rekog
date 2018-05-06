
import requests
import http.client
from urllib.parse import urlparse
import time
import boto3
import datetime
import hashlib
import time

#AWS Info
ACCESS_KEY= "AKIAJVR3DFLUAJLFZKWA"
SECRET_KEY = "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"

#S3 Info
S3_REGION="us-east-1"
BUCKET = 'e88-final'
credentials = {"aws_access_key_id" : ACCESS_KEY, "aws_session_access_key" : SECRET_KEY}


#Nest Cam Info
TOKEN = "c.tTwDnxdnToHZrpWnhk5iH4q3JEebhvbeLqitUnsbyBgSupaWkrYlvX1b4374SwVi19akENZsFCmi8RG3AhiquFSpeTjtxtC93rIL1DFoLd69sWoJcPTbh0XXFv2esuVqJmP9eachNAw2wN7J"
DEVICE_ID= "aKftwtb142trLSdvl87kPZxJokmXYmriK-jpahONPvB9Veuc8C1zMA"
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
    print('oh snap!')




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
    snap_producer(1, 5, s3)


