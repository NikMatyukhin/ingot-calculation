from typing import Any, Optional
from gui import ui_settings

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QDialog


class SettingsDialog(QDialog):
    """Класс окна с настройками"""
    def __init__(self, parent=None, settings: QSettings = QSettings()):
        super().__init__(parent)
        self.ui = ui_settings.Ui_Dialog()
        self.ui.setupUi(self)

        # Сохранение объекта настроек для дальнейшей работы с ним
        self.settings = settings
        self.saved = False

        self.ui.save.clicked.connect(self.save)
        self.ui.cancel.clicked.connect(self.reject)
        self.ui.cutting.clicked.connect(
            lambda: self.ui.page_area.setCurrentWidget(self.ui.cutting_page))
        self.ui.rolling.clicked.connect(
            lambda: self.ui.page_area.setCurrentWidget(self.ui.rolling_page))
        self.ui.forging.clicked.connect(
            lambda: self.ui.page_area.setCurrentWidget(self.ui.forging_page))

        # Считывание настроек и внесение их в интерфейс
        self.init_settings()

    def init_settings(self):
        """Инициализация окна настроек

        Всем виджетам SpinBox и DoubleSpinBox устанавливаются значения
        по умолчанию в соответствии с сохранёнными настройками.
        Значения, возвращаемые по умолчанию из defauldValue, являются
        стандартными для всего приложения и согласованы с владельцем продукта.
        """
        self.ui.cut_allowance.setValue(self.settings.value(
            'cutting/cut_allowance', defaultValue=2, type=int))
        self.ui.end_face.setValue(self.settings.value(
            'cutting/end_face', defaultValue=0.01, type=float) * 100)
        self.ui.min_width.setValue(self.settings.value(
            'cutting/min_width', defaultValue=50, type=int))
        self.ui.guillotine.setValue(self.settings.value(
            'cutting/guillotine', defaultValue=1250, type=int))
        self.ui.min_length.setValue(self.settings.value(
            'cutting/min_length', defaultValue=100, type=int))
        self.ui.max_length.setValue(self.settings.value(
            'cutting/max_length', defaultValue=1300, type=int))
        self.ui.cutting_thickness.setValue(self.settings.value(
            'cutting/cutting_thickness', defaultValue=4.2, type=float))
        self.ui.clean_height.setValue(self.settings.value(
            'rolling/clean_height', defaultValue=3, type=int))
        self.ui.rough_edge.setValue(self.settings.value(
            'rolling/rough_edge', defaultValue=4, type=int))
        self.ui.clean_edge.setValue(self.settings.value(
            'rolling/clean_edge', defaultValue=2, type=int))
        self.ui.deformation.setValue(self.settings.value(
            'rolling/deformation', defaultValue=0.7, type=float) * 100)
        self.ui.max_rough_width.setValue(self.settings.value(
            'rolling/max_rough_width', defaultValue=450, type=int))
        self.ui.max_clean_width.setValue(self.settings.value(
            'rolling/max_clean_width', defaultValue=280, type=int))
        self.ui.min_forge_length.setValue(self.settings.value(
            'forging/min_forge_length', defaultValue=70, type=int))
        self.ui.min_forge_width.setValue(self.settings.value(
            'forging/min_forge_width', defaultValue=70, type=int))
        self.ui.min_forge_height.setValue(self.settings.value(
            'forging/min_forge_height', defaultValue=20.0, type=float))
        self.ui.max_forge_length.setValue(self.settings.value(
            'forging/max_forge_length', defaultValue=180, type=int))
        self.ui.max_forge_width.setValue(self.settings.value(
            'forging/max_forge_width', defaultValue=180, type=int))
        self.ui.max_forge_height.setValue(self.settings.value(
            'forging/max_forge_height', defaultValue=30.0, type=float))

    def save(self):
        """Сохранение настроек

        Если пользователь нажал кнопку `Сохранить`, то соответствующие значения
        перезаписываются в файл.
        Для значений, получаемых из DoubleSpinBox, проводится приведение к
        относительным единицам вместо процентов.
        """
        self.settings.setValue('cutting/end_face',
                               self.ui.end_face.value() / 100)
        self.settings.setValue('cutting/cut_allowance',
                               self.ui.cut_allowance.value())
        self.settings.setValue('cutting/guillotine',
                               self.ui.guillotine.value())
        self.settings.setValue('cutting/min_width',
                               self.ui.min_width.value())
        self.settings.setValue('cutting/min_length',
                               self.ui.min_length.value())
        self.settings.setValue('cutting/max_length',
                               self.ui.max_length.value())
        self.settings.setValue('cutting/cutting_thickness',
                               self.ui.cutting_thickness.value())
        self.settings.setValue('rolling/clean_height',
                               self.ui.clean_height.value())
        self.settings.setValue('rolling/rough_edge',
                               self.ui.rough_edge.value())
        self.settings.setValue('rolling/clean_edge',
                               self.ui.clean_edge.value())
        self.settings.setValue('rolling/deformation',
                               self.ui.deformation.value() / 100)
        self.settings.setValue('rolling/max_rough_width',
                               self.ui.max_rough_width.value())
        self.settings.setValue('rolling/max_clean_width',
                               self.ui.max_clean_width.value())
        self.settings.setValue('forging/min_forge_length',
                               self.ui.min_forge_length.value())
        self.settings.setValue('forging/min_forge_width',
                               self.ui.min_forge_width.value())
        self.settings.setValue('forging/min_forge_height',
                               self.ui.min_forge_height.value())
        self.settings.setValue('forging/max_forge_length',
                               self.ui.max_forge_length.value())
        self.settings.setValue('forging/max_forge_width',
                               self.ui.max_forge_width.value())
        self.settings.setValue('forging/max_forge_height',
                               self.ui.max_forge_height.value())
        self.saved = True
        self.accept()
