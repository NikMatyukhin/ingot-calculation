from gui import ui_settings

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QApplication


class Settings(QDialog):

    def __init__(self, parent=None, settings: QSettings = QSettings()):
        super(Settings, self).__init__(parent)
        self.ui = ui_settings.Ui_Dialog()
        self.ui.setupUi(self)
        self.settings = settings
        self.saved = False

        self.init_settings()

        self.ui.cutting.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.cuttingPage)
        )
        self.ui.rolling.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.rollingPage)
        )

        self.ui.save.clicked.connect(self.save_settings)
        self.ui.cancel.clicked.connect(self.reject)

    def init_settings(self):
        self.ui.spinBox_9.setValue(self.settings.value(
            'cutting/cut_allowance', defaultValue=2, type=int))
        self.ui.doubleSpinBox.setValue(self.settings.value(
            'cutting/end_face', defaultValue=0.01, type=float) * 100)
        self.ui.spinBox_6.setValue(self.settings.value(
            'cutting/min_width', defaultValue=50, type=int))
        self.ui.spinBox_8.setValue(self.settings.value(
            'cutting/guilliotine', defaultValue=1200, type=int))
        self.ui.spinBox_7.setValue(self.settings.value(
            'cutting/min_height', defaultValue=100, type=int))
        self.ui.spinBox_5.setValue(self.settings.value(
            'cutting/max_height', defaultValue=1200, type=int))
        self.ui.doubleSpinBox_3.setValue(self.settings.value(
            'cutting/cutting_thickness', defaultValue=4.2, type=float))

        self.ui.spinBox_4.setValue(self.settings.value(
            'rolling/clean_depth', defaultValue=3, type=int))
        self.ui.spinBox_11.setValue(self.settings.value(
            'rolling/rough_edge', defaultValue=4, type=int))
        self.ui.spinBox_12.setValue(self.settings.value(
            'rolling/clean_edge', defaultValue=2, type=int))
        self.ui.doubleSpinBox_2.setValue(self.settings.value(
            'rolling/deformation', defaultValue=0.7, type=float) * 100)
        self.ui.spinBox_2.setValue(self.settings.value(
            'rolling/max_rough_width', defaultValue=450, type=int))
        self.ui.spinBox_3.setValue(self.settings.value(
            'rolling/max_clean_width', defaultValue=400, type=int))

    def save_settings(self):
        self.settings.setValue('cutting/end_face',
                               self.ui.doubleSpinBox.value() / 100)
        self.settings.setValue('cutting/cut_allowance',
                               self.ui.spinBox_9.value())
        self.settings.setValue('cutting/guilliotine',
                               self.ui.spinBox_8.value())
        self.settings.setValue('cutting/min_width',
                               self.ui.spinBox_6.value())
        self.settings.setValue('cutting/min_height',
                               self.ui.spinBox_7.value())
        self.settings.setValue('cutting/max_height',
                               self.ui.spinBox_5.value())
        self.settings.setValue('cutting/cutting_thickness',
                               self.ui.doubleSpinBox_3.value())

        self.settings.setValue('rolling/clean_depth',
                               self.ui.spinBox_4.value())
        self.settings.setValue('rolling/rough_edge',
                               self.ui.spinBox_11.value())
        self.settings.setValue('rolling/clean_edge',
                               self.ui.spinBox_12.value())
        self.settings.setValue('rolling/deformation',
                               self.ui.doubleSpinBox_2.value() / 100)
        self.settings.setValue('rolling/max_rough_width',
                               self.ui.spinBox_2.value())
        self.settings.setValue('rolling/max_clean_width',
                               self.ui.spinBox_3.value())

        self.saved = True
        self.accept()


if __name__ == '__main__':
    application = QApplication()

    window = Settings()
    window.show()

    application.exec_()
