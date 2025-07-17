from django.contrib import admin
from .models import Cards,SmsLog,CARD_STATUS
from import_export import resources,fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import DateTimeWidget
from django.contrib import messages
from datetime import datetime
import re
class CardResource(resources.ModelResource):
    expire = fields.Field(attribute='expire',column_name='expire')


    class Meta:
        model = Cards
        fields = ('card_number','owner','expire','phone_number','card_status','balance')

    def before_import_row(self, row, **kwargs):

        if 'card_number' in row and row['card_number']:
            row['card_number'] = re.sub(r'\D', '', str(row['card_number']))
            if len(row['card_number']) > 16:
                row['card_number'] = row['card_number'][:16]

        if 'expire' in row and row['expire']:
            expire_str = str(row['expire']).strip()

            match = re.match(r'(\d{1,2})[/\-](\d{2,4})',expire_str)
            if match:
                month = match.group(1).zfill(2)
                year = match.group(2)

                if len(year) ==4:
                    year = year[2:]
                row['expire'] = f"{month} / {year}"

            else:
                try:
                    dt_obj = datetime.strptime(expire_str, '%Y-%m-%d %H:%M:%S')
                    row['expire'] = dt_obj.strftime('%m/%y')
                except ValueError:
                    row['expire']
           # Clean phone_number: remove all non-digits and potentially truncate
        if 'phone_number' in row and row['phone_number']:
            phone_str = str(row['phone_number']).strip()
            # Remove all non-digit characters
            cleaned_phone = re.sub(r'\D', '', phone_str)
            row['phone_number'] = cleaned_phone[:20] 

        if 'balance' in row and row['balance']:
            balance_str = str(row['balance']).lower()
            balance_str = balance_str.replace('mlrd uzs','').replace(' ', '').replace(',', '')
            try:
                if 'mlrd' in str(row['balance']).lower():
                     value = float(balance_str) * 1_000_000_000 # Convert to billion
                else:
                    value = float(balance_str)
                row['balance'] = str(round(value, 2)) # Round to 2 decimal places and convert back to string for import
            except ValueError:
                row['balance'] = '0.00' # Default to 0 if parsing fails
          # Ensure status is one of the valid choices
        if 'card_status' in row and row['card_status']:
            status_upper = str(row['card_status']).upper()
            valid_statuses = [choice[0] for choice in CARD_STATUS]
            if status_upper not in valid_statuses:
                row['card_status'] = 'ACTIVE' # Default to ACTIVE if invalid status provided
    
        return super().before_import_row(row, **kwargs)
    def get_instance(self, instance_loader, row):
        try:
            return self.Meta.model.objects.get(card_number=row.get('card_number'))
        except self.Meta.model.DoesNotExist:
            return None
@admin.action(description='Send SMS to selected cards')
def send_sms_action(modeladmin, request, queryset):
    # In a real application, you would integrate with an SMS gateway here.
    # For this task, we're just simulating and logging.
    sent_count = 0
    log_messages = []

    for card in queryset:
        if card.phone_number:
            # Simulate sending SMS
            message_content = f"Dear {card.owner}, your card {card.card_number[-4:]} balance is {card.balance} UZS. Status: {card.get_card_status_display()}."
            
            # Log the action
            SmsLog.objects.create(
                card=card,
                message=message_content,
                success=True # Assume success for mock function
            )
            log_messages.append(f"SMS sent to {card.owner} ({card.phone_number}) for card {card.card_number}.")
            sent_count += 1
        else:
            log_messages.append(f"Skipped SMS for {card.owner} (Card: {card.card_number}) - No phone number.")

    if sent_count > 0:
        modeladmin.message_user(request, f"Successfully simulated sending SMS to {sent_count} card(s).", messages.SUCCESS)
    else:
        modeladmin.message_user(request, "No SMS were sent (either no cards selected or no phone numbers found).", messages.WARNING)

    # Display detailed log messages
    for msg in log_messages:
        modeladmin.message_user(request, msg, messages.INFO)


# --- Register Models in Admin ---
@admin.register(Cards)
class CardsAdmin(ImportExportModelAdmin):
    resource_class = CardResource
    list_display = ('card_number', 'owner', 'expire', 'phone_number', 'card_status', 'balance',)
    list_filter = ('card_status', 'owner',) # Filtering by status and owner
    search_fields = ('card_number', 'owner', 'phone_number',) # Searching by card number, owner, phone
    actions = [send_sms_action] # Register the custom action

@admin.register(SmsLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ('card', 'message', 'sent_at', 'success',)
    list_filter = ('sent_at', 'success', 'card__card_status',) # Filter by log date, success, and related card status
    search_fields = ('card__card_number', 'card__owner', 'message',) # Search by related card info and message
    readonly_fields = ('card', 'message', 'sent_at', 'success',) # Logs should not be editable
    
