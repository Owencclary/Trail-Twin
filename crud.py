from model import db, User, Friendship, Activity, Message, connect_to_db
from geopy.distance import geodesic
from datetime import datetime
import cloudinary.uploader
import cloudinary.api
import cloudinary

cloudinary.config(
    cloud_name="dsp4ua5sr",
    api_key="684521112869916",
    api_secret="W0afXudkKDLhrSC0pRWHD0NqWU8",
    secure=True,
)
cloud_name="dsp4ua5sr"


# Create SQL
# --------------------------------
def create_user(first_name, last_name, username, email, password, phone_number, address, gender, dob, bio, latitude, longitude):
    age = calculate_age(dob)
    user = User(first_name=first_name, last_name=last_name, username=username, email=email, password=password, phone_number=phone_number, address=address, age=age, gender=gender, dob=dob, bio=bio, latitude=latitude, longitude=longitude)
    db.session.add(user)
    db.session.commit()
    return user

def create_friendship(sender_id, receiver_id):
    existing_friendship = friend_request_exists(sender_id, receiver_id)
    print(f'EXISTING FRIENDSHIP: {existing_friendship}')
    if existing_friendship:
        return "friendship already exists"
    else:
        # Creates the friendship
        friendship = Friendship(user_id = sender_id, friend_id = receiver_id)
        db.session.add(friendship)
        db.session.commit()
        print(f'FRIENDSHIP: {friendship}')
        return friendship

def add_activity(user_id, activity):
    activity_instance = Activity(user_id=user_id, activity_name=activity)
    db.session.add(activity_instance)
    db.session.commit()
    return activity_instance

def create_message(sender_id, receiver_id, content):
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()
    return message

# Read SQL data
# --------------------------------
def friend_request_exists(user_id, friend_id):

    # Find friendship where friend request column is true
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    friendship_swapped = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id, friend_request=True).first()

    if friendship:
        return friendship
    if friendship_swapped:
        return friendship_swapped



def get_friend_requests(user_id):

    # Retrieve friend requests where user_id is the friend_id
    friend_requests = Friendship.query.filter_by(friend_id=user_id, friend_request=True).all()

    # Return the user of each friend id in the filterd friendships
    return [get_user(request.user_id) for request in friend_requests]


def get_friends_with_chats(user_id):

    # find friends where user_id is saved in the user_id column and friend_id culumn and chat boolean true
    user_friends_chat = Friendship.query.filter_by(user_id=user_id, chat=True).all()
    friend_friends_chat = Friendship.query.filter_by(friend_id=user_id, chat=True).all()

    # find the ids in each friendship 
    user_ids = [friend.friend_id for friend in user_friends_chat]
    friend_ids = [friend.user_id for friend in friend_friends_chat]

    # Remove duplicates
    all_friend_ids = list(set(user_ids + friend_ids))

    # Return the user of each friend id in the filterd friendships
    return [get_user(friend_id) for friend_id in all_friend_ids]


def get_friends(user_id):

    # friend friends where user_id is is saved in the user_id column and friend_id culumn
    user_friends = Friendship.query.filter_by(user_id=user_id, friend_request=False).all()
    friend_friends = Friendship.query.filter_by(friend_id=user_id, friend_request=False).all()

    # find the ids in each friendship 
    user_ids = [friend.friend_id for friend in user_friends]
    friend_ids = [friend.user_id for friend in friend_friends]

    # Remove duplicates
    all_friend_ids = list(set(user_ids + friend_ids))

    # Return the user of each friend id in the filterd friendships
    return [get_user(friend_id) for friend_id in all_friend_ids]

def get_friendship(user_id, friend_id):
    # Check for existing friendships in both directions
    friendship = Friendship.query.filter_by(user_id=user_id, friend_id=friend_id).first()
    friendship_with_ids_swapped = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id).first()
    
    if friendship:
        return friendship
    if friendship_with_ids_swapped:
        return friendship_with_ids_swapped

def get_all_users():
    return User.query.all()
    
def get_all_users_besides_user(user_id):
    return User.query.filter(User.user_id != user_id).all()

def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")
    return user

def get_user_by_username(username):
    user = User.query.filter(User.username==username).first()
    print(f'USER: {user}')
    if user:
        return user
    else:
        return "User not found"

def get_user_by_email(email):
    return User.query.filter(User.email == email).first()

def activities_dicitonary():
    activities = get_all_activities()
    activities_dictionary = {}
    for activity in activities:
        user_id = activity.user_id
        activity_name = activity.activity_name
        if user_id in activities_dictionary:
            activities_dictionary[user_id].append(activity_name)
        else:
            activities_dictionary[user_id] = [activity_name]
    return activities_dictionary

def search_users_with_filter(user_id, radius_mi, min_age, max_age, activity_input, gender):
    user = User.query.get(user_id)
    user_location = (user.latitude, user.longitude)
    all_users = get_all_users_besides_user(user_id)

    # Radius filter
    filtered_users_1 = []
    for filtered_user in all_users:
        filtered_user_location = (filtered_user.latitude, filtered_user.longitude)
        filtered_user_and_user_distance = geodesic(user_location, filtered_user_location).kilometers
        distance_mi = filtered_user_and_user_distance / 1.60934
        print(f'DISTANCE MI: {distance_mi}, RAIDUS_MI: {radius_mi}')
        if distance_mi <= float(radius_mi):
            filtered_users_1.append(filtered_user)
    print(f'FILTER 1: {filtered_users_1}')

    # Activity filter
    filtered_users_2 = []
    if activity_input == 'All' or activity_input == 'Choose...':
        filtered_users_2 = list(filtered_users_1)
    else: 
        for filtered_user in filtered_users_1:
            filtered_user_activities = get_activities(filtered_user.user_id)
            print(f'ACTIVITIES: {filtered_user_activities}')
            for activity in filtered_user_activities:
                if activity.activity_name == activity_input:
                    filtered_users_2.append(filtered_user)
    print(f'FILTER 2: {filtered_users_2}')

    # Age filter
    filtered_users_3 = []
    for filtered_user in filtered_users_2:
        if filtered_user.age is None or int(min_age) <= filtered_user.age <= int(max_age):
            filtered_users_3.append(filtered_user)

    print(f'FILTER 3: {filtered_users_3}')

    # Gender filter
    final_filter = []
    if gender == 'All' or gender == 'Choose...':
        final_filter = list(filtered_users_3)
    else: 
        for filtered_user in filtered_users_2:
            if filtered_user.gender == gender:
                final_filter.append(filtered_user)

    print(f'FILTER 4: {final_filter}')


    return final_filter
            
def get_activities(user_id):
    activities = Activity.query.filter(Activity.user_id == user_id).all()
    return activities

def get_all_activities():
    activities = Activity.query.all()
    return activities


# Update SQL Data
# --------------------------------
def edit_profile(user_id, bio):
    user = User.query.get(user_id)
    user.bio = bio
    db.session.commit()

def accept_friend_request(user_id, friend_id):
    friend_request = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id, friend_request=True).first()
    if friend_request:
        friend_request.friend_request = False
        db.session.commit()
        print(f'FRIEND_REQUEST: {friend_request} {friend_request.friend_request}')
        return 'Friend Accepted'
    else: 
        return 'Friendship not found'

# Function to decline friend requests
def decline_friend_request(user_id, friend_id):
    friendship_request = Friendship.query.filter_by(user_id=friend_id, friend_id=user_id, friend_request=True).first()

    if friendship_request:
        db.session.delete(friendship_request)
        db.session.commit()
        return "Friend request declined successfully."
    else:
        return "Friend request not found."
    
# Updates friendship chat boolean
def create_chat_with_friend(user_id, friend_id):
    friendship = get_friendship(user_id, friend_id)
    friendship.chat = True
    db.session.commit()
    
    return "Chat created"

# Updates users age
def update_age(user_id):
    user = User.query.get(user_id)
    user.age = calculate_age(user.dob)
    db.session.commit()

    return "Age updated"


# Delete SQL Data
# --------------------------------
def remove_activity(activity_id):
    activity = Activity.query.get(activity_id)  
    if activity:
            db.session.delete(activity)
            db.session.commit()
            return "success"
    return "failed"

def remove_friend(user_id, friend_id):
    friendship = get_friendship(user_id, friend_id)
    if friendship:
            db.session.delete(friendship)
            db.session.commit()
            return "success"
    return "failed"

# -------------------------------------------------------------------------------- #
# Cloudinary database
# -------------------------------------------------------------------------------- #


# Create cloudinary images
# --------------------------------
def create_cloudinary_photo(user_id, photo, photo_type):
    user = User.query.get(user_id)
    print(f'PHOTO: {photo}')
    print(f'ID: {user.username.lower()}{photo_type}')
    public_id = f"{user.username.lower()}{photo_type}"
    # Destroy existing photo if it exists
    try:
        res = cloudinary.uploader.destroy(public_id=public_id)
        print(res)
    except:
        print(res)
    # Upload the new photo
    try: 
        print(f'PUBLIC_ID: {public_id}')
        res = cloudinary.uploader.upload(photo, public_id=public_id)
        print(res)
        return 'success'
    except:
        return 'failed'


# Read cloundary images
# --------------------------------
# get all cloudinary photos with user_id with "_slideshow_photo_1,2,3"
def get_cloudinary_slideshow_photos(user_id):
    user = get_user(user_id)
    print(f'USER {user}')
    print(f'USER ID: {user.username.lower()}_slideshow_photo_1')
    slideshow_list = []
    slideshow_list.append(f"https://res.cloudinary.com/{cloud_name}/image/upload/{user.username.lower()}_slideshow_photo_1.jpg")
    slideshow_list.append(f"https://res.cloudinary.com/{cloud_name}/image/upload/{user.username.lower()}_slideshow_photo_2.jpg")
    slideshow_list.append(f"https://res.cloudinary.com/{cloud_name}/image/upload/{user.username.lower()}_slideshow_photo_3.jpg")
    print(f'SLIDESHOW LIST: {slideshow_list}')
    return slideshow_list

# get cloudinary photo with user_id and "-profile_photo"
def get_cloudinary_profile_photo(user_id):
    user = User.query.get(user_id)
    public_id = user.username.lower() + "_profile_photo"
    try:
        profile_photo = f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.jpg"
        return profile_photo
    except:
        return "Photo not found"

# get all cloudinary photos with all the users user_ids plus "-profile_photo"
def get_cloudinary_profile_photo_dictionary(users):
    profile_photo_dict = {}
    for user in users:
        public_id = user.username.lower() + "_profile_photo"
        profile_photo_dict[user.user_id] = [f"https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}.jpg"]
    return profile_photo_dict




# Other
# --------------------------------
def calculate_age(birthdate):
    # Convert birthdate string to a datetime object
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d")
    
    # Get the current date
    current_date = datetime.now()
    
    # Calculate the age
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))
    
    return age


def is_valid_password(password):
    # Check if the password meets the following requirements:
    # - At least 8 characters
    if len(password) >= 8:
        return True
    else:
        return False

if __name__ == '__main__':
    from server import app
    connect_to_db(app)