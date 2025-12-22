class DataSource:
    def read_signal(self):
        raise NotImplementedError("This method should be overridden by subclasses")

class DataSourceA(DataSource):
    def read_signal(self):
        # Simulate reading a signal from data source A
        return "Signal from DataSource A"

class DataSourceB(DataSource):
    def read_signal(self):
        # Simulate reading a signal from data source B
        return "Signal from DataSource B"

# Add more data sources as needed