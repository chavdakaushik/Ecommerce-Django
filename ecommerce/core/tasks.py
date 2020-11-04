from celery.decorators import task
from celery.utils.log import get_task_logger

from core.email import confirmation_email

logger = get_task_logger(__name__)


@task(name='confirmation_email_task')
def confirmation_email_task(user_id, subject, message):
    logger.info('Confirmation email is send ')
    return confirmation_email(user_id, subject, message)
