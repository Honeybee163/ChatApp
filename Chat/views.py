from django.shortcuts import render, redirect
from .form import UserForm, ContactForm,MessageForm,ImageForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import User, Contact, Message, ChatRoom
from django.db.models import Q



def RegisterUser(request):
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserForm()
    return render(request, "register.html", {"form": form})







def Login(request):
    # If user is already authenticated, redirect to home
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to the 'next' parameter if provided, otherwise home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})









def Logout(request):
    logout(request)
    return redirect("login")











@login_required
def home(request, room_id=None):
    # get logged in user
    user1 = request.user
    
    # get contact and message form
    form = ContactForm()
    message_form = MessageForm()

    # Fetch all contacts where current user is either the owner
    # OR has been added as a contact by someone else
    contacts = Contact.objects.filter(
        Q(owner=user1) | Q(contact_user=user1)
    )

    # Prepare a dictionary of room_ids for each contact
    selected_room = None
    messages = []
    chat_user = None
    room_ids = {}
    last_messages = {}

    for contact in contacts:
        # Determine the "other" user in this contact,
        # so that it works correctly from both sides
        if contact.owner == user1:
            other_user = contact.contact_user
        else:
            other_user = contact.owner

        # Attach for template usage (contact.other_user)
        contact.other_user = other_user

        # Create/fetch a stable room_id based on sorted user ids
        if user1.id < other_user.id:
            room_id_val = f"{user1.id}-{other_user.id}"
            room_user1 = user1
            room_user2 = other_user
        else:
            room_id_val = f"{other_user.id}-{user1.id}"
            room_user1 = other_user
            room_user2 = user1

        room, created = ChatRoom.objects.get_or_create(
            room_id=room_id_val,
            defaults={"user1": room_user1, "user2": room_user2}
        )

        room_ids[other_user.id] = room_id_val

        last_msg = Message.objects.filter(room=room).order_by("-timestamp").first()
        last_messages[other_user.id] = last_msg

    # Handle adding a new contact
    if request.method == "POST" and "submit_contact" in request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get("phone_number")
            email = form.cleaned_data.get("email")

            if not phone_number and not email:
                return HttpResponse("Please enter email or phone number")

            contact_user = None
            if phone_number:
                contact_user = User.objects.filter(phone_number=phone_number).first()
            if not contact_user and email:
                contact_user = User.objects.filter(email=email).first()
            if not contact_user:
                return HttpResponse("User not registered")
            if contact_user == request.user:
                return HttpResponse("You cannot add yourself")
            if Contact.objects.filter(owner=user1, contact_user=contact_user).exists():
                return HttpResponse("This contact already exists")

            Contact.objects.create(owner=user1, contact_user=contact_user)

            # Recompute room_id for the new contact
            user2 = contact_user
            if user1.id < user2.id:
                room_id_val = f"{user1.id}-{user2.id}"
                room_user1 = user1
                room_user2 = user2
            else:
                room_id_val = f"{user2.id}-{user1.id}"
                room_user1 = user2
                room_user2 = user1

            room, _ = ChatRoom.objects.get_or_create(
                room_id=room_id_val,
                defaults={"user1": room_user1, "user2": room_user2}
            )

            # After successfully adding a contact, redirect so that
            # contacts, room_ids, and other_user mapping are rebuilt cleanly
            return redirect("home", room_id=room_id_val)
            
    
    # Load messages if room_id is provided
    if room_id:
        try:
            selected_room = ChatRoom.objects.get(room_id=room_id)
            messages = Message.objects.filter(room=selected_room).order_by('timestamp')
            
            # Determine the other user in the chat
            if selected_room.user1 == user1:
                chat_user = selected_room.user2
            else:
                chat_user = selected_room.user1
        except ChatRoom.DoesNotExist:
            pass
    
    return render(request, "contact.html", {
        "form": form,
        "message_form": message_form,
        "contacts": contacts,
        "room_ids": room_ids,
        "selected_room": selected_room,
        "messages": messages,
        "chat_user": chat_user,
        "current_room_id": room_id,
        "last_messages": last_messages, 
    })











@login_required
def send_message(request, room_id):
    if request.method == "POST":
        form = MessageForm(request.POST)
        image = request.FILES.get("image")

        # Allow either text, image, or both
        if form.is_valid() or image:
            text = form.cleaned_data.get("text") if form.is_valid() else ""
            sender = request.user
            try:
                room = ChatRoom.objects.get(room_id=room_id)
                Message.objects.create(room=room, sender=sender, text=text or "", image=image)
                return redirect("home", room_id=room_id)
            except ChatRoom.DoesNotExist:
                return redirect("home")
    return redirect("home", room_id=room_id)





@login_required
def upload_image(request, room_id):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data.get("image")
            text = form.cleaned_data.get("text") or ""  # optional text with image
            sender = request.user

            # Get room or 404
            room = get_object_or_404(ChatRoom, room_id=room_id)

            # Save message
            Message.objects.create(room=room, sender=sender, image=image, text=text)

            # Redirect to chat page
            return redirect("home", room_id=room_id)
        else:
            # Optional: show error if invalid
            return redirect("home", room_id=room_id)
    return redirect("home", room_id=room_id)