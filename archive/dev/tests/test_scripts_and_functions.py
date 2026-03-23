import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import numpy as np
import pandas as pd

# Add the 'dev' directory to the Python path so we can import scripts_and_functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import scripts_and_functions as sf

class TestScriptsAndFunctions(unittest.TestCase):

    def setUp(self):
        # Mock global hardware objects and os.chdir
        self.patcher_rm = patch('scripts_and_functions.rm', spec=True)
        self.patcher_signal_generator = patch('scripts_and_functions.signal_generator', spec=True)
        self.patcher_osc = patch('scripts_and_functions.osc', spec=True)
        self.patcher_zva = patch('scripts_and_functions.zva', spec=True)
        self.patcher_rf_Generator = patch('scripts_and_functions.rf_Generator', spec=True)
        self.patcher_powermeter = patch('scripts_and_functions.powermeter', spec=True)
        self.patcher_os_chdir = patch('os.chdir')
        self.patcher_time_sleep = patch('time.sleep', return_value=None)
        self.patcher_np_savetxt = patch('numpy.savetxt')
        self.patcher_pd_to_csv = patch('pandas.DataFrame.to_csv')

        self.mock_rm = self.patcher_rm.start()
        self.mock_signal_generator = self.patcher_signal_generator.start()
        self.mock_osc = self.patcher_osc.start()
        self.mock_zva = self.patcher_zva.start()
        self.mock_rf_Generator = self.patcher_rf_Generator.start()
        self.mock_powermeter = self.patcher_powermeter.start()
        self.mock_os_chdir = self.patcher_os_chdir.start()
        self.mock_time_sleep = self.patcher_time_sleep.start()
        self.mock_np_savetxt = self.patcher_np_savetxt.start()
        self.mock_pd_to_csv = self.patcher_pd_to_csv.start()

        # Mock dir_and_var_declaration.zva_parameters as it's imported and used globally
        self.patcher_zva_params = patch('scripts_and_functions.dir_and_var_declaration.zva_parameters', {
            "zva_traces": "/mock/zva/traces",
            "instrument_file": "/mock/instrument.sta",
            "setup_s3p": "/mock/s3p_setup.sta",
            "setup_s2p": "/mock/s2p_setup.sta",
            "setup_s1p": "/mock/s1p_setup.sta",
        })
        self.mock_zva_params = self.patcher_zva_params.start()
        
        # Mock other dir_and_var_declaration attributes
        self.patcher_other_dir_vars = patch('scripts_and_functions.dir_and_var_declaration', spec=True)
        self.mock_other_dir_vars = self.patcher_other_dir_vars.start()
        self.mock_other_dir_vars.ZVA_File_Dir_ZVA67 = "/mock/zva_file_dir"
        self.mock_other_dir_vars.PC_File_Dir = "/mock/pc_file_dir"
        self.mock_other_dir_vars.power_bias_test_setup_powermeter = "MOCK_POWER_BIAS_SETUP"
        self.mock_other_dir_vars.snp_meas_setup_sig_gen = "MOCK_SNP_MEAS_SIG_GEN_SETUP"
        self.mock_other_dir_vars.pullin_setup_sig_gen = "MOCK_PULLIN_SETUP_SIG_GEN"
        self.mock_other_dir_vars.power_test_setup_sig_gen = "MOCK_POWER_TEST_SETUP_SIG_GEN"
        self.mock_other_dir_vars.power_test_setup_rf_gen = "MOCK_POWER_TEST_SETUP_RF_GEN"
        self.mock_other_dir_vars.cycling_setup_oscilloscope = "MOCK_CYCLING_SETUP_OSC"
        self.mock_other_dir_vars.pullin_setup_oscilloscope = "MOCK_PULLIN_SETUP_OSC"
        self.mock_other_dir_vars.pullin_setup_rf_gen = "MOCK_PULLIN_SETUP_RF_GEN"
        self.mock_other_dir_vars.cycling_setup_rf_gen = "MOCK_CYCLING_SETUP_RF_GEN"
        self.mock_other_dir_vars.cycling_setup_sig_gen = "MOCK_CYCLING_SETUP_SIG_GEN"


    def tearDown(self):
        patch.stopall()

    # --- Test Utility Functions ---

    def test_extension_detector(self):
        self.assertEqual(sf.extension_detector("file.txt"), ("file", ".txt"))
        self.assertEqual(sf.extension_detector("archive.tar.gz"), ("archive.tar", ".gz"))
        self.assertEqual(sf.extension_detector("no_extension"), ("no_extension", ""))
        self.assertEqual(sf.extension_detector(".bashrc"), (".bashrc", ""))

    @patch('os.listdir', return_value=['file1.txt', 'file2.s3p', 'image.jpg', 'data.s2p', 'report.txt', 'test.s1p'])
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}")
    def test_filetypes_dir(self, mock_join, mock_isfile, mock_listdir):
        s3p_files, s2p_files, txt_files, s1p_files = sf.filetypes_dir("/mock/path")
        self.assertEqual(s3p_files, ('file2.s3p',))
        self.assertEqual(s2p_files, ('data.s2p',))
        self.assertEqual(txt_files, ('file1.txt', 'report.txt'))
        self.assertEqual(s1p_files, ('test.s1p',))

        # Test with empty path
        result = sf.filetypes_dir("")
        self.assertEqual(result, ('empty', 'empty'))

    def test_format_duration(self):
        self.assertEqual(sf.format_duration(0), "00d 00h 00m 00.00s")
        self.assertEqual(sf.format_duration(1), "00d 00h 00m 01.00s")
        self.assertEqual(sf.format_duration(59), "00d 00h 00m 59.00s")
        self.assertEqual(sf.format_duration(60), "00d 00h 01m 00.00s")
        self.assertEqual(sf.format_duration(3600), "00d 01h 00m 00.00s")
        self.assertEqual(sf.format_duration(86400), "01d 00h 00m 00.00s")
        self.assertEqual(sf.format_duration(90061.5), "01d 01h 01m 01.50s")

    @patch('os.system')
    def test_clear_screen(self, mock_os_system):
        sf.clear_screen(delay=0) # Set delay to 0 to avoid actual sleep in test
        mock_os_system.assert_called_once_with('cls' if os.name == 'nt' else 'clear')
        self.mock_time_sleep.assert_called_once_with(0)

    # --- Test Instrument Initialization/Closing ---

    @patch('scripts_and_functions.pyvisa.ResourceManager')
    @patch('scripts_and_functions.sig_gen_init')
    @patch('scripts_and_functions.osc_init')
    @patch('scripts_and_functions.zva_init')
    @patch('scripts_and_functions.powermeter_init')
    @patch('scripts_and_functions.rf_gen_init')
    def test_initialize_hardware_success(self, mock_rf_gen_init, mock_powermeter_init, mock_zva_init,
                                         mock_osc_init, mock_sig_gen_init, mock_resource_manager):
        # Setup mocks for successful initialization
        mock_resource_manager.return_value = MagicMock()
        mock_sig_gen_init.return_value = MagicMock()
        mock_osc_init.return_value = MagicMock()
        mock_zva_init.return_value = MagicMock()
        mock_powermeter_init.return_value = MagicMock()
        mock_rf_gen_init.return_value = MagicMock()

        sf.initialize_hardware("zva_ip", "sig_gen_ip", "osc_ip", "powermeter_ip", "rf_gen_ip")

        # Assert that all initializers were called with the correct IPs
        mock_resource_manager.assert_called_once()
        mock_sig_gen_init.assert_called_once_with("sig_gen_ip")
        mock_osc_init.assert_called_once_with("osc_ip")
        mock_zva_init.assert_called_once_with(tcpip_address="zva_ip", zva="ZNA67")
        mock_powermeter_init.assert_called_once_with("powermeter_ip")
        mock_rf_gen_init.assert_called_once_with(tcpip_address="rf_gen_ip", rf_gen_type='smb')

        # Assert global variables are set
        self.assertIsNotNone(sf.rm)
        self.assertIsNotNone(sf.signal_generator)
        self.assertIsNotNone(sf.osc)
        self.assertIsNotNone(sf.zva)
        self.assertIsNotNone(sf.powermeter)
        self.assertIsNotNone(sf.rf_Generator)

    @patch('scripts_and_functions.pyvisa.ResourceManager', side_effect=OSError("Test OS Error"))
    @patch('builtins.print') # Mock print to check output
    def test_initialize_hardware_failure(self, mock_print, mock_resource_manager):
        sf.initialize_hardware("zva_ip", "sig_gen_ip", "osc_ip", "powermeter_ip", "rf_gen_ip")

        # Assert that it prints the error and goes offline
        mock_print.assert_any_call("Hardware initialization failed: Test OS Error")
        mock_print.assert_any_call("Running in offline mode. Some functionality will be disabled.")
        self.assertIsNone(sf.rm)
        self.assertIsNone(sf.signal_generator)
        self.assertIsNone(sf.osc)
        self.assertIsNone(sf.zva)
        self.assertIsNone(sf.powermeter)
        self.assertIsNone(sf.rf_Generator)

    def test_close_resource(self):
        # Test closing RsInstrument
        mock_rs_instrument = MagicMock(spec=sf.RsInstrument)
        sf.close_resource(mock_rs_instrument)
        mock_rs_instrument.close.assert_called_once()

        # Test closing pyvisa.Resource
        mock_pyvisa_resource = MagicMock(spec=sf.pyvisa.resources.tcpip.TCPIPInstrument) # More specific spec
        sf.close_resource(mock_pyvisa_resource)
        mock_pyvisa_resource.close.assert_called_once()

    def test_close_all_resources(self):
        # Mock global instruments to be not None
        sf.signal_generator = MagicMock()
        sf.zva = MagicMock()
        sf.osc = MagicMock()
        sf.rf_Generator = MagicMock()
        sf.powermeter = MagicMock()

        sf.close_all_resources()

        sf.signal_generator.close.assert_called_once()
        sf.zva.close.assert_called_once()
        sf.osc.close.assert_called_once()
        sf.rf_Generator.close.assert_called_once()
        sf.powermeter.close.assert_called_once()

        # Test with some resources being None
        sf.signal_generator = None
        sf.zva = MagicMock() # ZVA still exists
        sf.close_all_resources()
        sf.zva.close.assert_called_once() # Should still be called once from previous + once from this
        
    # --- Test Simple Instrument Interactions (example: set_f_start) ---

    def test_set_f_start(self):
        sf.zva = MagicMock() # Ensure zva is mocked
        sf.set_f_start(5.5)
        sf.zva.write_str_with_opc.assert_called_once_with("FREQ:STAR 5500000000.0")
        
    def test_set_fstop(self):
        sf.zva = MagicMock() # Ensure zva is mocked
        sf.set_fstop(15.0)
        sf.zva.write_str_with_opc.assert_called_once_with("FREQ:STOP 15000000000.0")
        
    def test_number_of_points(self):
        sf.zva = MagicMock() # Ensure zva is mocked
        sf.number_of_points(1001)
        sf.zva.write_str_with_opc.assert_called_once_with("SWEep:POINts 1001")
        
    def test_send_trig(self):
        sf.signal_generator = MagicMock() # Ensure signal_generator is mocked
        sf.send_trig()
        sf.signal_generator.write.assert_called_once_with('TRIG')
        sf.signal_generator.query.assert_called_once_with('*OPC?')
        
    def test_query_signal_generator(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.return_value = '1\n'
        self.assertEqual(sf.query_signal_generator(), '1')
        sf.signal_generator.query.assert_called_once_with('OUTput1?')
        
    def test_toggle_signal_generator_off_to_on(self):
        sf.signal_generator = MagicMock()
        # Simulate initial state is OFF
        sf.signal_generator.query.return_value = '0\n' 
        
        sf.toggle_signal_generator()
        
        sf.signal_generator.write.assert_called_once_with('OUTput1 1')
        sf.signal_generator.query.assert_called_once_with('OUTput1?')

    def test_toggle_signal_generator_on_to_off(self):
        sf.signal_generator = MagicMock()
        # Simulate initial state is ON
        sf.signal_generator.query.return_value = '1\n' 
        
        sf.toggle_signal_generator()
        
        sf.signal_generator.write.assert_called_once_with('OUTput1 0')
        sf.signal_generator.query.assert_called_once_with('OUTput1?')
        
    def test_dc_voltage(self):
        sf.signal_generator = MagicMock()
        sf.dc_voltage(1.5)
        sf.signal_generator.write.assert_called_once_with('SOURce:VOLTage:OFFSET 1.5')
        
    def test_set_osc_event_count(self):
        sf.osc = MagicMock()
        sf.set_osc_event_count(20)
        sf.osc.write.assert_called_once_with("TRIGger:B:EVENTS:COUNt 20")
        
    def test_rf_gen_set_freq(self):
        sf.rf_Generator = MagicMock()
        sf.rf_gen_set_freq(18.0)
        sf.rf_Generator.write_str_with_opc.assert_called_once_with('SOUR:FREQ 18.0 GHz')

    # --- Tests for more complex instrument interactions ---

    def test_bias_voltage(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '1\n', '0.5\n', '0.5\n']

        result = sf.bias_voltage('10')

        self.assertAlmostEqual(result, 10.0)
        
        expected_write_calls = [
            unittest.mock.call("SOURce:VOLTage:OFFSET 0"),
            unittest.mock.call("SOURce:VOLTage:LOW 0"),
            unittest.mock.call("SOURce:VOLTage:HIGH 0.5"),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls, any_order=True)

        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce:VOLTage?"),
        ], any_order=True)

    def test_bias_pull_in_voltage(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '1\n', '0.75\n', '0.75\n']
        
        result = sf.bias_pull_in_voltage('15')
        
        self.assertAlmostEqual(result, 15.0)

        expected_write_calls = [
            unittest.mock.call("SOURce:VOLTage:OFFSET 0"),
            unittest.mock.call("SOURce:VOLTage:LOW -0.75"),
            unittest.mock.call("SOURce:VOLTage:HIGH 0.75"),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls, any_order=True)
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce:VOLTage?"),
        ], any_order=True)

    def test_ramp_width(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '1\n', '0, "No error"']

        sf.ramp_width(100.0)

        expected_freq = 1 / (4 * 100.0 * 10**(-6))
        
        expected_write_calls = [
            unittest.mock.call('SOURce1:FUNCtion:RAMP:SYMMetry 50'),
            unittest.mock.call(f'FREQuency {expected_freq}'),
            unittest.mock.call('OUTPut 1'),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls)
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call('SYSTem:ERRor?'),
        ], any_order=True)

    def test_set_pulse_width(self):
        sf.signal_generator = MagicMock()
        sf.zva = MagicMock()
        sf.zva.query_str_with_opc.return_value = '0.002'
        sf.signal_generator.query.side_effect = ['0.004\n', '0, "No error"\n'] 

        with patch('builtins.print') as mock_print:
             sf.set_pulse_width(0.001)

        sf.signal_generator.write.assert_called_once_with('SOURce1:FUNCtion:PULSe:WIDTh 0.001')
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("SOURce1:FUNCtion:PULSe:PERiod?"),
        ], any_order=True)
        mock_print.assert_any_call("Pulse width is too small for a complete sweep measurement", end='\n')

    def test_set_prf_success(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '1\n', '0.0005\n', '0\n', '1\n']
        
        result = sf.set_prf(1000)
        
        sf.signal_generator.write.assert_called_once_with('SOURce1:FUNCtion:PULSe:PERiod 0.001')
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce1:FUNCtion:PULSe:WIDTh?"),
        ], any_order=True)
        self.assertEqual(result, "Pulse width set to 0.0005")

    def test_set_prf_fail(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '1\n', '0.002\n']
        
        result = sf.set_prf(1000)
        
        sf.signal_generator.write.assert_not_called()
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce1:FUNCtion:PULSe:WIDTh?"),
        ], any_order=True)
        self.assertEqual(result, "Pulse width is too large, settings conflict\nMax Pulse width must be < 0.001")


    # --- Tests for more complex instrument interactions ---

    def test_bias_voltage(self):
        sf.signal_generator = MagicMock()
        # Side effect for multiple query calls from bias_voltage (decorator + actual queries)
        sf.signal_generator.query.side_effect = ['0\n', '0.5\n', '0.5\n'] 

        result = sf.bias_voltage('10')

        self.assertAlmostEqual(result, 10.0)
        
        # Calls from bias_voltage itself
        expected_write_calls = [
            unittest.mock.call("SOURce:VOLTage:OFFSET 0"),
            unittest.mock.call("SOURce:VOLTage:LOW 0"),
            unittest.mock.call("SOURce:VOLTage:HIGH 0.5"),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls, any_order=True)

        # Queries from decorator (*OPC?) and function (SOURce:VOLTage?)
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce:VOLTage?"),
            unittest.mock.call("SOURce:VOLTage?"),
        ])

    def test_bias_pull_in_voltage(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '0.75\n', '0.75\n'] # For decorator and function queries
        
        result = sf.bias_pull_in_voltage('15')
        
        self.assertAlmostEqual(result, 15.0)

        expected_write_calls = [
            unittest.mock.call("SOURce:VOLTage:OFFSET 0"),
            unittest.mock.call("SOURce:VOLTage:LOW -0.75"),
            unittest.mock.call("SOURce:VOLTage:HIGH 0.75"),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls, any_order=True)
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce:VOLTage?"),
            unittest.mock.call("SOURce:VOLTage?"),
        ])


    def test_ramp_width(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '0, "No error"'] # For decorator and function query

        sf.ramp_width(100.0) # 100 µs

        expected_freq = 1 / (4 * 100.0 * 10**(-6)) # 2500 Hz
        
        expected_write_calls = [
            unittest.mock.call('SOURce1:FUNCtion:RAMP:SYMMetry 50'),
            unittest.mock.call(f'FREQuency {expected_freq}'),
            unittest.mock.call('OUTPut 1'),
        ]
        sf.signal_generator.write.assert_has_calls(expected_write_calls)
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call('SYSTem:ERRor?'),
        ])


    @patch('scripts_and_functions.sig_gen_opc_control', lambda x: x) # Temporarily disable decorator to debug ZeroDivisionError
    def test_set_pulse_width(self):
        sf.signal_generator = MagicMock()
        sf.zva = MagicMock()
        sf.zva.query_str_with_opc.return_value = '0.002' # 2ms sweep time
        sf.signal_generator.query.return_value = '0.004\n' # 4ms period (PRI)


        with patch('builtins.print') as mock_print:
             sf.set_pulse_width(0.003) # 3ms pulse width

        sf.signal_generator.write.assert_called_once_with('SOURce1:FUNCtion:PULSe:WIDTh 0.003')
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce1:FUNCtion:PULSe:PERiod?"),
        ])
        # Check if the warning was printed
        mock_print.assert_any_call("Pulse width is too small for a complete sweep measurement", end='\n')
        mock_print.assert_any_call("Minimum pulse length is: 0.002\nRequired prf=500.0 Hz", end='\n')
    
    def test_set_prf_success(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '0.0005\n', '0\n'] # For decorator and function query
        
        result = sf.set_prf(1000) # 1kHz PRF -> 1ms PRI
        
        sf.signal_generator.write.assert_called_once_with('SOURce1:FUNCtion:PULSe:PERiod 0.001')
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce1:FUNCtion:PULSe:WIDTh?"),
            unittest.mock.call("*OPC?"),
        ])
        self.assertEqual(result, "Pulse width set to 0.0005")

    def test_set_prf_fail(self):
        sf.signal_generator = MagicMock()
        sf.signal_generator.query.side_effect = ['0\n', '0.002\n', '0\n'] # For decorator and function query
        
        result = sf.set_prf(1000) # 1kHz PRF -> 1ms PRI
        
        sf.signal_generator.write.assert_not_called()
        sf.signal_generator.query.assert_has_calls([
            unittest.mock.call("*OPC?"),
            unittest.mock.call("SOURce1:FUNCtion:PULSe:WIDTh?"),
            unittest.mock.call("*OPC?"),
        ])
        self.assertEqual(result, "Pulse width is too large, settings conflict\nMax Pulse width must be < 0.001")

if __name__ == '__main__':
    unittest.main()
