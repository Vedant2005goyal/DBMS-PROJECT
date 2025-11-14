#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os 
import json
import mysql.connector
from typing import List, Optional, Tuple, Dict, Any, cast
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("Warning: face_recognition not available in Face_Recognition.py")
import numpy as np
from numpy.typing import NDArray
import cv2 as cv
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available")


# In[3]:


class FaceRegistration:
    def __init__(self):
        try:
            from config import Config
            self.mysql_connection=mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                port=Config.DB_PORT
            )
            self.cursor=self.mysql_connection.cursor(dictionary=True)
            print('Database connected succesfully!!')
            self.students_photo_dir:str=''
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            raise

    def extract_embeddings(self,image_path:str):
        if not FACE_RECOGNITION_AVAILABLE:
            return None, None
        image=face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image) 
        if len(face_locations) == 0:
            print("No face detected in the image!")
            return None, None    
        if len(face_locations) > 1:
                print(f"{len(face_locations)} faces detected. Using the largest face.")
                face_locations = [max(face_locations, key=lambda loc: (loc[2]-loc[0])*(loc[1]-loc[3]))]
        face_encodings = face_recognition.face_encodings(image, face_locations) if FACE_RECOGNITION_AVAILABLE else []    
        if len(face_encodings) > 0:
            print(f"Embeddings extracted successfully")
            return face_encodings[0], face_locations[0]
        else:
            print("Could not generate embeddings")
            return None, None

    def face_with_bbox(self,image_path:str,face_locations:List[Tuple[int,int,int,int]]):
        image=cv.imread(image_path)
        if image is None:
            print("Could not read image")
            return
        img_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        for (top, right, bottom, left) in face_locations:
            print(f"Top: {top}, Right: {right}, Bottom: {bottom}, Left: {left}")
            img_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            cv.rectangle(img_rgb, (left, top), (right, bottom), (0, 255, 0), 3)
        plt.imshow(img_rgb)
        plt.show()

    def get_info(self,User_ID):
        query="SELECT u.User_ID,u.Name,u.Email FROM User u WHERE u.User_ID = %s"
        self.cursor.execute(query, (User_ID,))
        student: Optional[Dict[str, Any]] = self.cursor.fetchone() # type: ignore
        if student:
            print(f"User Found: {student['Name']}")
            return student
        else:
            print(f"User with User_ID {User_ID} not found")
            return None

    def check_existing_embeddings(self,User_ID):
        query="SELECT f.Face_ID,f.Photo_Path from Face_Embeddings f WHERE f.User_ID=%s LIMIT 1"
        self.cursor.execute(query, (User_ID,))
        # cast the fetched row to an optional dict for proper typing
        result = cast(Optional[Dict[str, Any]], self.cursor.fetchone())
        if result:
            print(f"Face embedding already exists for User_ID: {User_ID}")
            print(f"Face_ID: {result['Face_ID']}, Photo: {result['Photo_Path']}")
            return result
        return None


    def insert_data_database(self,User_ID,face_encodings:list[NDArray],Photo_Path:str):
        embeddings=face_encodings.tolist() # type: ignore
        embeddings_json=json.dumps(embeddings)
        sql="INSERT INTO Face_Embeddings (User_ID, Face_Encoding, Photo_Path) VALUES (%s, %s, %s)"
        self.cursor.execute(sql,(User_ID, embeddings_json, Photo_Path))
        self.mysql_connection.commit()
        face_id=self.cursor.lastrowid
        return face_id

    def register_person(self,User_ID,image_path,show_preview=False):
        if not os.path.exists(image_path):
            return False, "Image path does not exist."
        user = self.get_info(User_ID)
        if not user:
            return False, f"User ID {User_ID} not found in database."
        existing = self.check_existing_embeddings(User_ID)
        if existing:
            message = f"User ID {User_ID} ({user.get('Name', '')}) already has a face registered."
            print(message)
            return False, message
        face_encoding, face_location = self.extract_embeddings(image_path)
        if face_encoding is None:
            return False, "No face detected in the provided image."
        if show_preview:
            self.face_with_bbox(image_path, [face_location]) # type: ignore
        self.insert_data_database(User_ID,face_encoding,image_path) # type: ignore
        message= f"{User_ID} added to the database"
        print(message)
        return True,message

    def delete_face(self,User_ID)->None:
        existing=self.check_existing_embeddings(User_ID)
        if existing:
            x=input("Are you sure you want to delete it from the database: Yes Y,No N")
            if(x=="Y"|x=="y"): # type: ignore
                sql = "DELETE FROM Face_Embeddings WHERE User_ID = %s"
                self.cursor.execute(sql, (User_ID,))
                self.mysql_connection.commit()
            print(f"{User_ID} deleted successfully!!")


# In[4]:


if __name__ == "__main__":
    facesys=FaceRegistration()
    dir='/Users/vedantgoyal/Desktop/CODING/dbms_project/Celebrity Faces Dataset'
    content=os.listdir(dir)
    celebrity_id_map = {
        'Angelina Jolie': 1,
        'Brad Pitt': 2,
        'Denzel Washington': 3,
        'Hugh Jackman': 4,
        'Jennifer Lawrence': 5,
        'Johnny Depp': 6,
        'Kate Winslet': 7,
        'Leonardo DiCaprio': 8,
        'Megan Fox': 9,
        'Natalie Portman': 10,
        'Nicole Kidman': 11,
        'Robert Downey Jr': 12,
        'Sandra Bullock': 13,
        'Scarlett Johansson': 14,
        'Tom Cruise': 15,
        'Tom Hanks': 16,
        'Will Smith': 17,
        'Osho': 18,
        'Khalil Gibran': 19,
        'Aditya Gupta': 20,
        'Vedant Gpyal': 21,
        'Rushil Upadhhyay': 22,
        'Nikunj Garg': 23,
        'Kusham Lata': 24
    }
    k:int=1
    for i in content:
        img_dirs=os.path.join(dir,i)
        if os.path.isdir(img_dirs) and i in celebrity_id_map:
            current_user_id=celebrity_id_map[i]
            if os.path.isdir(img_dirs) and not i.startswith('.'):
                img_files=os.listdir(img_dirs)
                for j in img_files:
                    if j.lower().endswith(('.png','.jpeg','.jpg')):
                        full_image_path=os.path.join(img_dirs,j)
                        print(full_image_path)
                        facesys.register_person(User_ID=current_user_id,image_path=full_image_path,show_preview=True)
                        k+=1



# In[ ]:




