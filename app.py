from flask import Flask, render_template, redirect, jsonify, request, url_for
import pyaudio
import wave
import speech_recognition as sr
import csv
import os
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

username=''
name=''
folder=''

def recoder(x):
    chunk = 1024  
    sample_format = pyaudio.paInt16 
    channels = 1
    fs = 44100  
    seconds = 5
    p = pyaudio.PyAudio()
    print('Recording...')
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)
    frames = []
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()  
    print('Finished recording.')
    wf = wave.open(f'static/recorded_voice_{x}.wav', 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    return voice_to_text(x)

def voice_to_text(x):
    r = sr.Recognizer()
    audio_path = f"static/recorded_voice_{x}.wav"
    with sr.AudioFile(audio_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        return text
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return "error1"
    except sr.RequestError as e:
        print(f"Error: {e}")
        return "error1"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/Signup.html")
def signin():
    return render_template("Signup.html")

@app.route("/recording_signup")
def password():
    if recoder("up")!="error1": 
        rec='Voice recorded Sucessfully'
    else:
        rec="Again record voice"    
    return render_template("Signup.html",rec=rec)

@app.route("/recording_signin") 
def password1():
    if recoder("in")!="error1": 
        rec='Voice recorded Sucessfully'
    else:
        rec="Again record voice"        
    return render_template("index.html",rec=rec)

@app.route('/Signup.html', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        register_data=pd.read_csv("static/register.csv")
        if username in register_data['username'].values:
            return render_template('Signup.html',use="Username is already exits")
        name = request.form['name']
        email = request.form['email']
        text=voice_to_text("up")
        if text!="error1":
            with open('static/register.csv', 'a',newline="") as file:
                writer = csv.writer(file)
                writer.writerow([name,email,username,text])
            os.makedirs(f"static/data/{username}")
            return "Account created Sucessfully"
    return render_template("Signup.html")

@app.route('/', methods=['POST'])
def signin1():
    global username,name,folder
    if request.method == 'POST':
        username = request.form['username']
        text=voice_to_text("in")
        register_data=pd.read_csv("static/register.csv")
        if username not in register_data['username'].values:
            return render_template('index.html',use="Username is not correct")
        data=register_data.values
        for i in data:
            if i[2]==username and i[3]==text:
                folder=f"static/data/{i[2]}"
                name=i[0]
                files=os.listdir(folder)
                return render_template("data.html" , name = i[0],files=files,folder=folder)


    return render_template("index.html")

@app.route('/data.html')
def data():
    global name,username,folder
    folder=f"static/data/{username}"
    files=os.listdir(folder)
    return render_template("data.html" ,name=name,files=files,folder=folder)

@app.route("/data.html",methods=['POST'])
def upload():  
    global username,name,folder
    try:
        if request.method == 'POST':
            files = request.files.getlist('files')
            for file in files:
                filename = secure_filename(file.filename)
                file.save("static/data/" +username+"/" + file.filename)
            folder=f"static/data/{username}"
            files=os.listdir(folder)
            return render_template('data.html',name=name,files=files,folder=folder)        

    except:        
        err="Try Again"
        return render_template('data.html',err=err) 

          


if __name__ == "__main__":
    app.run(host='127.0.0.1',port=5000,debug=True)    

