from base.choices import ChoiceEnum


class NotificationType(ChoiceEnum):
    """this are the roles that we have in the vendor api/website, using this we can track the roles
    in our system for example if the user is MQG admin then he is NW admin in the vendor's site
    """

    login = ("LOGIN", "logged_in")
    contract_created = ("CONTRACT_CREATED", "contract_created")
    credit_consumed = ("CREDIT_CONSUMED", "credit_consumed")
