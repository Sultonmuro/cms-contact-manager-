from django.shortcuts import render,redirect,get_object_or_404
from .models import Contact
from .forms import ContactForm
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.serializers import serialize
import json
def contact_list(request):
    contacts = Contact.objects.all()

    context = {
        'contacts':contacts,
        'page_title':'Список контактов'
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