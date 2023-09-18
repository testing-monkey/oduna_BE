from user.models import User




def send_email_verification_mail_async(user_id):
    user = User.objects.get(id=user_id)
    user.send_email_verification_mail()



def send_password_reset_mail_async(user_id):
    user = User.objects.get(id=user_id)
    user.send_password_reset_mail()

