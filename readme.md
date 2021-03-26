# voice processing application using aws lex service
## About the project
   - In this project, we have integrated the boto3 python sdk onto the c610 platform and using this, one can invoke and run various Amazon cloud services on the c610 target board. Here we are using Amazon’s lex service to create a voice based application in order to access the camera feed,and also store the captured image on the cloud using Amazon’s s3 bucket service. 
     
## Dependencies
- Ubuntu System 18.04 or above
- Install Adb tool (Android debugging bridge) on host system
- create an Aws user account
- Install python3.5 or above on the host system 

## Prerequisites
- Camera Environment configuration setup on the target device.
- Create a lex bot with intent and slot. 
- Create a  s3 bucket service on AWS website.
- Building the opencv$ bitbake opencv  library for target board


### Camera Environment configuration setup on the target device.
 -To setup the camera environment configuration follow the below  document "Turbox-C610_Open_Kit_Software_User_Manual_LE1.0_v2.0.pdf" In given url 
“https://www.thundercomm.com/app_en/product/1593776185472315” and Refer section 2.10.1

### Create a Lex bot with intent and slot
  - To create a lex bot refer below link 
  ```
   https://alexaworkshop.com/en/custom-skill/1.create-lex.html
  ```  
  Note: make sure that, you have created the intent for "camera", "video" and "recognise", the respnse message of lexbot service need to match with "capture camera", "record video", "recognise". once the setup of lex bot is done, note down the botname, bot alias, userid.
  
### Create a s3 bucket service on Aws website
   - To create the s3 bucket, refer below url from amazon document. 
   ```sh
    https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html
   ```
**Note:** once the s3 bucket is created, note down the bucket name.

### Install opencv library on board 
- To install opencv library on the target board the required meta recipe for opencv is already present in folder “poky/meta-openembedded/meta-oe/recipes-support/opencv/opencv_3.4.5.bb” file. We need to follow the below steps to build.

-  Get into the yocto working directory

 ```sh
  $ cd  <yocto working directory>
 ```
 
- Execute source command for environment setting 

 ```sh
    $ source poky/qti-conf/set_bb_env.sh
 ```
- The pop up menu will be open for available machines that select “qcs610-odk” and press ok. Then one more pop up window will be open for distribution selection in that we need to select “qti-distro-fullstack-perf”. Run the bitbake command for installing packages.

 ```sh
 $ bitbake opencv 
 ```
 
- Client is  screening using a live program development and compiling test, also  provided is the predefined input, you have meet the mentioned output set in the program result

- Once the build is complete the shhttps://alexaworkshop.com/en/custom-skill/1.create-lex.htmlared library and include file will be available in “./tmp-glibc/sysroots-components/armv7ahf-neon/opencv/usr”
Push the opencv shared library to the target board 

 ```sh
   $ cd  ./tmp-glibc/sysroots-components/armv7ahf-neon/opencv/usr/
   $ adb push lib/  /data/lex/
 ```

**Note**: 
- For more reference refer to the “QCS610/QCS410 Linux Platform Development Kit Quick Start Guide document”.
- Also make sure install the all the dependency library from the yocto build to the system (ex: libgphoto2, libv4l-utils) 
- bb recipes of above  library are available inside meta-oe layer you can directly run bitbake command


### Install boto3 library on board
 To install the boto3 package on qcs610. you need to build and install the following python3 packages on yocto build. below are the list of packages
     
   - python3-boto3
   - python3-botocore
   - python3-jmespath 
   - python3-s3transfer
   - html, date-util, multiprocessing, concurrent etc.

We can place the above mentioned bb recipe in the given folder name "poky/poky/meta-openembedded/meta-python/python/". meta recipes for these packages are available in the meta-recipe from given source repository. Afterwards, run the bitbake command python3-boto3 for each library 

Once the build is complete for all recipes, create a libboto3 directory and copy all the required libraries to the folder, and push this same folder to /data/lex folder path of target board.
 ```sh 
    $  adb push libboto3/ /data/lex/ 
 ```

### Steps to build and run the application: 


**Step-1** : initialize the target board with root access.
  ```sh
       $ adb root 
       $ adb remount 
       $ adb shell  mount -o remount,rw /
  ```

**Step-2** : Push the source to the target board with adb command.
  
 ```sh               
       $ git clone <source repository> 
       $ cd <source repository> 
       $ adb push lex_inference.py  /data/lex/
       $ adb push config.py  /data/lex/
       $ adb push cacade/ /data/lex/
       $ adb push recognizer/ /data/lex/
  ```
**Note**: In file config.py, you need to fill your aws security key details abs lex bot information

      - aws_access_key_id,
      - aws_secret_access_key
      - region
      - user-id
      - botName
      - botAlias and s3_bucket_name.
     
- For more information, please refer the below "url https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html"

         
**Step-3** : Execute the python script in the target environment.
  - To start the application, run the below commands on the qcs610 board, 
   ```sh
       /# adb shell
       /# 
   ```
To enable wifi connectivity on target board

   ```sh        
       /# wpa_supplicant -Dnl80211 -iwlan0 -c /etc/misc/wifi/wpa_supplicant.conf -ddddt &
       /# dhcpcd wlan0
   ```  
    
Export the shared library to the LD_LIBRARY_PATH
      
   ```sh   
        /# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/data/lex/lib/
        /# cd data/lex/
   ```
   
**Step 4**:  Execute the python code on the target board,

   ```sh  
         /# python3 lex_inference.py -t "record the video"  
   ```         

it will start recording the vedeo for total duration of 5 sec.

   ```sh  
         /# python3 lex_inference.py -t "capture the image"  
   ```

camera will start capture the image and store the same on s3 bucket.

   ```  
         /# python3 lex_inference.py -t "recognise the person"  
   ```

- It will start identify the person standing before the camera. display it on terminal. 

- To see the capture image, you need to log into s3 bucket console and download the image.

To see the recoded video, you need to execute below command on host system,

  ```
   $ adb pull /data/lex/video.mp4
  ```

