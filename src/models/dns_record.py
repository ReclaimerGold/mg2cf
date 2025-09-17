class DNSRecord:
    def __init__(self, name, record_type, content):
        self.name = name
        self.type = record_type
        self.content = content

    def validate(self):
        if not self.name or not self.type or not self.content:
            raise ValueError("All fields (name, type, content) must be provided.")
        # Additional validation logic can be added here

    def __repr__(self):
        return f"DNSRecord(name={self.name}, type={self.type}, content={self.content})"