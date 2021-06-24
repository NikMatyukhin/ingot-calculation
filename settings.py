from gui import ui_settings

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QDialog, QApplication


class SettingsDialog(QDialog):
    """Класс окна с настройками"""
    def __init__(self, parent=None, settings: QSettings = QSettings()):
        super(SettingsDialog, self).__init__(parent)
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
        self.ui.forging.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.forgingPage)
        )
        self.ui.save.clicked.connect(self.save)
        self.ui.cancel.clicked.connect(self.reject)

    def init_settings(self):
        """Инициализация окна настроек

        Всем виджетам SpinBox и DoubleSpinBox устанавливаются значения
        по умолчанию в соответствии с сохранёнными настройками.
        Значения, возвращаемые по умолчанию из defauldValue, являются
        стандартными для всего приложения и согласованы с владельцем продукта.
        """
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

        self.ui.spinBox_13.setValue(self.settings.value(
            'forging/min_height', defaultValue=70, type=int))
        self.ui.spinBox_14.setValue(self.settings.value(
            'forging/min_width', defaultValue=70, type=int))
        self.ui.doubleSpinBox_5.setValue(self.settings.value(
            'forging/min_depth', defaultValue=20.0, type=float))

        self.ui.spinBox_16.setValue(self.settings.value(
            'forging/max_height', defaultValue=185, type=int))
        self.ui.spinBox_15.setValue(self.settings.value(
            'forging/max_width', defaultValue=185, type=int))
        self.ui.doubleSpinBox_6.setValue(self.settings.value(
            'forging/max_depth', defaultValue=30.0, type=float))
        self.ui.doubleSpinBox_7.setValue(self.settings.value(
            'forging/size_error', defaultValue=2.0, type=float))
        self.ui.doubleSpinBox_4.setValue(self.settings.value(
            'forging/allowance', defaultValue=1.5, type=float))

    def save(self):
        """Сохранение настроек

        Если пользователь нажал кнопку `Сохранить`, то соответствующие значения
        перезаписываются в файл.
        Для значений, получаемых из DoubleSpinBox, проводится приведение к
        относительным единицам вместо процентов.
        """
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

        self.settings.setValue('forging/min_height',
                               self.ui.spinBox_13.value())
        self.settings.setValue('forging/min_width',
                               self.ui.spinBox_14.value())
        self.settings.setValue('forging/min_depth',
                               self.ui.doubleSpinBox_5.value())

        self.settings.setValue('forging/max_height',
                               self.ui.spinBox_16.value())
        self.settings.setValue('forging/max_width',
                               self.ui.spinBox_15.value())
        self.settings.setValue('forging/max_depth',
                               self.ui.doubleSpinBox_6.value())
        self.settings.setValue('forging/size_error',
                               self.ui.doubleSpinBox_7.value())
        self.settings.setValue('forging/allowance',
                               self.ui.doubleSpinBox_4.value())

        self.saved = True
        self.accept()
