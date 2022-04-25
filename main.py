from PyQt5 import QtWidgets
import sys
import os

# Import local modules:
import app_framework as af

# Convert UI to python code (should be removed later)
# os.system('pyuic5 -x gui_main_window.ui -o gui_main_window.py')

# Create GUI application
app = QtWidgets.QApplication(sys.argv)
form = af.MyWindow()
form.show()
sys.exit(app.exec_())