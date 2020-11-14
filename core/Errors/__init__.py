class CommandError(Exception):
    def __init__(self, message=None, *args, **kwargs):
        self.message = 'Unknown Command '+str(message)
        if not message:
            self.message='Unknown Command.'
        super().__init__(*args, **kwargs)
    
    def __str__(self):
        import json
        return repr('[!!] '+repr(self.message))

class HackError(Exception):
    def __init__(self, txt='', *args, **kwargs):
        print('\033[91m[ERR]\033[0m Unable to hack.'+txt)