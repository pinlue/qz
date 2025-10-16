class ModelIOBridge:
    def __init__(self, strategy, file_format):
        self.strategy = strategy
        self.file_format = file_format

    def import_file(self, file):
        data = self.file_format.read(file)
        self.strategy.import_data(data)

    def export_file(self):
        data = self.strategy.export_data()
        return self.file_format.write(data)