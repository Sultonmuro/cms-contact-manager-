from django.shortcuts import render,redirect,get_object_or_404
from .models import Contact
from .forms import ContactForm
def contact_list(request):
    contacts = Contact.objects.all()

    context = {
        'contacts':contacts,
        'page_title':'Список контактов'
    }
    return render(request,'contacts/contact_list.html',context)
    
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