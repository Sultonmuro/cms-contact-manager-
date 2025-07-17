from django.shortcuts import render,redirect,get_object_or_404
from .models import Contact
from .forms import ContactForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.serializers import serialize
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json
from django.contrib.auth.decorators import login_required
import os
import requests
from django.conf import settings
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('contacts:contact_list')
    else:
        form = UserCreationForm()
    context = {
        'form':form,
        'page_title': 'Регистрация',
        'submit_button_text': 'Зарегистроваться'
    }
    return render(request,'contacts/signup.html',context)
@login_required
def contact_list(request):
    contacts = Contact.objects.all().order_by('name')
    
    query = request.GET.get('q')

    if query:
        contacts = contacts.filter(
            Q(name__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(email__icontains=query)
        )
    paginator = Paginator(contacts,9)
    page_number = request.GET.get('page')
    try:
        contacts = paginator.page(page_number)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    context = {
        'contacts':contacts,
        'page_title':'Список контактов',
        'search_query': query if query else '',
    }
    return render(request,'contacts/contact_list.html',context)
def main_page(request):
    total_contacts = Contact.objects.count()
    today = timezone.localdate()
    contacts_created_today = Contact.objects.filter(
        created_at__date=today
    ).count()
    contacts_before_today = total_contacts - contacts_created_today
    context = {
        'page_title': "Менеджер контактов",
        'total_contacts':total_contacts,
        'contacts_created_today':contacts_created_today,
        'contacts_created_before_today': contacts_before_today,
    }
    return render(request,'contacts/main_page.html',context)
@login_required
def get_contacts_by_date(request):
    seletected_date_str = request.GET.get('date')
    contacts_on_date = []

    if seletected_date_str:
        try:
            selected_date = timezone.datetime.strptime(seletected_date_str,'%Y-%m-%d').date()

            contacts_on_date = list(Contact.objects.filter(created_at__date=selected_date).values('id','name','phone_number','email','created_at'))
        
            for contact in contacts_on_date:
                if contact['created_at']:
                    contact['created_at'] = contact['created_at'].isoformat()
        except ValueError:
             return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e) },status=500)
    return JsonResponse({'contacts': contacts_on_date})

                    
def about(request):
    
    context = {
        'page_title': 'Наш Менеджер контактов'
    }

    return render(request,'contacts/about.html',context)
@login_required
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/contacts/')
    else:
        form = ContactForm()
    context ={
        'form': form,
        'page_title': 'Добавить новый контакт',
        'submit_button_text': 'Добавить контакт',
    }
    return render(request,'contacts/add_contact.html',context)
@login_required
def edit_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('/contacts/')
    else:
            form = ContactForm(instance=contact)
    
    context = {
        "form": form,
        'page_title': f'Редактировать контакты: {contact.name}',
        'submit_button_text': 'Сохранить изменения',
    }
    return render(request,'contacts/edit_contact.html',context)
@login_required
def delete_contact(request,pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect('/contacts/')
    context = {
        'contact': contact,
        'page_title': f"Удалить контакт: {contact.name}?"
    }
    return render(request,'contacts/contact_confirm_delete.html',context)


# @login_required
# def chatbot_view(request):
#      print("DEBUG: chatbot_view accessed.")
#      if request.method == 'POST':
#         user_message = request.POST.get('message')
#         print(f"DEBUG: POST request received. User message: '{user_message}'")

#         if not user_message:
#             print("DEBUG: No message provided in POST request.")
#             return JsonResponse({'error': 'No message provided'}, status=400)

#         api_key = settings.OPENAI_API_KEY
#         api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

#         headers = {
#             "Content-Type": "application/json",
#         }
#         payload = {
#             "contents": [{"role": "user", "parts": [{"text": user_message}]}]
#         }
#         print(f"DEBUG: Payload for API call: {payload}")
#         # Be careful not to print the full API key in logs in production
#         print(f"DEBUG: API Key (first 5 chars): {api_key[:5]}... (length: {len(api_key)})") 

#         try:
#             print(f"DEBUG: Attempting to send request to {api_url}")
#             response = requests.post(f"{api_url}?key={api_key}", headers=headers, json=payload, timeout=30) # Added timeout
#             print(f"DEBUG: API response status code: {response.status_code}")
#             print(f"DEBUG: Raw API response text: {response.text}") # Print raw text for all responses

#             response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
#             ai_response_data = response.json()
#             print(f"DEBUG: Parsed AI response data (JSON): {ai_response_data}")
            
#             ai_text = ""
#             if ai_response_data and ai_response_data.get('candidates'):
#                 for candidate in ai_response_data['candidates']:
#                     if candidate.get('content') and candidate['content'].get('parts'):
#                         for part in candidate['content']['parts']:
#                             if part.get('text'):
#                                 ai_text += part['text']
#                                 break
#                     if ai_text:
#                         break

#             if not ai_text:
#                 print("DEBUG: No text found in AI response candidates. Response structure might be unexpected.")
#                 ai_text = "Извините, я не смог получить ответ от ИИ."

#             print(f"DEBUG: Final AI response text to send to frontend: '{ai_text}'")
#             return JsonResponse({'response': ai_text})

#         except requests.exceptions.Timeout:
#             print("DEBUG: API Request timed out.")
#             return JsonResponse({'error': "Превышено время ожидания ответа от ИИ. Пожалуйста, попробуйте снова."}, status=504) # Gateway Timeout
#         except requests.exceptions.RequestException as e:
#             print(f"DEBUG: API Request failed: {e}")
#             # If response exists, print its text for more context
#             if 'response' in locals() and response is not None:
#                 print(f"DEBUG: Failed API response text: {response.text}")
#             return JsonResponse({'error': f"Ошибка при обращении к ИИ: {e}"}, status=500)
#         except json.JSONDecodeError:
#             print(f"DEBUG: Failed to decode JSON from AI response. Response text: {response.text}")
#             return JsonResponse({'error': "Неверный формат ответа от ИИ."}, status=500)
#         except Exception as e:
#             print(f"DEBUG: An unexpected error occurred: {e}")
#             return JsonResponse({'error': f"Произошла непредвиденная ошибка: {e}"}, status=500)

#     # For GET request, render the chatbot HTML page
#      context = {
#         'page_title': 'OpenAi Chatbot',
#     }
#      print("DEBUG: Rendering chatbot.html for GET request.")
#      return render(request, 'contacts/chatbot.html', context)