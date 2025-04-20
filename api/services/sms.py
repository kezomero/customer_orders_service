import africastalking
import os
import logging

logger = logging.getLogger(__name__)

class SMSService:
    @classmethod
    def send_order_notification(cls, customer_phone, message):
        try:
            username = os.getenv('AFRICASTALKING_USERNAME')
            api_key = os.getenv('AFRICASTALKING_API_KEY')

            africastalking.initialize(username, api_key)
            sms = africastalking.SMS

            formatted_phone = cls._format_phone_number(customer_phone)
            logger.debug(f"Formatted phone: {formatted_phone}")

            if not formatted_phone:
                logger.warning("Invalid phone number format.")
                return False

            response = sms.send(message, [formatted_phone])
            logger.debug(f"AT Response: {response}")

            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            return recipients and recipients[0].get('status') == 'Success'

        except Exception as e:
            logger.error(f"SMS Error: {e}", exc_info=True)
            return False

    @staticmethod
    def _format_phone_number(phone):
        cleaned = ''.join(filter(str.isdigit, phone))
        if cleaned.startswith('0') and len(cleaned) == 10:
            return f'+254{cleaned[1:]}'
        elif cleaned.startswith('254') and len(cleaned) == 12:
            return f'+{cleaned}'
        elif cleaned.startswith('254') and len(cleaned) == 13:
            return f'+{cleaned}'
        elif cleaned.startswith('7') and len(cleaned) == 9:
            return f'+254{cleaned}'
        elif cleaned.startswith('+254'):
            return cleaned
        return None
