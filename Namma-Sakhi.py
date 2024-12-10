import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
from PIL import Image
import io
import uuid
import os
import time
import PyPDF2
import docx
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pygame
from gtts import gTTS
from translate import Translator

nltk.download('vader_lexicon', quiet=True)

genai.configure(api_key="AIzaSyAqLgulBNIV689k89u8cQcvO9RekyMJ7rk")
model = genai.GenerativeModel('gemini-pro')

recognizer = sr.Recognizer()

sia = SentimentIntensityAnalyzer()

pygame.mixer.init()

translator = Translator(to_lang="en")

def process_voice_input():
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            sentiment = analyze_sentiment(text)
            return text, sentiment
        except:
            return "Sorry, I could not understand that.", None


def analyze_sentiment(text):
    sentiment_scores = sia.polarity_scores(text)
    compound_score = sentiment_scores['compound']
    if compound_score >= 0.05:
        return "Positive"
    elif compound_score <= -0.05:
        return "Negative"
    else:
        return "Neutral"

def generate_response(prompt):
    response = model.generate_content(prompt)
    return response.text

def speak(text, lang='en'):
    text = text.replace('%', ' percent ')
    text = text.replace('&', ' and ')
    text = text.replace('$', ' dollars ')
    text = text.replace('@', ' at ')
    text = text.replace('*', '  ')
    
    
    if lang != 'en':
        text = translator.translate(text, dest=lang).text

    
    pygame.mixer.init()

    
    tts = gTTS(text=text, lang=lang)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)  

   
    pygame.mixer.music.load(audio_data, 'mp3')
    pygame.mixer.music.play()

   
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def stop_audio():
    pygame.mixer.music.stop()



def analyze_file(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    elif file_extension == 'docx':
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        text = file.read().decode('utf-8')
    
    summary = generate_response(f"Summarize the following medical document: {text}")
    return summary


st.title("Namma-Sakhi: GenAI-Powered Single Mother Companion")


st.sidebar.title("Welcome To Namma-Sakhi")
feature = st.sidebar.radio("", 
    ["Hey-Sakhi"])


languages = {
    "English": "en", "Hindi": "hi", "Kannada": "kn", "Telugu": "te", "Tamil": "ta",
    "Bengali": "bn", "Nepali": "ne", "Marathi": "mr", "Korean": "ko", "Spanish": "es",
    "French": "fr", "German": "de", "Chinese": "zh-cn"
}
selected_language = st.sidebar.selectbox("Select Language", list(languages.keys()))
lang_code = languages[selected_language]

if feature == "Hey-Sakhi":
    st.header("How Can I Help You!")
    
    sub_feature = st.selectbox("Choose a service", 
        ["Express yourself", "File Analysis", "Symptom Checker", "Health Advice", "Voice Interaction", "Diet Plan Creator", "Predictive Health", "Appointment Scheduling"])

    if sub_feature == "Express yourself":
        user_input = st.text_input("Sakhi-Clear your Medical Queries:")
        if user_input:
            response = generate_response(user_input)
            st.write("Namma Sakhi:", response)
            if st.button("Read Response"):
                speak(response, lang_code)
            if "drug photo" in user_input.lower():
                st.image("https://via.placeholder.com/300x200.png?text=Drug+Photo+Placeholder", caption="Requested Drug Photo")

    elif sub_feature == "File Analysis":
        uploaded_file = st.file_uploader("Upload a medical document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            summary = analyze_file(uploaded_file)
            st.write("Document Summary:", summary)
            if st.button("Read Summary"):
                speak(summary, lang_code)

    elif sub_feature == "Symptom Checker":
      symptoms = st.multiselect("Select your symptoms:", 
        ["Fever", "Cough", "Headache", "Fatigue", "Nausea", "Shortness of breath", 
         "Chest pain", "Abdominal pain", "Diarrhea", "Vomiting", "Muscle aches", 
         "Sore throat"])
    
      if st.button("Check Symptoms"):
        symptom_text = ", ".join(symptoms)
        diagnosis = generate_response(f"Based on these symptoms: {symptom_text}, what could be the possible conditions? Provide a concise explanation.")
        
       
        st.session_state.diagnosis = diagnosis
        
        st.write("Possible Conditions:", diagnosis)

    
      if "diagnosis" in st.session_state:
        diagnosis = st.session_state.diagnosis
        
        if st.button("Read Diagnosis"):
            speak(diagnosis, lang_code)


    elif sub_feature == "Health Advice":
        age = st.number_input("Age", min_value=0, max_value=120)
        weight = st.number_input("Weight (kg)", min_value=0.0)
        height = st.number_input("Height (cm)", min_value=0.0)
        if st.button("Get Advice"):
            advice = generate_response("Provide brief health advice for a {age}-year-old person weighing {weight} kg and {height} cm tall.")
            st.write("Health Advice:", advice)
            if st.button("Read Advice"):
                speak(advice, lang_code)

    elif sub_feature == "Voice Interaction":
        if st.button("Start Voice Interaction"):
            user_speech, sentiment = process_voice_input()
            st.write("You said:", user_speech)
            if sentiment:
                st.write("Detected Sentiment:", sentiment)
            if user_speech != "Sorry, I could not understand that.":
                ai_response = generate_response(user_speech)
                st.write("Namma Sakhi:", ai_response)
                speak(ai_response, lang_code)

    elif sub_feature == "Diet Plan Creator":
        age = st.number_input("Age", min_value=0, max_value=120, key="diet_age")
        weight = st.number_input("Weight (kg)", min_value=0.0, key="diet_weight")
        height = st.number_input("Height (cm)", min_value=0.0, key="diet_height")
        diet_preference = st.selectbox("Diet Preference", ["Vegetarian", "Non-vegetarian", "Vegan"])
        health_goal = st.selectbox("Health Goal", ["Weight loss", "Weight gain", "Maintenance"])
        if st.button("Generate Diet Plan"):
            diet_plan = generate_response(f"Create a brief 7-day diet plan for a {age}-year-old {diet_preference} person weighing {weight} kg and {height} cm tall, with a goal of {health_goal}.")
            st.write("Your Personalized Diet Plan:", diet_plan)
            if st.button("Read Diet Plan"):
                speak(diet_plan, lang_code)

    elif sub_feature == "Predictive Health":
        st.write("Please provide your health information for a predictive analysis:")
        age = st.number_input("Age", min_value=0, max_value=120, key="pred_age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        family_history = st.multiselect("Family History of Diseases", ["Diabetes", "Heart Disease", "Cancer", "Hypertension"])
        lifestyle = st.selectbox("Lifestyle", ["Sedentary", "Moderately Active", "Very Active"])
        if st.button("Generate Predictive Health Report"):
            prediction = generate_response(f"Provide a concise predictive health analysis for a {age}-year-old {gender} with family history of {', '.join(family_history)} and a {lifestyle} lifestyle.")
            st.write("Predictive Health Report:", prediction)
            if st.button("Read Health Report"):
                speak(prediction, lang_code)

    elif sub_feature == "Appointment Scheduling":
        patient_name = st.text_input("Patient Name")
        appointment_date = st.date_input("Preferred Date")
        appointment_time = st.time_input("Preferred Time")
        doctor_specialty = st.selectbox("Doctor Specialty", ["General Physician", "Cardiologist", "Dermatologist", "Orthopedic", "Pediatrician"])
        if st.button("Schedule Appointment"):
            confirmation = f"Appointment scheduled for {patient_name} with a {doctor_specialty} on {appointment_date} at {appointment_time}"
            st.success(confirmation)
            if st.button("Read Confirmation"):
                speak(confirmation, lang_code)

    if st.button("Stop Audio"):
        stop_audio()


# Feedback system
st.sidebar.header("Feedback")
feedback = st.sidebar.text_area("Please provide your feedback:")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")
    speak("Thank you for your feedback!", lang_code)

# Disclaimer
disclaimer = "This is a prototype. Always consult with a qualified healthcare professional for medical advice."
st.sidebar.markdown(f"*Disclaimer:* {disclaimer}")
if st.sidebar.button("Read Disclaimer"):
    speak(disclaimer, lang_code)