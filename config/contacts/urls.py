from django.urls import path
from . import views
app_name ='contacts'

urlpatterns = [
    path('', views.contact_list, name='contact_list'), # <--- CORRECTED: This now resolves to /contacts/
    path('add/', views.add_contact, name='add_contact'), # Resolves to /contacts/add/
    path('edit/<int:pk>/', views.edit_contact, name='edit_contact'), # Resolves to /contacts/edit/PK/
    path('delete/<int:pk>/', views.delete_contact, name='delete_contact'), # Resolves to /contacts/delete/PK/
    path('about/', views.about, name='about'), # Resolves to /contacts/about/
    path('signup/', views.signup, name='signup'), # Resolves to /contacts/signup/
    path('chatbot/', views.chatbot_view, name='chatbot_view'), # Resolves to /contacts/chatbot/
    path('api/contacts-by-date/', views.get_contacts_by_date, name='contacts_by_date_api'), # Resolves to /contacts/api/contacts-by-date/
   
]
