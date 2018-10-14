from flask import Flask, redirect, request
from flask import render_template
from bs4 import BeautifulSoup
import requests
import json
import cognitive_face as CF
from io import BytesIO
import requests
# If you are using a Jupyter notebook, uncomment the following line.
#%matplotlib inline
#import matplotlib.pyplot as plt
from PIL import Image
from operator import itemgetter
from collections import OrderedDict

SUBSCRIPTION_KEY = '09e018dfa90a46bbbf49409cae325fd5'
BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'
STUDENT_GROUP_ID = 'known-students'
CF.BaseUrl.set(BASE_URL) #Set base_url
CF.Key.set(SUBSCRIPTION_KEY) #Set key
daysInClass = 0
totalDays = 0
all_students = []
emotion = {}
def createStudentGroup(name, img_url):
    try:
        CF.person_group.create(STUDENT_GROUP_ID, 'Known Students') #Create new student group
    except:
        pass
    #user_data = 'Grad student'
    response = CF.person.create(STUDENT_GROUP_ID, name)


    # Get person_id from response
    person_id = response['personId']
    CF.person.add_face(img_url, STUDENT_GROUP_ID, person_id)
    global all_students
    all_students = CF.person.lists(STUDENT_GROUP_ID)
    #print("nmmnm")
    #print (all_students)


    CF.person_group.train(STUDENT_GROUP_ID)
    response = CF.person_group.get_status(STUDENT_GROUP_ID)
    #status = response['status']

def deletePersonGroup(groupID):
    CF.person_group.delete(groupID)

def identifyStudent(img_url):
    response = CF.face.detect(img_url)
    face_ids = [d['faceId'] for d in response]
    #print (response)
    identified_faces = CF.face.identify(face_ids, STUDENT_GROUP_ID)
    #print (identified_faces)

    personID = identified_faces[0]['candidates'][0]['personId']
    #print(personID)
    #print(all_students)
    for student in all_students:
        if student['personId'] == personID:
            print(student['name'])
            print('present in class')
            return True

    return False




#img = Image.open(BytesIO(response.content))
#img.show()

def detectEmotions(img_url):
    faces = CF.face.detect(img_url,attributes='emotion')
    e = faces[0]['faceAttributes']['emotion']

    for key, value in sorted(e.items(), key = itemgetter(1), reverse = True):
        d = {key:value}
        return d


def getAttendence():
    return int((daysInClass/totalDays))


# createStudentGroup('jitesh', 'jitesh.jpg') #add student and image
# identifyStudent('jitesh_new.jpg') #check if image matches with original student image
# deletePersonGroup(STUDENT_GROUP_ID)
# detectEmotions('jitesh_new.jpg')

sName = None
imagePath = None

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/studentProfiles/')
def studentProfiles():
    return render_template('studentProfiles.html')

@app.route('/newStudent/')
def newStudent():
    return render_template('newStudent.html')

@app.route('/studentInput/', methods=['POST'])
def studentInput():
    imagePath = request.form['pic']
    sName = request.form['studentName']
    emo = next(iter(detectEmotions(imagePath)))
    return render_template('studentInput.html', image = imagePath, student = sName, emote = emo)

if __name__ == '__main__':
    app.run(debug = True)
