class Record:
    def __init__(self):
        self.id = 0
        self.zone_id = 0
        self.active = False
        self.cls = ''
        self.type = ''
        self.ttl = 0
        self.data = {}
        self.is_conditional = False
        self.conditional_count = 0
        self.conditional_limit = 0
        self.confitional_reset = False
        self.conditional_data = {}
