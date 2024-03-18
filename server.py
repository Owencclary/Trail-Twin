from flask import Flask, render_template, request, session, flash, redirect, jsonify
from flask_socketio import SocketIO, emit
from jinja2 import StrictUndefined
from model import connect_to_db, db
import requests
import crud

app = Flask(__name__)
app.secret_key = "OwenClary"
app.jinja_env.undefined = StrictUndefined
socketio = SocketIO(app)

GMAPS_API_KEY = 'AIzaSyDwQOKBTzLzux_ELP9WiR1GMWfWrnIjDD8' 
GMAPS_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

# Real-time chat
@socketio.on('private_message')
def handle_private_message(msg):
        
    sender_id = session.get('user')
    receiver_id = msg['receiver_id']
    content = msg['message']

    # Store the message in the database
    crud.create_message(sender_id, receiver_id, content)

    # Emit the message to the sender and receiver
    emit('private_message_sender', {'user_id': sender_id, 'message': content}, room=sender_id)
    emit('private_message_receiver', {'user_id': sender_id, 'message': content}, room=receiver_id)

# Initial page load
@app.route('/')
def login():
    return render_template('login.html')

# Route to users settings page
@app.route('/settings')
def settings():
    return render_template('settings.html')

# Route to Inbox displays all chats with users profile photos
@app.route('/chats')
def chats():
    user_id = session.get('user')
    friends_with_chats = crud.get_friends_with_chats(user_id)
    friend_profile_photos = crud.get_cloudinary_profile_photo_dictionary(friends_with_chats)
    return render_template('chats.html', friends_with_chats=friends_with_chats, friend_profile_photos=friend_profile_photos)

# Route to accept friend requests to change the friend request boolean
@app.route('/accept_friend_request/<friend_id>')
def accept_friend_request(friend_id):
    user_id = session.get('user')
    crud.accept_friend_request(user_id, friend_id)
    return redirect('/friends')

# Route to decline friend requests to delete the friendship row
@app.route('/decline_friend_request/<friend_request_id>')
def decline_friend_request(friend_id):
    user_id = session.get('user')
    crud.decline_friend_request(user_id, friend_id)
    return redirect('/friends')

@app.route('/remove_friend/<friend_id>')
def remove_friend(friend_id):
    user_id = session.get('user')
    crud.remove_friend(user_id, friend_id)
    return redirect('/friends')

# Route to individual chatroom
@app.route('/chat/<friend_id>')
def chat(friend_id):
    user_id = session.get('user')
    res = crud.create_chat_with_friend(user_id, friend_id)
    print(f'RES: {res}')
    friendship = crud.get_friendship(user_id, friend_id)
    friend = crud.get_user(friend_id)
    profile_photo = crud.get_cloudinary_profile_photo(friend_id)
    return render_template('chat.html', friend=friend, profile_photo=profile_photo, friendship=friendship)

# Route to veiwing freind profile
@app.route('/friend/<friend_id>/<friend_request_status>')
def friend(friend_id, friend_request_status):
    friend = crud.get_user(friend_id)
    activities = crud.get_activities(friend_id)
    slideshow_list = crud.get_cloudinary_slideshow_photos(friend_id)
    return render_template('friend.html', friend=friend, activities=activities, slideshow_list=slideshow_list, friend_request_status=friend_request_status)

# Route to friendslist
@app.route('/friends')
def friends():
    user_id = session.get('user')
    friends = crud.get_friends(user_id)
    friend_requests = crud.get_friend_requests(user_id)
    friend_profile_photos = crud.get_cloudinary_profile_photo_dictionary(friends)
    friend_request_profile_photos = crud.get_cloudinary_profile_photo_dictionary(friend_requests)
    return render_template('friends.html', friend_profile_photos=friend_profile_photos, friends=friends, friend_requests=friend_requests, friend_request_profile_photos=friend_request_profile_photos)

# Gallery of all users
@app.route('/gallery')
def gallery():
    user_id = session.get('user')
    users = crud.get_all_users_besides_user(user_id)
    profile_photos = crud.get_cloudinary_profile_photo_dictionary(users)
    activities_dictionary = crud.activities_dicitonary()
    return render_template('gallery.html', users=users, activities_dictionary=activities_dictionary, radius=50, min_age=5, max_age=70, profile_photos=profile_photos)

# Gallery of all users with a filter applied
@app.route('/filtered_gallery', methods=['POST'])
def filtered_gallery():
    user_id = session.get('user')
    radius_mi = request.form.get("radius")
    min_age = request.form.get("min_age")
    max_age = request.form.get("max_age")
    activity = request.form.get("activity")
    gender = request.form.get("gender")
    activities_dictionary = crud.activities_dicitonary()
    filtered_users = crud.search_users_with_filter(user_id, radius_mi, min_age, max_age, activity, gender)
    profile_photos = crud.get_cloudinary_profile_photo_dictionary(filtered_users)
    return render_template('gallery.html', users=filtered_users, activities_dictionary=activities_dictionary, radius=radius_mi, min_age=min_age, max_age=max_age, activity=activity, profile_photos=profile_photos)


# Gallery of all users with a filter applied
@app.route('/username_search', methods=['POST'])
def username_search():
    username = request.form.get("username")
    user = crud.get_user_by_username(username)
    if user == "User not found":
        print("User not found")
        return redirect('/gallery')
    else:
        profile_photo = crud.get_cloudinary_profile_photo(user.user_id)
        activities_dictionary = crud.activities_dicitonary()
        profile_photos = {}
        profile_photos[user.user_id] = [profile_photo]
        users = []
        users.append(user)
        return render_template('gallery.html', users=users, activities_dictionary=activities_dictionary, radius=50, min_age=5, max_age=70, profile_photos=profile_photos)


# Load personal profile
@app.route('/profile')
def profile():
    user_id = session.get('user')
    user = crud.get_user(user_id)
    activities = crud.get_activities(user_id)
    profile_photo = crud.get_cloudinary_profile_photo(user_id)
    slideshow_list = crud.get_cloudinary_slideshow_photos(user_id)
    return render_template('profile.html', user=user, activities=activities, profile_photo=profile_photo, slideshow_list=slideshow_list)

# Edit profile
@app.route('/edit_profile')
def edit_profile():
    user_id = session.get('user')
    user = crud.get_user(user_id)
    activities = crud.get_activities(user_id)
    profile_photo = crud.get_cloudinary_profile_photo(user_id)
    slideshow_list = crud.get_cloudinary_slideshow_photos(user_id)
    return render_template('/edit_profile.html', user=user, activities=activities, profile_photo=profile_photo, slideshow_list=slideshow_list)

# Uploads inputed photo to cloudinary
@app.route('/add_photo/<photo_type>', methods=['POST'])
def add_photo(photo_type):
    user_id = session.get('user')
    print(f'PHOTO TYPE: {photo_type}')

    # Gets the type of photo from the HTML form
    photo = request.files.get(photo_type)

     # Ensure that photo is not None before proceeding
    if photo:
        # Error handling for create_cloudinary_photo function
        try:
            crud.create_cloudinary_photo(user_id, photo, photo_type)
            print("Photo uploaded successfully")
        except:
            print("Error uploading photo")
    else:
        print("No photo uploaded")

    return redirect('/edit_profile')


# Updates users profile features 
@app.route('/update_bio', methods=['POST'])
def update_bio():
    user_id = session.get('user')
    bio = request.form.get("bio")
    crud.edit_profile(user_id, bio)
    return redirect('/edit_profile')

# Removes users activity from the SQL 
@app.route('/remove_activity/<activity_id>')
def remove_activity(activity_id):
    user_id = session.get('user')
    if user_id: 
        status = crud.remove_activity(activity_id)
        if status == "success":
            return jsonify('success')             
    else:
        return jsonify('fail') 

# Add activity of interest
@app.route('/add_activity', methods=['POST'])
def add_activity():
    user_id = session.get('user')
    activity = request.form.get("activity")
    activities = crud.get_activities(user_id)
    for users_activity in activities:
        if users_activity.activity_name == activity:
            return redirect('edit_profile')
    crud.add_activity(user_id, activity)
    return redirect('edit_profile')

# Individual user profile
@app.route('/user/<user_id>')
def user(user_id):
    user = crud.get_user(user_id)
    activities = crud.get_activities(user_id)
    slideshow_list = crud.get_cloudinary_slideshow_photos(user_id)
    return render_template('user.html', user=user, activities=activities, slideshow_list=slideshow_list)

# Creates friend request
@app.route('/add_friend/<friend_id>')
def add_friend(friend_id):
    user_id = session.get('user')
    res = crud.create_friendship(user_id, friend_id)
    if res == "friendship already exists":
        flash('Friendship already exists')
        return redirect(f'/user/{friend_id}')
    else:
        flash("Friend request sent")
        return redirect(f'/user/{friend_id}')

# Account creation
@app.route('/create_account')
def create_account():
    return render_template('create_account.html')

# Registration
@app.route('/register', methods=['POST'])
def register():

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    phone_number = request.form.get("phone_number")
    address = request.form.get("address")
    gender = request.form.get("gender")
    dob = request.form.get("dob")
    bio = request.form.get("bio")
    profile_photo = request.files.get("profile_photo")
    slideshow_photo = request.files.get("profile_photo")

    # Geocode address
    params = {"address": address, "key": GMAPS_API_KEY}
    response = requests.get(GMAPS_URL, params=params).json()

    # Get latitude and longitude 
    if response['status'] == 'OK':
        geometry = response['results'][0]['geometry']
        latitude = geometry['location']['lat']
        longitude = geometry['location']['lng']

        # Check if email or username is taken
        existing_email = crud.get_user_by_email(email)
        exisiting_username = crud.get_user_by_username(username)
        if existing_email:
            flash("Email already in use, please try again.")
        else:
            if exisiting_username == "User not found":
                if password == confirm_password:
                    if crud.is_valid_password(password) == True:
                        # Create user
                        user = crud.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password, phone_number=phone_number, address=address, gender=gender, dob=dob, bio=bio, latitude=latitude, longitude=longitude)
                        crud.create_cloudinary_photo(user.user_id, profile_photo, "_profile_photo")
                        crud.create_cloudinary_photo(user.user_id, slideshow_photo, "_slideshow_photo_1")
                        flash('Account created, please log in')
                        return render_template('login.html')
                    else:
                        flash("Password does not meet the requirements.")
                else: 
                    flash('Passwords do not match')
            else: 
                flash("Username already in use, please try again.")
    else:
        flash("Invalid address, please try again.")

    return redirect('/create_account')

# Login
@app.route('/login', methods=['POST'])
def login_user():

    email = request.form.get("email")
    password = request.form.get("password")

    # Check if user exists
    user = crud.get_user_by_email(email)
    if user:
        if user.password == password:
            session["user"] = user.user_id
            crud.update_age(user.user_id)
            return redirect('/gallery')
        else:
            flash('Invalid password, please try again')
    else:
        flash('User not found, please try again')
    
    return render_template('login.html')

# Logout
@app.route("/logout")
def logout():
   del session["user"]
   return render_template("login.html") 


# Custom Error Page
@app.errorhandler(404)
def error_404(e): 
   return render_template("404.html") 
        

if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)
    


