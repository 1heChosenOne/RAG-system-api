class EmailNotFound(Exception):
    def __init__(self,email:str):
        self.email=email
        super().__init__(f"no email as {email} in database")
        
class PassEmailIncorrect(Exception):
    def __init__(self):
        super().__init__("password or email is incorrect")