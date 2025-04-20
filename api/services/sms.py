import africastalking
import os
import logging

logger = logging.getLogger(__name__)

class SMSService:
    @classmethod
    def send_order_notification(cls, customer_phone, message):
        try:
            # Get credentials
            username = os.getenv('AFRICASTALKING_USERNAME')
            api_key = os.getenv('AFRICASTALKING_API_KEY')

            # Log to verify credentials are picked
            logger.debug(f"AT username: {username}, API key set: {bool(api_key)}")

            # Initialize Africa's Talking
            africastalking.initialize(username, api_key)

            # Format phone number
            formatted_phone = cls._format_phone_number(customer_phone)
            logger.debug(f"Formatted phone number: {formatted_phone}")

            if not formatted_phone:
                logger.warning("Phone number format invalid.")
                return False

            # Send SMS
            sms = africastalking.SMS
            response = sms.send(message, [formatted_phone])

            # Log full API response
            logger.debug(f"Africa's Talking SMS API response: {response}")

            recipients = response.get('SMSMessageData', {}).get('Recipients', [])
            if recipients and recipients[0].get('status') == 'Success':
                return True
            else:
                logger.warning(f"SMS sending failed: {recipients}")
                return False

        except Exception as e:
            logger.error(f"Exception when sending SMS: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def _format_phone_number(phone):
        cleaned = ''.join(c for c in phone if c.isdigit())
        if cleaned.startswith('0') and len(cleaned) == 10:
            return f'+254{cleaned[1:]}'
        elif cleaned.startswith('254') and len(cleaned) == 12:
            return f'+{cleaned}'
        elif cleaned.startswith('+254') and len(cleaned) == 13:
            return cleaned
        return None
