class Zone:
    def __init__(self):
        self.id = 0
        self.user_id = 0
        self.active = False
        self.catch_all = False
        self.forwarding = False
        self.regex = False
        self.master = False
        self.domain = ''
        self.created_at = ''
        self.updated_at = ''
        self.tags = []
