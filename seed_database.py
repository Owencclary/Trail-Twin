import csv
import crud
import model
import server
import requests
from model import db

app = server.app
model.connect_to_db(app)

API_KEY = 'AIzaSyDwQOKBTzLzux_ELP9WiR1GMWfWrnIjDD8' 
url = 'https://maps.googleapis.com/maps/api/geocode/json'

# Creates database
with app.app_context():
    db.create_all()
    users = []
    n = 1

    # Read csv rows
    with open("data/addresses.csv", 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            address = row

            # Geocode address
            params = {"address": address, "key": API_KEY}
            response = requests.get(url, params=params).json()

            # Get lat and long of address 
            if response['status'] == 'OK':
                geometry = response['results'][0]['geometry']
                latitude = geometry['location']['lat']
                longitude = geometry['location']['lng']

                # genderate user info 
                username = str(n)
                email = f'user{n}@test.com'
                password = 'test'
                phone_number = f'123-456-123{n}'

                # Read profile photo CSV and add profile photo 
                with open("data/profile_photos.csv", 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    for current_row_number, row in enumerate(reader, start=1):
                        if current_row_number == n:
                            image_url = row[0]
                            profile_photo = image_url.replace("{", "").replace("}", "")
                            print(f'PROFILE PHOTO: {profile_photo}')

                # add two kinds of photos, bios and activies
                if n % 2 == 0:
                    first_name = 'John'
                    last_name = 'Doe'
                    gender = 'male'
                    age = n * 3
                    dob = "2003-12-12"
                    bio = 'Crazy downhill mountain biker from the pnw! Lets go ride!'
                    activity_1 = "Mountain Biking"
                    activity_2 = "Backpacking"
                else:
                    first_name = 'Sara'
                    last_name = 'Smith'
                    gender = 'female'
                    age = n * 2
                    dob = "2003-12-12"
                    bio = 'Total ski bum livin out the van!'
                    activity_1 = "Skiing"
                    activity_2 = "Running"
                
                user = crud.create_user(first_name, last_name, username, email, password, phone_number, address, gender, dob, bio, latitude, longitude)
                users.append(user)
                crud.add_activity(user.user_id, activity_1) 
                crud.add_activity(user.user_id, activity_2)  
                crud.create_cloudinary_photo(user.user_id, image_url, "_profile_photo")
                crud.create_cloudinary_photo(user.user_id,  "https://c02.purpledshub.com/uploads/sites/39/2022/10/Fox-DHX-Factory-rear-mountain-bike-shock-2-3e0ee7f.jpg?w=1029&webp=1", "_slideshow_photo_1")
                crud.create_cloudinary_photo(user.user_id,  "https://columbia.scene7.com/is/image/ColumbiaSportswear2/10-11_42909_C_C_OG_10Benefits_SkiSnowboard_Thumbnail?scl=1", "_slideshow_photo_2")
                crud.create_cloudinary_photo(user.user_id,  "https://publisher-ncreg.s3.us-east-2.amazonaws.com/pb-ncregister/swp/hv9hms/media/2022090222090_bd7f8fbd3ed58a2a438346439affa9e7decff92a177e952c46d787dcdbefaac4.jpg", "_slideshow_photo_3")

                n += 1
            else:
                print(f"Geocoding failed for address: {address}")

    model.db.session.add_all(users)
    model.db.session.commit()
