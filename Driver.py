from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from streamlit import caching
from PIL import Image
import streamlit as st 
import pandas as pd
import sqlite3

conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB Management sqlite3 

def create_userauth():
    c.execute('CREATE TABLE IF NOT EXISTS auth_user(username TEXT,password TEXT)') 

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT, security_key TEXT)') 

def add_userdata(username, password,security_key):
     c.execute('INSERT INTO userstable(username,password,security_key) VALUES (?,?,?)', (username,password,security_key))
     conn.commit() 

def add_auth_user(username, password):
     c.execute('INSERT INTO auth_user(username,password) VALUES (?,?)', (username,password))
     conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?',(username,password))
    data = c.fetchall()
    if data:
        add_auth_user(username, password)
    return data

def logout_user():
    c.execute('DELETE FROM auth_user')
    conn.commit()


def is_authenticated():
    c.execute('''SELECT COUNT(*) from auth_user ''')
    data = c.fetchall()
    if data[0][0]==0:
        return False
    return True

def view_all_users():
    c.execute('SELECT * FROM userstable')
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



def migrate():
    create_userauth() 
    create_usertable()



def main():
    migrate() 
    #st.title("DIABETES DETECTOR APP") 
    if is_authenticated():
        print("some one is authenticated")
        auth_menu = ["Dashboard","Analytics","Profile","Users","Logout"]
        choice = st.sidebar.selectbox("Select A Task",auth_menu)
        if choice == "Users":
            st.subheader("All Users")
            user_result = view_all_users()
            clean_db = pd.DataFrame(user_result,columns=['Username','Password','Security_key'])
            st.dataframe(clean_db)
        if choice == "Logout":
            logout_user()
        if choice == "Analytics":
            #st.subheader("Diabetes Analytics")
            df = pd.read_csv('assets/data.csv')
            st.subheader("Training Data Information:")
            st.dataframe(df) 
            st.write(df.describe()) 
            chart = st.bar_chart(df) 
            X = df.iloc[:, 0:8].values 
            Y = df.iloc[:, -1].values
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
            user_input = get_user_input() 
            st.subheader('User Input:')
            st.write(user_input)

            #Create model 
            MyRandomForestClassifierObj = RandomForestClassifier() 
            MyRandomForestClassifierObj.fit(X_train, Y_train) 

            # Show the models metrics 

            st.subheader('Model Test Accuracy Score:') 
            st.write(str(accuracy_score(Y_test, MyRandomForestClassifierObj.predict(X_test)) * 100)+'%')

            # Store the  models predictions in  a variable 
            prediction = MyRandomForestClassifierObj.predict(user_input) 

            #Set a subheaderand display the classification 

            st.subheader('Classification: ') 
            st.write(prediction)
        if choice == "Dashboard":
            st.subheader("Welcome to Automated Diabetes Detection System") 
            # Cover Image
            image = Image.open('assets/011.jpg')
            st.image(image, caption='ML',use_column_width=True)
        
    else:
        print("You are logged out")
        menu = ["Home","Login","SignUp"]

        choice = st.sidebar.selectbox("Menu",menu) 

        if choice == "Home":
            st.subheader("Home")
        if choice == "Logout":
            state['logged_in']=False
            #caching.clear_cache()
            st.warning("You have Logged out")
            
        if choice == "Login":
            username = st.sidebar.text_input("User Name")
            password = st.sidebar.text_input("Password",type='password')
            if st.sidebar.checkbox("Login"): 
                create_usertable()
                result = login_user(username,password)
                if result:
                    st.success("Logged In as {}".format(username)) 
                    task = st.selectbox("Select a Task",["Dashboard","Analytics","All Users"])

                    if task == "Dashboard":
                        st.subheader("Welcome to Automated Diabetes Detection System") 
                        # Cover Image
                        image = Image.open('assets/011.jpg')
                        st.image(image, caption='ML',use_column_width=True)
                    elif task == "Analytics":
                        st.subheader("Diabetes Analytics")
                        df = pd.read_csv('assets/data.csv')
                        st.subheader("Training Data Information:")
                        st.dataframe(df) 
                        st.write(df.describe()) 
                        chart = st.bar_chart(df) 
                        X = df.iloc[:, 0:8].values 
                        Y = df.iloc[:, -1].values
                        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
                        user_input = get_user_input() 
                        st.subheader('User Input:')
                        st.write(user_input)

                        #Create model 
                        MyRandomForestClassifierObj = RandomForestClassifier() 
                        MyRandomForestClassifierObj.fit(X_train, Y_train) 

                        # Show the models metrics 

                        st.subheader('Model Test Accuracy Score:') 
                        st.write(str(accuracy_score(Y_test, MyRandomForestClassifierObj.predict(X_test)) * 100)+'%')

                        # Store the  models predictions in  a variable 
                        prediction = MyRandomForestClassifierObj.predict(user_input) 

                        #Set a subheaderand display the classification 

                        st.subheader('Classification: ') 
                        st.write(prediction)


                    elif task == "All Users":
                        st.subheader("All Users")
                        user_result = view_all_users()
                        clean_db = pd.DataFrame(user_result,columns=['Username','Password','Security_key','Logged_in'])
                        st.dataframe(clean_db)
                else:
                    st.warning("Incorrect Username/Password") 


        if choice == "SignUp":
            st.subheader("Create New Account")
            
            new_user = st.text_input("Username")
            new_password = st.text_input("Password",type='password')
            security_key = st.text_input("Security Question: which city were you born")  
            logged_in='true'
            if st.button("Signup"):  
                create_usertable()
                add_userdata(new_user,new_password,security_key)
                st.success("You have successfully created a valid Account") 
                st.info("Go to Login Menu to login") 

if __name__ == "__main__":
    main()