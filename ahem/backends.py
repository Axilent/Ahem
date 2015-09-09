from __future__ import unicode_literals

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.conf import settings as django_settings

from ahem.models import UserBackendRegistry


class BaseBackend(object):
    """
    VARIABLES
    name - A unique string that identifies the backend
    across the project
    required_settings - A list of setings required to register
    a user in the backend

    METHODS
    send_notification - Custom method for each backend that
    sends the desired notification
    """

    required_settings = []

    @classmethod
    def register_user(cls, user, **settings):
        required_settings = []
        if hasattr(cls, 'required_settings'):
            required_settings = cls.required_settings

        if not set(required_settings).issubset(set(settings.keys())):
            raise Exception("Missing backend settings.") # TODO: change to custom exception

        try:
            registry = UserBackendRegistry.objects.get(
                user=user, backend=cls.name)
        except ObjectDoesNotExist:
            registry = UserBackendRegistry(
                user=user, backend=cls.name)

        registry.settings = settings
        registry.save()

        return registry

    def send_notification(self, user, notification, context={}, settings={}):
        raise NotImplementedError


class EmailBackend(BaseBackend):
    """
    CONTEXT PARAMS
    subject - An subject for the email.
    from_email - The email the message will be sent from,
    default is DEFAULT_FROM_EMAIL.
    use_html - If true, the email will be sent with html content type.
    """
    name = 'email'

    def send_notification(self, user, notification, context={}, settings={}):
        body = notification.render_template(user, self.name, context=context)
        subject = context.get('subject', '')
        from_email = context.get('from_email', django_settings.DEFAULT_FROM_EMAIL)
        recipient_list = [user.email]
        use_html = context.get('use_html', False)

        email_params = {}
        if use_html:
            email_params['html_message'] = body

        send_mail(subject, body, from_email, recipient_list, **email_params)


class LoggingBackend(BaseBackend):
    """
    CONTEXT PARAMS
    logger - logger name
    logging_level - the level of the logger
    """
    name = 'logging'

    def get_logger(self, logger_name):
        if logger_name:
            logger = logging.getLogger(logger_name)
        else:
            logger = logging

        return logger

    def send_notification(self, user, notification, context={}, settings={}):
        text = notification.render_template(user, self.name, context=context)

        logging_level = context.get('logging_level', 'info')
        logger = self.get_logger(context.get('logger', None))

        getattr(logger, logging_level)(text)
