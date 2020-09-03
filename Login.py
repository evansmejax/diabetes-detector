from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from PIL import Image
import streamlit as st 
import pandas as pd

import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()

# DB Management sqlite3 

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)') 

def add_userdata(username, password):
     c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username,password))
     conn.commit() 

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?',(username,password))
    data = c.fetchall()
    return data

def view_all_users(username,password):
    c.execute('SELECT * FROM userstable',(username,password))
    data = c.fetchall()
    return data


def get_user_input(): 
    pregnancies = st.sidebar.slider('pregnancies', 0, 17, 3) 
    glucose = st.sidebar.slider('glucose', 0, 199, 117) 
    blood_pressure = st.sidebar.slider('blood_pressure', 0, 122, 72) 
    skin_thickness = st.sidebar.slider('skin thickness', 0, 99, 23)
    insulin = st.sidebar.slider('insulin', 0.0, 846.0, 30.5)
    BMI = st.sidebar.slider('BMI', 0.0, 67.1, 32.0) 
    DPF = st.sidebar.slider('DPF', 0.078, 2.42, 0.3725) 
    age = st.sidebar.slider('age', 21, 81, 29) 

    # Store a dictionary into a variable 
    user_data = { 
        'pregnancies': pregnancies, 
        'glucose': glucose, 
        'blood_pressure': blood_pressure, 
        'skin_thickness': skin_thickness, 
        'insulin':insulin, 
        'BMI': BMI, 
        'DPF':DPF, 
        'age':age
        } 

    # Transform the data into a data frame

    features = pd.DataFrame(user_data, index = [0])
    return features 
    




def main(): 
    st.title("DIABETES DETECTOR APP") 
    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu) 
    if choice == "Home":
        st.subheader("Home") 
    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"): 
            #if == password '12315':
            create_usertable()
            result = login_user(username,password)
            if result:
                st.success("Logged In as {}".format(username)) 
                task = st.selectbox("Select a Task",["Dashboard","Analytics","Edit Profile"]) 
                if task == "Dashboard":
                    st.subheader("Welcome to Automated Diabetes Detection System") 
                    # Cover Image
                    image = Image.open('assets/011.jpg')
                    st.image(image, caption='ML',use_column_width=True)
                elif task == "Analytics":
                    st.subheader("Diabetes Analytics")
                    df = pd.read_csv('assets/data.csv')
                    st.subheader("Data Information:")
                    st.dataframe(df) 
                    st.write(df.describe()) 
                    chart = st.bar_chart(df) 
                    X = df.iloc[:, 0:8].values 
                    Y = df.iloc[:, -1].values
                    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
                    user_input = get_user_input() 
                    st.subheader('User Input:')
                    st.write(user_input)

                    #Create '7. 'lie model " 
                    RandomForestClassifier = RandomForestClassifier() 
                    RandomForestClassifier.fit(X_train, Y_train) 

                    #Show the models metrics 

                    st.subheader('Model Test Accuracy Score:') 
                    st.write(str(accuracy_score(Y_test, RandomForestClassifier.predict(X_test)) * 100)+'%')


                    #Store the  models predictions in  a variable 
                    prediction = RandomForestClassifier.predict(user_input) 

                    #Setasubheaderand display the classification 

                    st.subheader('Classification: ') 
                    st.write(prediction)


                elif task == "Edit Profile":
                    st.subheader("Your Profile")
                    user_result = view_all_users(username,password)
                    clean_db = pd.DataFrame(user_result,columns=['Username','Password'])
                    st.dataframe(clean_db)
            else:
                st.warning("Incorrect Username/Password") 


    if choice == "SignUp":
        st.subheader("Create New Account")
        
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')  
        if st.button("Signup"):  
            create_usertable()
            add_userdata(new_user,new_password)
            st.success("You have successfully created a valid Account") 
            st.info("Go to Login Menu to login") 

if __name__ == "__main__":
    main()