from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11, unique=True)
    
    
    
# Contact
# owner (FK → User) → the one who is saving contacts
# contact_user (FK → User) → the registered user being added as a contact
# created_at

class Contact(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_contacts")
    contact_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_by")
    created_at = models.DateTimeField(auto_now_add=True)
    
    
# 1. Create ChatRoom Model
# Since this is one-to-one chat (contacts based):
# room_id
# user1
# user2
# created_at
# 📌 Ensure only 1 room exists between 2 users.
class ChatRoom(models.Model):
    room_id = models.CharField(max_length=100, primary_key=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user2")
    created_at = models.DateTimeField(auto_now_add=True)
    

# 2. Create Message Model
# Message
# room (FK)
# sender (FK User)
# text
# timestamp
# is_read (optional)
# Goal: Messages can be stored and linked to a chat room.

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    image=models.ImageField(upload_to='images/', null=True, blank=True)