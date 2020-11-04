import threading

from django.contrib.auth import get_user_model

User = get_user_model()


class EmailThread(threading.Thread):

    def __init__(self, user, subject, message):
        self.user = user
        self.subject = subject
        self.message = message
        threading.Thread.__init__(self)

    def run(self):

        self.user.email_user(self.subject, self.message)


def confirmation_email(user_id, subject, message):
    user = User.objects.get(pk=user_id)
    return EmailThread(user, subject, message).start()
