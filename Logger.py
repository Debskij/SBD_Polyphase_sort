class Logger:
    def __init__(self):
        self.log = []
        self.dbg_variables = {'database_log': True,
                              'distribution_log': True,
                              'merge_log': True}

    def __call__(self, *args, **kwargs):
        try:
            if self.dbg_variables[args[0]]:
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
