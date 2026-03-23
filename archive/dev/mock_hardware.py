# dev/mock_hardware.py

class MockInstrument:
    """A mock instrument class that simulates the behavior of a real instrument in offline mode."""

    def __init__(self, resource_string='MOCK'):
        self._resource_string = resource_string
        print(f"INFO: Using MockInstrument for '{self._resource_string}'")

    def write(self, command):
        print(f"MOCK WRITE to {self._resource_string}: {command}")

    def query(self, command):
        print(f"MOCK QUERY to {self._resource_string}: {command}")
        if '?' in command:
            if 'SYSTem:ERRor?' in command:
                return '+0,"No error"'
            if '*IDN?' in command:
                return f"Mock Instrument ({self._resource_string}),12345,1.0"
            if 'OUTput' in command:
                return '0'
            if 'ACQuire:NUMACq?' in command:
                return '1'
            # Add more specific query responses here
            if 'PULSe:WIDTh?' in command:
                return '0.001' # 1ms default pulse width
            if 'PULSe:PERiod?' in command:
                return '0.01' # 10ms default period (100Hz)
            if 'VOLTage?' in command:
                return '1.0'
            if 'SWEep:TIME?' in command:
                return '1.0'
        return "0" # Return "0" for unknown queries instead of ""

    def write_str_with_opc(self, command, timeout=None):
        print(f"MOCK WRITE (with OPC) to {self._resource_string}: {command}")
        return None

    def query_str(self, command):
        print(f"MOCK QUERY_STR to {self._resource_string}: {command}")
        if '?' in command:
            if 'SYSTem:ERRor?' in command:
                return '+0,"No error"'
            if '*IDN?' in command:
                return f"Mock Instrument ({self._resource_string}),12345,1.0"
        return ""
        
    def query_str_with_opc(self, command):
        return self.query_str(command)

    def query_binary_values(self, message, header_fmt="ieee", is_big_endian=True, chunk_size=2000):
        print(f"MOCK QUERY_BINARY_VALUES from {self._resource_string}: {message}")
        return [0.0]

    def close(self):
        print(f"MOCK CLOSE for {self._resource_string}")

    @property
    def idn_string(self):
        return f"Mock Instrument ({self._resource_string}),12345,1.0"
