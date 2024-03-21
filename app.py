from flask import render_template, jsonify, Flask, redirect, url_for, request, make_response
import os
import io
import numpy as np
from PIL import Image
import keras.utils as image
from keras.models import model_from_json

from datetime import datetime

# Import Firebase
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./config/config.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)


# Admin Side

@app.route('/admin-login', methods=['GET', 'POST'])
def adminLogin():
    if request.method == 'POST':
        data = request.json
        
        name = data.get('username')
        password = data.get('password')
        
        if (name=='admin' and password=='admin@123'):
            return jsonify({'message': 'Authenticated', 'status': 202})
        else:
            return jsonify({'message': 'Not Authenticated', 'status': 401 })
    else:
        return render_template('admin/login.html')

@app.route('/admin')
def admin():
    return render_template('admin/admin.html')

@app.route('/admin/doctors')
def adminDoctors():
    doctors = []
    doctors_ref = db.collection("doctors").get()
    for doctor in doctors_ref:
        doctors.append(doctor.to_dict())
    return render_template('admin/doctors.html', doctors=doctors)

@app.route('/admin/doctors/<username>')
def adminDoctor(username):
    doctor_details = db.collection("doctors").document(username).get().to_dict()
    tests = []
    tests_ref = db.collection("tests").where("username","==",username).get()
    for test in tests_ref:
        tests.append(test.to_dict())
    return render_template('admin/doctor-single.html', tests=tests, doctor_details=doctor_details)

@app.route('/api/doctors/add', methods=['POST'])
def adminAddDoctors():
    if request.method == 'POST':
        data = request.json
        doc_ref = db.collection("doctors").document(data.get('username'))
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({'message': 'Document already exist', 'status': 403})
        else:
            doc_ref.set(data)
            return jsonify({'message': 'Document Created successfully', 'status': 202 })


@app.route('/admin/patients')
def adminPatients():
    patients = []
    patients_ref = db.collection("users").get()
    for patient in patients_ref:
        patients.append(patient.to_dict())
    return render_template('admin/patients.html', patients=patients)

@app.route('/admin/patients/<username>')
def adminPatient(username):
    patient_details = db.collection("users").document(username).get().to_dict()
    tests = []
    tests_ref = db.collection("tests").where("username","==",username).get()
    for test in tests_ref:
        tests.append(test.to_dict())
    return render_template('admin/patient-single.html', tests=tests, patient_details=patient_details)

@app.route('/api/patients')
def getPatients():
    patients = []
    patients_ref = db.collection("tests").get()
    for patient in patients_ref:
        patients.append(patient.to_dict())
    return jsonify(patients)
    


# User Side

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/doctors')
def doctors():
    doctors = []
    doctors_ref = db.collection("doctors").get()
    for doctor in doctors_ref:
        doctors.append(doctor.to_dict())
    return render_template('doctors.html', doctors=doctors)

@app.route('/doctors/<username>')
def doctor(username):
    doctor_details = db.collection("doctors").document(username).get().to_dict()
    tests = []
    tests_ref = db.collection("tests").where("username","==",username).get()
    for test in tests_ref:
        tests.append(test.to_dict())
    return render_template('doctor-single.html', tests=tests, doctor_details=doctor_details)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/profile/<username>', methods=["POST"])
def profileGet(username):
    user_info = db.collection("users").document(username).get().to_dict()
    return user_info

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        doc_ref = db.collection("users").where("username","==",data.get('username')).where("password","==",data.get('password')).limit(1)
        doc = doc_ref.get()
        if doc:
            return jsonify({'message': 'Authenticated', 'status': 202})
        else:
            return jsonify({'message': 'Not Authenticated', 'status': 401 })
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        doc_ref = db.collection("users").document(data.get('username'))
        doc = doc_ref.get()
        if doc.exists:
            return jsonify({'message': 'Document already exist', 'status': 403})
        else:
            doc_ref.set(data)
            return jsonify({'message': 'Document Created successfully', 'status': 202 })
    else:
       return render_template('signup.html')


SKIN_CLASSES = {
    0: 'Actinic Keratoses (Solar Keratoses) or intraepithelial Carcinoma (Bowen’s disease)',
    1: 'Basal Cell Carcinoma',
    2: 'Benign Keratosis',
    3: 'Dermatofibroma',
    4: 'Melanoma',
    5: 'Melanocytic Nevi',
    6: 'Vascular skin lesion'
}

def findMedicine(pred):
    if pred == 0:
        return "fluorouracil"
    elif pred == 1:
        return "Aldara"
    elif pred == 2:
        return "Prescription Hydrogen Peroxide"
    elif pred == 3:
        return "fluorouracil"
    elif pred == 4:
        return "fluorouracil (5-FU):"
    elif pred == 5:
        return "fluorouracil"
    elif pred == 6:
        return "fluorouracil"        


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    json_response = {}
    if request.method == 'POST':
        
        try:
            file = request.files['file']
        except KeyError:
            return make_response(jsonify({
                'error': 'No file part in the request',
                'code': 'FILE',
                'message': 'file is not valid'
            }), 400)

        imagePil = Image.open(io.BytesIO(file.read()))
        imageBytesIO = io.BytesIO()
        imagePil.save(imageBytesIO, format='JPEG')
        imageBytesIO.seek(0)
        
        path = imageBytesIO
        
        j_file = open('model.json', 'r')
        loaded_json_model = j_file.read()
        j_file.close()
        
        model = model_from_json(loaded_json_model)
        model.load_weights('model.h5')
        
        img = image.load_img(path, target_size=(224, 224))
        img = np.array(img)
        img = img.reshape((1, 224, 224, 3))
        img = img/255
        
        prediction = model.predict(img)
        pred = np.argmax(prediction)
        
        disease = SKIN_CLASSES[pred]
        accuracy = prediction[0][pred]
        accuracy = round(accuracy*100, 2)
        medicine=findMedicine(pred)
        
        data = {
            "username": request.form['username'],
            "image": request.form['image'],
            "disease": disease,
            "accuracy": accuracy,
            "medicine" : medicine,
            "img_path": file.filename,
            "date": datetime.now(),
        }
        
        doc_ref = db.collection("tests").add(data)
    
        json_response = {
            "detected": False if pred == 2 else True,
            "disease": disease,
            "accuracy": accuracy,
            "medicine" : medicine,
            "img_path": file.filename,
        }

        return make_response(jsonify(json_response), 200)

    else:
        return render_template('detect.html')


if __name__ == "__main__":
    app.run(debug=True, port=3000)
