DEBUG_VARIABLES = {'database_log': False,
                   'distribution_log': False,
                   'merge_log': False,
                   'phase_log': True}


class Logger:
    def __init__(self, dbg_variables: dict):
        self.log = []
        self.dbg_variables = dbg_variables

    def __call__(self, *args, **kwargs):
        try:
            if self.dbg_variables.get(args[0]):
                self.log.append(args[1])
        except:
            pass

    def save_log_to_file(self, path):
        try:
            with open(path, 'r+') as file:
                for line in self.log:
                    file.write(line)
        except:
            pass

    def print_log(self):
        for line in self.log:
            print(line)
