from . import views
from django.urls import path

urlpatterns = [
    path('',views.home,name='home'),
    path('register/',views.RegisterUser,name='register'),
    path('login/',views.Login,name='login'),
    path('logout/',views.Logout,name='logout'),
    path('<str:room_id>/',views.home,name='home'),
    path('<str:room_id>/send_message/',views.send_message,name='send_message'),
    path('<str:room_id>/upload_image/',views.upload_image,name='upload_image'),
    

]