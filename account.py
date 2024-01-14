from templates import Panel, Form, FormField


class _RegistrationForm(Form):

    def __init__(self):
        super().__init__()
        self.username = self.add_input_text('Username:', maxchar=10, input_underline='_')
        self.email = self.add_input_text('Email:', maxchar=50, input_underline='_')
        self.password = self.add_input_text('Password:', maxchar=50, password=True, input_underline='_')
        self.confirm_password = self.add_input_text('Confirm Password:', maxchar=50, password=True, input_underline='_')

    def validate(self):
        pass

    def register(self):
        pass


class _AuthenticationForm(Form):

    def __init__(self):
        super().__init__()
        self.username = self.add_input_text('Username:', maxchar=10, input_underline='_')
        self.password = self.add_input_text('Password:', maxchar=50, password=True, input_underline='_')

    def validate(self):
        pass

    def authenticate(self):
        pass
