import os
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending templated emails, with support for multiple backends,
    error handling, logging, and queueing stub.
    """

    def __init__(self, backend: str = None):
        self.backend = backend or getattr(
            settings, "EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend"
        )
        self.connection = get_connection(self.backend)
        self.default_from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER
        )

    def send_email(
        self,
        subject,
        recipient,
        template_name,
        context=None,
        html_template_name=None,
        attachments=None,
    ):
        """
        Send an email using a template. Supports both plain text and HTML.
        """
        context = context or {}
        try:
            text_body = render_to_string(template_name, context)
            html_body = None
            if html_template_name:
                html_body = render_to_string(html_template_name, context)
            else:
                # Try to find an HTML version by convention
                base, ext = os.path.splitext(template_name)
                html_candidate = f"{base}.html"
                if os.path.exists(
                    os.path.join(settings.BASE_DIR, "templates", html_candidate)
                ):
                    html_body = render_to_string(html_candidate, context)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=self.default_from_email,
                to=[recipient],
                connection=self.connection,
            )
            if html_body:
                msg.attach_alternative(html_body, "text/html")
            if attachments:
                for attachment in attachments:
                    msg.attach(*attachment)  # (filename, content, mimetype)
            msg.send()
            logger.info(f"Sent email to {recipient} with subject '{subject}'")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}", exc_info=True)
            return False

    def send_verification_email(self, recipient, token, context=None):
        """
        Send an email verification message.
        """
        context = context or {}
        context.update({"token": token, "recipient": recipient})
        subject = "Email Verification"
        return self.send_email(
            subject=subject,
            recipient=recipient,
            template_name="emails/verification.txt",
            html_template_name="emails/verification.html",
            context=context,
        )

    def send_password_reset_email(self, recipient, token, context=None):
        """
        Send a password reset email.
        """
        context = context or {}
        context.update({"token": token, "recipient": recipient})
        subject = "Password Reset Request"
        return self.send_email(
            subject=subject,
            recipient=recipient,
            template_name="emails/password_reset.txt",
            html_template_name="emails/password_reset.html",
            context=context,
        )

    def send_bulk_emails(self, email_data_list):
        """
        Send multiple emails efficiently (stub for queueing).
        Each item in email_data_list should be a dict with keys:
        subject, recipient, template_name, context, html_template_name, attachments
        """
        # In production, this should enqueue jobs to a task queue like Celery.
        results = []
        for data in email_data_list:
            result = self.send_email(
                subject=data.get("subject"),
                recipient=data.get("recipient"),
                template_name=data.get("template_name"),
                context=data.get("context"),
                html_template_name=data.get("html_template_name"),
                attachments=data.get("attachments"),
            )
            results.append(result)
        return results

    def queue_email(self, *args, **kwargs):
        """
        Stub for queueing an email to be sent asynchronously.
        In production, this would enqueue a Celery or RQ task.
        """
        logger.info("Queueing email (stub): args=%s kwargs=%s", args, kwargs)
        # Example: from myproject.tasks import send_email_task; send_email_task.delay(...)
        pass
