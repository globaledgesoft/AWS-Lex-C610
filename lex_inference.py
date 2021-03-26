import sys
sys.path.append("./libboto3")            # Adding dependency library path 
import config
import boto3
import numpy as np
import argparse
import cv2

"""
import sounddevice as sd
import pyaudio

"""


lex_client = boto3.client('lex-runtime', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key , region_name= config.region)
s3_client = boto3.client('s3', aws_access_key_id = config.aws_access_key_id, aws_secret_access_key = config.aws_secret_access_key , region_name= config.region)

label_mapper = ['Unknown', 'sahil']

"""
def samplerecord(seconds):

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000
    
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT, 
                    channels = CHANNELS, 
                    rate = RATE, 
                    input = True, 
                    frames_per_buffer = CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return b''.join(frames)


def post_content(frame, request_attributes = None, session_attributes = None):

    response = lex_client.post_content(
        botName = config.botName, 
        botAlias =  config.botAlias,
        userId =  config.userId,
        request_attributes = {},
        session_attributes = {},
        contentType = "audio/lpcm; sample-rate=8000; sample-size-bits=16; channel-count=1; is-big-endian=false", 
        accept = 'audio/pcm', 
        inputStream = frame
    )
    return response
"""

def post_text(text, request_attributes = None, session_attributes = None):

    request_attributes = {}
    session_attributes = {}
    response = lex_client.post_text(
    botName = config.botName, 
    botAlias =  config.botAlias,
    userId =  config.userId,
    sessionAttributes= session_attributes,
    requestAttributes= request_attributes,
    inputText=text
    )
    return response


def capture_image():
    
    cap = cv2.VideoCapture("qtiqmmfsrc ldc=TRUE !video/x-raw, format=NV12, width=1280, height=720, framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)    
    count = 15
    while(count):             # skipping the initial bluish frame
        count = count - 1 
        ret ,frame = cap.read()
        if(count == 5):
            cv2.imwrite('image.jpg',frame)
            s3_client.upload_file('image.jpg', config.bucket_name , 'image_upload.jpg')      
            break
    cap.release()


def record_video(seconds):  #  This function will record for 5 sec 
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter("appsrc ! videoconvert ! omxh264enc ! h264parse ! mp4mux ! filesink location=video.mp4", fourcc, 30, (1280, 720), True)
    cap = cv2.VideoCapture("qtiqmmfsrc ldc=TRUE !video/x-raw, format=NV12, width=1280, height=720, framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)    
    count = seconds * 30                 #30fps  
    while(count):             
        count = count - 1 
        ret ,frame = cap.read()
        out.write(frame)
    cap.release()
    out.release()


def predict(recognizer):
    # perform perdict function 
    face_cascade = cv2.CascadeClassifier('cascade/haarcascade_frontalface_default.xml')
    detected = 0
    i=0

    cap = cv2.VideoCapture("qtiqmmfsrc ldc=TRUE !video/x-raw, format=NV12, width=1280, height=720, framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
    count =15
    names = []
    while(count):
        count = count - 1
        _, img = cap.read()
        if(count == 5): 
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)  
            for (x,y,w,h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                label, dist_val = recognizer.predict(roi_gray)
                if(dist_val>70):
                    label = 0
                else:
                    i += 1
                names.append(label_mapper[label]) 
            break;
    cap.release()
    return names


if __name__ == "__main__":

    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--text", default = " ", required=False, help=" text message to lex bot")   
    ap.add_argument("-s", "--seconds", default = 2 , required=False, help=" no of sec need to be record")   
    args = vars(ap.parse_args())

    if (config.method  == "text" ):
        response = post_text(args['text'])
        print(response["message"])

    """
    if(config.method == 'audio'):
        frame  = samplerecord(args['seconds'])
        response = post_content(frame) 
        if response["dialogState"] == 'ReadyForFulfillment': break
        elif response["dialogState"] == "Failed": isFailed = True
        content = np.fromstring(response["audioStream"].read(), dtype="<i2")
        sd.play(content, 16000)
        print(response["message"])    
    """

    if(response['message'] == "capture image"):
        capture_image()
        print("captured image is stored in s3 bucket")

    if(response['message'] == "record video"):
        record_video(5)
        print("recording the video for 5 sec")

    if(response['message'] == "recognise"):
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("recognizer/trainningData.yml")
        name = predict(recognizer)

        if(name[0]  == ''):
            print("no person infront of camera")
        elif(name[0] == 'Unknown'):
            print("unknown person detected")  
        else:
            print("recognize person is", name[0]) 


