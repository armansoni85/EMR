from django.utils.translation import gettext as _

ERROR_IN_THE_REQUEST = _("Error in the request.")
APPLICATION_ERROR_MESSAGE = _("Application Error.")
DO_NOT_HAVE_PERMISSION_MESSAGE = _("Permission Denied")
RESOURCE_NOT_FOUND_MESSAGE = _("Resource not found")
INVALID_REQUEST = _("Invalid Request")
VALIDATION_ERROR_MESSAGE = _("Validation Error")
API_ERROR_MESSAGE = _("API Error.")
RECORD_NOT_FOUND_MESSAGE = _("Record Not Found")
INVALID_LINK = _("Invalid link.")
ONLY_SUPPORTED_FOR_MOBILE = _(
    "This API is exclusively designed for mobile users. Please access it using a mobile device to utilize its features."
)
PASSWORD_RESET_TOKEN_ALREADY_USED = _("Password Reset Token is already used.")
FILE_UPLOAD_LIMIT = _("File should be less than 5MB.")
EXPIRED_LINK = _("Link has expired.")
UPDATE_SUCCESS = _("Updated successfully.")
DELETE_SUCCESS = _("Deleted successfully.")
CREATE_SUCCESS = _("Created successfully.")
CANNOT_LOGIN = _("Cannot log in with the provided credentials.")
LOGIN_SUCCESS = _("Logged in successfully.")
INVALID_LINK = _("Invalid token or link.")
MEDICAL_FILE_UPLOAD_LIMIT = _("File should be less than 5MB.")
ALLOWED_EXTENSIONS = ".pdf,.doc,.docx,.txt,.rtf,.jpeg,.png"
LIMITED_ALLOWED_EXTENSIONS = ".pdf,.doc,.docx,.jpeg,.png"
ALLOWED_AUDIO_EXTENSIONS = ".mp3,.webm"
INVALID_FILE_EXTENSION_MESSAGE = _(
    "Unsupported file extension. Allowed extensions are: %(allowed)s"
)
EXPIRED_LINK = _("Link has expired.")
UPDATE_SUCCESS = _("Updated successfully.")
DELETE_SUCCESS = _("Deleted successfully.")
CREATE_SUCCESS = _("Created successfully.")
CANNOT_LOGIN = _("Cannot log in with the provided credentials.")
LOGIN_SUCCESS = _("Logged in successfully.")
VERIFICATION_MAIL_SENT = _(
    "You will soon receive a verification email if your email is registered with us."
)
EMAIL_VERIFIED = _("Email verified successfully.")
EMAIL_ALREADY_VERIFIED = _("Email already verified.")
USER_NOT_ACTIVE = _("User is not active.")
CODE_SENT = _("Verification code sent to your mobile number.")
ERROR_OCCURRED = _("An error occurred.")
EMAIL_NOT_EXISTS = _("Email does not exist.")
RESET_PASSWORD_LINK_SENT = _(
    "You will receive a password reset link if your email is registered."
)
RESET_PASSWORD_OTP_SENT = _(
    "You will receive a password reset OTP code in your email if the email exists ."
)
SAME_PASSWORD_ERROR = _("New password cannot be the same as the current password.")
PASSWORD_WRONG = _("Incorrect password.")
PASSWORD_UPDATED = _("Password updated successfully.")
MOBILE_CODE_NO_MATCH = _("Mobile number does not match the verification code.")
INVALID_OTP = _("Invalid code entered.")
OLD_PASSWORD_WRONG = _("Please correct the entered current password.")
NOT_AVAILABLE = _("Not available.")
TNC_UPDATED_TITLE = _("Terms and conditions updated.")
TNC_UPDATED_DESCRIPTION = _(
    "Our terms and conditions have been updated. Please click on this notification to view the updated terms."
)
PRIVACY_POLICY_UPDATED_TITLE = _("Privacy policy updated.")
PRIVACY_POLICY_UPDATED_DESCRIPTION = _(
    "Our privacy policies have been updated. Please click on this notification to view the updated policies."
)
PAYMENT_TERM_UPDATED_TITLE = _("Payment terms updated.")
PAYMENT_TERM_UPDATED_DESCRIPTION = _(
    "Our payment terms have been updated. Please click on this notification to view the updated terms."
)
DEVICE_TOKEN_SAVED = _("Device token saved.")
DEVICE_TOKEN_REMOVED = _("Device token removed.")
NOTIFICATION_MARKED_READ = _("All notifications marked as read.")
ADD_MOBILE_NUMBER = _("Please add a mobile number to verify.")
MOBILE_ALREADY_VERIFIED = _("Mobile number is already verified.")
MOBILE_VERIFIED = _("Mobile number verified successfully.")
OTP_SENDING_TEXT = _(
    "Hello from MAS_QUE_GAS, your verification code is {}. It is valid for 10 minutes."
)
INVALID_CODE = _("Invalid code entered.")
INVALID_TOKEN = _("Invalid token received.")
EXPIRED_TOKEN = _("Token has expired.")
MOBILE_EXISTS = _("A user with this mobile number already exists.")
EMAIL_EXISTS = _("A user with this email ID already exists.")
DEFAULT_CLAUSES_TEXT = _(
    "Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum."
)
LOGGED_OUT_DESC = "Once logged out, you will not be able to access any restricted functionality. To access again, you have to log in."
INVALID_CONTENT_TYPE = _("Invalid Content Type")
RATING_VALIDATION_ERROR = _("Rating cannot be greater than 5.")
SERVER_ERROR_MESSAGE = _("Server Error")
CORRECT_BELOW_ERRORS = _("Please correct the errors below.")
MATCHING_ERROR_NOT_FOUND_MESSAGE = _("Not found")
PARSE_ERROR_MESSAGE = _("Parse error.")
# Appointment
PATIENT_DOCTOR_HOSPITAL_DIFFERENT = _(
    "Doctor ,Patient or Appointment creator must be of same hospital."
)
APPOINTMENT_PAST_DATE = _("Appointment datetime cannot be in past.")
APPOINTMENT_ALREADY_BOOKED = _("Appointment date is already booked.")
DOCTOR_AND_PATIENTS_REQUIRED = _("Both doctor or patient required.")
# Consultation
OWN_APPOINTMENT_CONSULTATION_ONLY_ALLOWED = _(
    "Only own appointment consultation is allowed."
)
FOLLOW_UP_DATE_PAST = _("Follow up date cannot be in past.")
MEDICAL_DOCUMENT_CROSS_HOSPITAL_ERROR = _(
    "Medical documents can only be shared between users of the same hospital."
)
MEDICAL_DOCUMENT_BOTH_PATIENT_ERROR = _(
    "One patient cannot send data to another patient"
)
DOCTOR_AI_CONSULTATION_PROMPT = "Act as expert doctor and provide consultation with following Subjective, Vitals, Assessment, and Plan details based on conversation with patient in english"  # donot add translation here
AI_CHAT_SUPPORT_PROMPT = """
    You are a virtual health assistant for a hospital. Your role is to provide general health-related information, answer common medical questions, and guide patients on when to seek professional medical care. 
    Your responses should be:
    - Respectful, professional, and easy to understand
    - Based on verified medical knowledge
    - Within the limits of general advice — never diagnose conditions, prescribe medications, or recommend specific treatments
    - Always encourage users to consult a doctor or visit the hospital for serious concerns

    Capabilities:
    - Provide information about common symptoms and possible causes (e.g., "What causes a sore throat?")
    - Explain how and when to book an appointment
    - Suggest general wellness tips and preventive care
    - Describe services offered at the hospital (e.g., departments, checkups, emergency services)
    - Advise when it is urgent to visit the hospital or call emergency services

    Limitations:
    - Do NOT diagnose conditions or provide treatment plans
    - Do NOT give personalized medical advice
    - Do NOT comment on lab reports or prescriptions
    - Do NOT engage in non-health-related topics

    Example inquiries you can answer:
    - "What are symptoms of dengue?"
    - "Is a fever of 102 dangerous?"
    - "How do I book an appointment with a dermatologist?"
    - "Does your hospital offer blood sugar testing?"
    - "What should I do if I have chest pain?"

    You are friendly, clear, and focused entirely on health support.
"""
