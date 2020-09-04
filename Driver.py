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
    c.execute('CREATE TABLE IF NOT EXISTS userstable(fullname TEXT,email TEXT,country TEXT,mobile TEXT,password TEXT,security_key TEXT)') 

def add_userdata(fullname,email,country,mobile,password,security_key):
     c.execute('INSERT INTO userstable(fullname,email,country,mobile,password,security_key) VALUES (?,?,?,?,?,?)', (fullname,email,country,mobile,password,security_key))
     conn.commit() 

def add_auth_user(username, password):
     c.execute('INSERT INTO auth_user(username,password) VALUES (?,?)', (username,password))
     conn.commit()

def reset_password(username,security,password):
    c.execute('SELECT * FROM userstable WHERE email =? AND security_key =?',(username,security))
    data = c.fetchall()
    if data:
        c.execute("UPDATE userstable set password=? WHERE email = ? AND security_key = ?",(password,username,security))
        conn.commit()
        c.execute("UPDATE auth_user set password = ? WHERE username = ? ",(password,username))
        conn.commit()
    return data

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE email =? AND password =?',(username,password))
    data = c.fetchall()
    if data:
        add_auth_user(username, password)
    return data

def update_user_profile(fullname,email,country,phone,password,old_email,old_password):
    c.execute("UPDATE userstable set email = ?, fullname = ?, country = ?, mobile = ?, password=? WHERE email = ? AND password = ?",(email,fullname,country,phone,password,old_email,old_password))
    conn.commit()
    c.execute("UPDATE auth_user set username = ?, password = ? WHERE username = ? AND password = ?",(email,password,old_email,old_password))
    conn.commit()

def get_user_data():
    c.execute('SELECT * FROM auth_user')
    data = c.fetchall()
    if data[0][0] != 0:
        email = data[0][0]
        password = data[0][1]
        c.execute('SELECT * FROM userstable WHERE email =? AND password =?',(email,password))
        data = c.fetchall()
    else:
        data = []
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
        if choice == "Profile":
            profile_menu = ["View Profile","Edit Profile"]
            action = st.selectbox("Action",profile_menu)
            udata = get_user_data()
            fullname = udata[0][0]
            old_email = udata[0][1]
            country = udata[0][2]
            phone = udata[0][3]
            old_password = udata[0][4]
            security = udata[0][5]
            print(udata)
            if action == "View Profile":
                st.subheader("Full Name : "+ fullname)
                st.subheader("Email Address : "+old_email)
                st.subheader("Country : "+country)
                st.subheader("Phone Number : "+phone)
            if action == "Edit Profile":
                fullname = st.text_input("Full Name : ", fullname)
                email = st.text_input("Email Address : ", old_email)
                country = st.text_input("Country : ", country)
                phone = st.text_input("Phone Number : ", phone)
                password = st.text_input("Password : ", old_password)
                if st.button("Update Profile"):
                    update_user_profile(fullname,email,country,phone,password,old_email,old_password)
        if choice == "Users":
            st.subheader("All Users")
            user_result = view_all_users()
            clean_db = pd.DataFrame(user_result,columns=['Fullname','Email','Country','Mobile','Password','Security_key'])
            st.dataframe(clean_db)
        if choice == "Logout":
            logout_user()
            st.warning("You have just logged out. Please reload the page and login/signup from menu")
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
        menu = ["Login","SignUp","Forgot Password"]
        choice = st.sidebar.selectbox("Menu",menu) 

        if choice == "Forgot Password":
            username = st.text_input("Enter Email")
            security = st.text_input("Which City Were You Born?")
            password = st.text_input("Enter The New Password?")
            if st.button("Reset Password"):
                reset = reset_password(username,security,password)
                if reset:
                    st.success("Password Reset Successfully") 
                else:
                    st.warning("Incorrect Email or Security key provided") 

        if choice == "Login":
            username = st.text_input("Enter Email")
            password = st.text_input("Enter Password",type='password')

            if st.button("Login"):
                result = login_user(username,password)
                if result:
                    st.success("Logged In as {}".format(username)) 
                    st.info("reload the page and select an option from the menu")
                else:
                    st.warning("Incorrect Username/Password")


        if choice == "SignUp":
            fullname = st.text_input("Enter Full Name")
            email = st.text_input("Enter Email")
            country = st.text_input("Enter Country")
            mobile = st.text_input("Enter Phone Number")
            password = st.text_input("Enter Password",type='password')
            security_key = st.text_input("Enter Security Question: which city were you born")

            logged_in='true'
            if st.button("Signup"): 
                add_userdata(fullname,email,country,mobile,password,security_key)
                st.success("You have successfully created a valid Account") 
                st.info("Go to Login Menu to login") 

if __name__ == "__main__":
    main()