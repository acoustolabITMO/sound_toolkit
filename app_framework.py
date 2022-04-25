import sys
import datetime
from PyQt5 import QtWidgets
from pathlib import Path
import matplotlib.pyplot as plt

# Import local modules:
import recorder as gr
import analyzer as an
from gui_main_window import Ui_MainWindow


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)

        # Main menu
        self.actionQuit.triggered.connect(self.close_app)
        self.actionPlot_signal.triggered.connect(self.plot_signal_quick)

        self.home()

    def home(self):
        # Recording tab:
        # Buttons:
        self.btnQuit.clicked.connect(self.close_app)
        self.btnStart.clicked.connect(self.start_gen_rec)

        # Combo boxes:
        self.comboBox_wfparam_type.currentTextChanged. \
            connect(self.switch_wf_inputs)
        self.label_wfparam_freq_sin.hide()
        self.lineEdit_wfparam_freq_sin.hide()

        # Analysis tab:
        # Buttons:
        self.btnBrowse_rec.clicked.connect(self.browse_files_signal)
        self.btnBrowse_ref.clicked.connect(self.browse_files_reference)
        self.btnPlot_rec.clicked.connect(lambda: self.plot_signal('recording'))
        self.btnPlot_ref.clicked.connect(lambda: self.plot_signal('reference'))
        self.btnPlot_tl.clicked.connect(self.plot_tl)

    def plot_signal(self, signal_type):
        if signal_type == 'recording':
            path_signal = self.lineEdit_filename_rec.text()
        elif signal_type == 'reference':
            path_signal = self.lineEdit_filename_ref.text()

        if self.checkBox_tl_filter.isChecked():
            is_filtered = True
            filter_params = {
                'f_low': float(self.lineEdit_tl_filter_f_low.text()),
                'f_high': float(self.lineEdit_tl_filter_f_high.text()),
                'order': self.spinBox_tl_filter_order.value()
            }
        else:
            is_filtered = False
            filter_params = None

        # TODO: check file contents

        if path_signal == '':
            error_msg = "You have not selected file to plot!"
            QtWidgets.QMessageBox.critical(self,
                                           "Error",
                                           error_msg)
        else:
            an.plot_spectrum(path_signal,
                             is_filtered=is_filtered,
                             filter_params=filter_params)

    def plot_signal_quick(self):
        [path_signal, _] = \
            QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file with recording',
                                                  'recording (*.wav, *.txt)')
        # TODO: check file
        if path_signal != '':
            an.plot_spectrum(path_signal,
                             is_filtered=False, filter_params=None)

    def plot_tl(self):
        filename_signal = self.lineEdit_filename_rec.text()
        filename_reference = self.lineEdit_filename_ref.text()

        if self.checkBox_tl_filter.isChecked():
            is_filtered = True
            filter_params = {
                'f_low': float(self.lineEdit_tl_filter_f_low.text()),
                'f_high': float(self.lineEdit_tl_filter_f_high.text()),
                'order': self.spinBox_tl_filter_order.value()
            }
        else:
            is_filtered = False
            filter_params = None

        if filename_signal == '':
            error_msg = "You have not selected file with recording!"
            QtWidgets.QMessageBox.critical(self,
                                           "Error",
                                           error_msg)
        elif filename_reference == '':
            error_msg = "You have not selected file with reference!"
            QtWidgets.QMessageBox.critical(self,
                                           "Error",
                                           error_msg)
        else:
            an.get_tl(filename_signal, filename_reference,
                      is_filtered=is_filtered, filter_params=filter_params)

    def browse_files_signal(self):
        [path_signal, _] = \
            QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  'recording (*.wav)')
        self.lineEdit_filename_rec.setText(path_signal)

    def browse_files_reference(self):
        [path_reference, _] = \
            QtWidgets.QFileDialog.getOpenFileName(self,
                                                  'Open file',
                                                  'reference (*.wav)')
        self.lineEdit_filename_ref.setText(path_reference)

    def switch_wf_inputs(self):
        state = self.comboBox_wfparam_type.currentText()
        # TODO: check more elegant way for that switcher
        if state == 'chirp':
            self.label_wfparam_freq_sin.hide()
            self.lineEdit_wfparam_freq_sin.hide()

            self.label_wfparam_freq_start.show()
            self.lineEdit_wfparam_freq_start.show()
            self.label_wfparam_freq_end.show()
            self.lineEdit_wfparam_freq_end.show()

            self.label_wfparam_freq_step.hide()
            self.lineEdit_wfparam_freq_step.hide()
            self.label_wfparam_sweep_pause.hide()
            self.lineEdit_wfparam_sweep_pause.hide()
        elif state == 'sweep':
            self.label_wfparam_freq_sin.hide()
            self.lineEdit_wfparam_freq_sin.hide()

            self.label_wfparam_freq_start.show()
            self.lineEdit_wfparam_freq_start.show()
            self.label_wfparam_freq_end.show()
            self.lineEdit_wfparam_freq_end.show()
            self.label_wfparam_freq_step.show()
            self.lineEdit_wfparam_freq_step.show()
            self.label_wfparam_sweep_pause.show()
            self.lineEdit_wfparam_sweep_pause.show()
        elif state == 'sin':
            self.label_wfparam_freq_sin.show()
            self.lineEdit_wfparam_freq_sin.show()

            self.label_wfparam_freq_start.hide()
            self.lineEdit_wfparam_freq_start.hide()
            self.label_wfparam_freq_end.hide()
            self.lineEdit_wfparam_freq_end.hide()
            self.label_wfparam_freq_step.hide()
            self.lineEdit_wfparam_freq_step.hide()
            self.label_wfparam_sweep_pause.hide()
            self.lineEdit_wfparam_sweep_pause.hide()

    def close_app(self):
        choice = \
            QtWidgets.QMessageBox.question(
                self,
                "Close the application",
                "Do you want to close the application?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def start_gen_rec(self):
        # TODO: Add type check here
        wf_params = {
            'type': self.comboBox_wfparam_type.currentText(),
            'duration': float(self.lineEdit_wfparam_duration.text()),
            'sample_rate': int(self.lineEdit_wfparam_sampling.text()),
            'cycles': self.spinBox_wfparam_cycles.value(),
            'cycles_pause': float(self.lineEdit_wfparam_cycle_pause.text())
        }

        if wf_params['type'] == 'sin':
            wf_params['freq'] = float(self.lineEdit_wfparam_freq_sin.text())
        elif wf_params['type'] in ['chirp', 'sweep']:
            wf_params['f_start'] = \
                float(self.lineEdit_wfparam_freq_start.text())
            wf_params['f_end'] = float(self.lineEdit_wfparam_freq_end.text())

        if wf_params['type'] == 'sweep':
            wf_params['f_step'] = float(self.lineEdit_wfparam_freq_step.text())
            wf_params['sweep pause'] = \
                float(self.lineEdit_wfparam_sweep_pause.text())

        # TODO: allow users to select path to save the results
        # Define paths to save the recorded signal:
        current_datetime = datetime.datetime.now()
        current_timestamp = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")

        dir_results = 'recordings'
        Path(dir_results).mkdir(parents=True, exist_ok=True)

        path2save = '{}/{}'.format(dir_results, current_timestamp)
        Path(path2save).mkdir(parents=True, exist_ok=True)

        # Save the parameters:
        file_header = (
            "Simultaneous generation and recording of sound signals. \n\n"
            "Parameters of the generated signal: \n"
        )
        file_footer = (
            "\n\n"
            "All frequencies are given in Hz and all time measures"
            " are in seconds. \n\n"
            "Recording started at {} "
        ).format(current_timestamp)

        with open('{}/parameters.txt'.format(path2save), 'a') as \
                file2save_param:
            file2save_param.write(file_header)
            for key, value in wf_params.items():
                file2save_param.write("{}: {}\n".format(key, value))
            file2save_param.write(file_footer)

        # Generate and record signals:
        gr.gr_workflow(wf_params, path2save)

        # Save timestamp corresponding to the end of workflow:
        end_workflow_datetime = datetime.datetime.now()
        end_workflow_timestamp = \
            end_workflow_datetime.strftime("%Y-%m-%d-%H-%M-%S")
        file_footer = (
            "and ended at {}.\n"
        ).format(end_workflow_timestamp)

        with open('{}/parameters.txt'.format(path2save), 'a') as \
                file2save_param:
            file2save_param.write(file_footer)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MyWindow()
    mainWindow.show()
    sys.exit(app.exec_())
