class WebPushManager:
    def __init__(self, vapid_private, admin_email, icon):
        self.__vapid_private = vapid_private
        self.__admin_email = admin_email
        self.__icon = icon
