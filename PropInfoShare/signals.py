from django.dispatch import Signal

new_notification = Signal(providing_args=["context", "sender_model_name", "sent_user_id"])
admin_notification = Signal(providing_args=["context", "notification_by", "notification_type", 'sender_model_name'])