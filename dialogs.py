import math
import logging
import typing
from datetime import datetime
from typing import Dict, List, Union, Optional
from collections import Counter
from itertools import chain

from PyQt5.QtCore import (
    QPoint, QTimer, Qt, pyqtSignal, QPointF, QModelIndex, QObject
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog, QCompleter, QGraphicsScene, QMessageBox, QMenu, QToolTip, QWidget,
    QGraphicsDropShadowEffect, QProgressDialog, QAction
)

from sequential_mh.bpp_dsc.rectangle import (
    Direction, Material, Blank, Kit, Bin
)
from sequential_mh.bpp_dsc.tree import (
    BinNode, Tree, solution_efficiency
)
# from sequential_mh.bpp_dsc.prediction import optimal_ingot_size
from sequential_mh.bpp_dsc.support import dfs
from gui import (
    ui_add_article_dialog, ui_add_detail_dialog,
    ui_add_order_dialog, ui_add_ingot_dialog, ui_full_screen,
    ui_ready_ingot_dialog
)
from service import (
    OrderDataService, StandardDataService, CatalogDataService, Field, UpdatableFieldsCollection
)
from models import (
   OrderComplectsFilterProxyModel, ComplectsModel, IngotModel, 
   CatalogFilterProxyModel
)
from widgets import (
    IngotSectionDelegate,
    ListValuesDelegate
)
from exceptions import ForcedTermination
from log import log_operation_info


Number = Union[int, float]
Sizes = tuple[Number, Number, Number]


class ArticleDialog(QDialog):
    """Диалоговое окно добавления новой продукции.

    После добавления новой продукции посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """
    
    recordSavedSuccess = pyqtSignal(list)

    def __init__(self, parent: Optional[QObject] = None):
        super(ArticleDialog, self).__init__(parent)
        self.ui = ui_add_article_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление изделия')

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        # Валидация полей и установка дополнений
        self.ui.regnum.setValidator(QIntValidator(self.ui.regnum))

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)

    def confirm_adding(self):
        """Добавление данных о новой продукции в базу.

        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        id = self.ui.regnum.text()
        name = self.ui.name.text()

        # Если номер ведомости, тип и описание заполнены, то можно добавлять
        if not id or not name:
            self.timer.start(1500)
            self.highlight()
            return
        
        id = StandardDataService.save_record('articles', id=id, name=name)
        if not id:
            QMessageBox.critical(self, 'Ошибка добавления', f'Изделие не было добавлено в базу!', QMessageBox.Ok)
            return
        
        QMessageBox.information(self, f'Изделие {id}', f'Изделие №{id} успешно добавлено!', QMessageBox.Ok)
        self.recordSavedSuccess.emit([id, name])

    def highlight(self):
        if not self.ui.regnum.text():
            QToolTip.showText(self.ui.regnum.mapToGlobal(QPoint(0, 0)), "Поле необходимо заполнить", self.ui.regnum)
            self.ui.regnum.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')
        if not self.ui.name.text():
            QToolTip.showText(self.ui.name.mapToGlobal(QPoint(0, 0)), "Поле необходимо заполнить", self.ui.name)
            self.ui.name.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.regnum.setStyleSheet('')
        self.ui.name.setStyleSheet('')


class DetailDialog(QDialog):
    """Диалоговое окно добавления новой заготовки.

    После добавления новой заготовки посылает сигнал с параметрами для того,
    чтобы основное окно каталога обновило данные в модели.
    """

    recordSavedSuccess = pyqtSignal(list)

    def __init__(self, name: str, id: int, parent: Optional[QObject] = None):
        super(DetailDialog, self).__init__(parent)
        self.ui = ui_add_detail_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle(f'Добавление заготовки - {name}')
        
        # Идентификатор изделия, к которому привязываются заготовки
        self.article_id = id

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)

        # Настройка списка с направлениями
        self.directions_list = CatalogDataService.directions_list()
        self.ui.direction.addItems(list(self.directions_list.keys()))

        # Настройка списка со сплавами
        self.fusions_list = CatalogDataService.fusions_list()
        self.ui.fusion.addItems(list(self.fusions_list.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)
        self.timer.timeout.connect(self.cooldown)

    def confirm_adding(self):
        name = self.ui.name.text()
        article_id = self.article_id
        fusion_id = self.fusions_list[self.ui.fusion.currentText()]
        direction_id = self.directions_list[self.ui.direction.currentText()]
        l = self.ui.length.value()
        w = self.ui.width.value()
        h = self.ui.height.value()
        amount = self.ui.amount.value()
        priority = self.ui.priority.value()

        # Если имя заполнено, то добавляем
        if not name:
            self.timer.start(1500)
            self.highlight()
            return

        detail_id = StandardDataService.save_record(
            'details', name=name, article_id=article_id, fusion_id=fusion_id, 
            direction_id=direction_id, length=l, width=w, height=h,
            amount=amount, priority=priority
        )
        
        if not detail_id:
            QMessageBox.critical(self, 'Ошибка добавления', f'Деталь {name}не была добавлена в базу!', QMessageBox.Ok)
            return

        QMessageBox.information(self, f'Изделие {article_id}', f'Деталь "{name}" успешно добавлена!', QMessageBox.Ok)
        self.recordSavedSuccess.emit([name, fusion_id, l, w, h, amount, priority, direction_id, detail_id])

    def highlight(self):
        QToolTip.showText(self.ui.name.mapToGlobal(QPoint(0, 0)), "Укажите название заготовки", self.ui.name)
        self.ui.name.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.name.setStyleSheet('')


class OrderAddingDialog(QDialog):
    """Диалоговое окно добавления нового заказа.

    После добавления нового заказа не посылает сигнал с параметрами, т.к.
    главный сценарий использования окна включает добавление одного заказа и
    дальнейшую работу уже с ним, а не создание прочих заказов.
    """

    recordSavedSuccess = pyqtSignal(dict)
    predictedIngotSaved = pyqtSignal(dict, dict, BinNode)

    def __init__(self, parent):
        super().__init__(parent)
        self.ui = ui_add_order_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowState(Qt.WindowMaximized)

        # Иерархическая модель изделие->заготовки для формирования заказа
        # ID (int) - идентификатор конкретного изделия или заготовки
        # ADDED (bool) - статус добавления этой заготовки или изделия в заказ
        self.headers = [
            'Ведомость', 'Название', 'Сплав', 'Длина', 'Ширина', 'Толщина',
            'Количество', 'Приоритет', 'Направление', 'Идентификатор', 'Добавлено'
        ]
        self.catalog_headers = self.headers[:3]
        self.added_headers = self.headers[:9]
        self.model = ComplectsModel(self.headers)

        # Модель данных со свободными слитками
        self.ingot_model = IngotModel('unused')
        self.ingot_delegate = IngotSectionDelegate(self.ui.ingotsView)
        self.ui.ingotsView.setModel(self.ingot_model)
        self.ui.ingotsView.setItemDelegate(self.ingot_delegate)

        # Храним данные о расчитанных слитках
        self.predicted_ingots = {}

        # Прокси-модель для поиска нужных изделий (фильтр по названию)
        self.search_proxy = CatalogFilterProxyModel()
        self.search_proxy.setSourceModel(self.model)
        self.ui.treeView_1.setModel(self.search_proxy)

        # Прокси модель добавленных заготовок и изделий (фильтр по флагу ADDED)
        self.choice_proxy = OrderComplectsFilterProxyModel()
        self.choice_proxy.setSourceModel(self.model)
        self.ui.treeView_2.setModel(self.choice_proxy)

        # Назначение меню кнопке
        self.menu = QMenu()
        self.fusions = CatalogDataService.fusions_list()
        self.directions = CatalogDataService.directions_list()
        for fusion in self.fusions:
            # Под каждый сплав создаётся отдельное событие выпадающего меню
            action: QAction = self.menu.addAction(fusion)
            action.setObjectName(fusion)
            action.triggered.connect(self.calculate_ingot)
        self.ui.pushButton.setMenu(self.menu)
        

        # Выравниваем ширину колонок левого представления под контент
        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_1.resizeColumnToContents(column)
        self.ui.treeView_2.setColumnWidth(1, 170)
        self.ui.treeView_2.setColumnWidth(2, 120)

        self.fusions_delegate = ListValuesDelegate(self.fusions)
        self.directions_delegate = ListValuesDelegate(self.directions)
        self.ui.treeView_1.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.treeView_2.setItemDelegateForColumn(2, self.fusions_delegate)
        self.ui.treeView_2.setItemDelegateForColumn(8, self.directions_delegate)

        # Скрываем ненужные нам колонки в соответствии со списками заголовков
        for index, column in enumerate(self.headers):
            self.ui.treeView_1.setColumnHidden(index, column not in self.catalog_headers)
            self.ui.treeView_2.setColumnHidden(index, column not in self.added_headers)

        # Теневой эффект у разделителя окна
        self.shadow_effect = QGraphicsDropShadowEffect()
        self.shadow_effect.setColor(Qt.gray)
        self.shadow_effect.setYOffset(0)
        self.shadow_effect.setXOffset(6)
        self.shadow_effect.setBlurRadius(13)
        self.ui.splitter.handle(1).setGraphicsEffect(self.shadow_effect)

        # Связываем сигналы и слоты
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.searchName.textChanged.connect(self.search_proxy.name)
        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)

    def show_context_menu(self, point: QPointF):
        """Метод вызова контекстного меню.

        Отвечает за добавление и удаление заготовок и изделий из комплектации
        заказа (путём изменения флага ADDED у записи или записей).

        :param point: Точка вызова контекстного меню
        :type point: QPointF
        """
        menu = QMenu()
        if self.ui.treeView_1.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.treeView_1.currentIndex().parent().isValid():
                    add = menu.addAction('Добавить заготовку')
                    add.triggered.connect(self.add_detail_to_complect)
                else:
                    add = menu.addAction('Добавить изделие целиком')
                    add.triggered.connect(self.add_article_to_complect)
        if self.ui.treeView_2.hasFocus():
            if self.model.rowCount(QModelIndex()):
                if self.ui.treeView_2.currentIndex().parent().isValid():
                    delete = menu.addAction('Убрать заготовку')
                    delete.triggered.connect(self.remove_detail_from_complect)
                else:
                    delete = menu.addAction('Убрать изделие целиком')
                    delete.triggered.connect(self.remove_article_from_complect)
        menu.exec_(self.mapToGlobal(point))

    def add_article_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)
        # Колонка со сплавами по другому размер не меняет
        self.ui.treeView_2.setColumnWidth(2, 93)
        self.ui.treeView_2.expandAll()

    def add_detail_to_complect(self):
        index = self.search_proxy.mapToSource(self.ui.treeView_1.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, True, Qt.EditRole)

        parent_state_index = self.model.index(parent.row(), 10, QModelIndex())
        self.model.setData(parent_state_index, True, Qt.EditRole)

        for column in range(self.model.columnCount(QModelIndex())):
            self.ui.treeView_2.resizeColumnToContents(column)
        # Колонка со сплавами по другому размер не меняет
        self.ui.treeView_2.setColumnWidth(2, 93)
        self.ui.treeView_2.expandAll()

    def remove_article_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        parent_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(parent_state_index, False, Qt.EditRole)

        # Если убирается изделие, то убираются и все его заготовки
        for row in range(self.model.rowCount(index)):
            child_state_index = self.model.index(row, 10, index)
            self.model.setData(child_state_index, False, Qt.EditRole)

    def remove_detail_from_complect(self):
        index = self.choice_proxy.mapToSource(self.ui.treeView_2.currentIndex())
        parent = self.model.parent(index)

        # HACK: если не перенести индекс на первую колонку, работать не будет
        index = self.model.index(index.row(), 0, parent)

        # Если является последней убираемой заготовкой, то убрать и изделие
        child_state_index = self.model.index(index.row(), 10, parent)
        self.model.setData(child_state_index, False, Qt.EditRole)
        if not self.article_have_details(parent):
            row = parent.row()
            parent_state_index = self.model.index(row, 10, QModelIndex())
            self.model.setData(parent_state_index, False, Qt.EditRole)

    def article_have_details(self, index: QModelIndex) -> bool:
        """Проверка наличия другой выбранной заготовки в пределах изделия.

        :param index: Ссылка на проверяемую запись
        :type index: QModelIndex
        :return: Истина, если есть другие заготовки, и ложь в обратном случае
        :rtype: bool
        """
        rows_states = []
        for row in range(self.model.rowCount(index)):
            row_index = self.model.index(row, 10, index)
            rows_states.append(self.model.data(row_index, Qt.DisplayRole))
        return any(rows_states)

    def calculate_ingot(self):
        sender = self.sender()

        # По свойству objectName узнаём о выбранном сплаве
        fusion_name = sender.objectName()
        material = Material(fusion_name, 2.2, 1.)

        progress = QProgressDialog('OCI', 'Отмена', 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle('Рассчет слитка под ПЗ')
        progress.forceShow()
        # FIXME: получить имя заказа
        # FIXME: а имени может и не быть, расчёт слитков происходит при добавлении заказа
        order_name = 'НОВЫЙ ЗАКАЗ'
        progress.setLabelText('Процесс расчета слитка под ПЗ...')

        if not self.choice_proxy.rowCount(QModelIndex()):
            QMessageBox.critical(self, 'Ошибка добавления', 'Должно быть добавлено хотя бы одно изделие!', QMessageBox.Ok)
            return
        
        details = self.get_details_kit(material)
        if details.is_empty():
            QMessageBox.information(self, 'Добавление слитка', 'Слитки такого сплава не найдены.', QMessageBox.Ok)
            progress.close()
            return
        
        log_operation_info(
            'start_ic',
            {
                'name': order_name, 'alloy': fusion_name,
                'blanks': details.qty(), 'heights': len(details.keys())
            },
        )
        
        try:
            sizes, tree, efficiency = self.predict_size(
                material, details, progress=progress
            )
            log_operation_info(
                'end_ic',
                {
                    'name': order_name, 'alloy': fusion_name,
                    'size': f'{sizes[0]}x{sizes[1]}x{sizes[2]}',
                    'efficiency': efficiency
                },
            )
        except ForcedTermination:
            log_operation_info(
                'user_inter_ic', {'name': order_name, 'alloy': fusion_name}
            )
            QMessageBox.information(self, 'Внимание', 'Процесс расчета слитка был прерван!', QMessageBox.Ok)
            return
        except Exception as exception:
            log_operation_info(
                'error_ic', {
                    'name': order_name, 'alloy': fusion_name, 'exception': exception
                }
            )
            QMessageBox.critical(
                self, 'Расчёт слитка завершился с ошибкой', f'{exception}', QMessageBox.Ok
            )
            return
        else:
            data_row = {
                'id': 0,
                'status_id': 4,
                'fusion_id': self.fusions[fusion_name],
                'batch': None,
                'size': sizes,
            }
            for row in range(self.ingot_model.rowCount()):
                ingot_index = self.ingot_model.index(row, 0, QModelIndex())
                if ingot_index.data(Qt.DisplayRole)['status_id'] == 1:
                    continue
                if self.fusions[fusion_name] == ingot_index.data(Qt.DisplayRole)['fusion_id']:
                    self.ingot_model.deleteRow(row, QModelIndex())
                    break
            self.ingot_model.appendRow(data_row)
            self.predicted_ingots[self.fusions[fusion_name]] = {'tree': tree.root, 'efficiency': round(efficiency, 2)}
        progress.close()

    def get_details_kit(self, material: Material) -> Kit:
        details = []
        # Переходим по всем выбранным изделиям
        for row in range(self.choice_proxy.rowCount(QModelIndex())):
            parent_proxy_index = self.choice_proxy.index(row, 0, QModelIndex())
            parent = self.choice_proxy.mapToSource(parent_proxy_index)
            
            # HACK: без этого работать не будет
            parent = self.model.index(parent.row(), 0, QModelIndex())
            parent_name_index = self.model.index(parent.row(), 1, QModelIndex())
            parent_name = self.model.data(parent_name_index, Qt.DisplayRole)
            
            # Переходим по всем заготовкам в изделии
            for sub_row in range(self.model.rowCount(parent)):
                fusion_id = int(self.model.data(self.model.index(sub_row, 2, parent), Qt.DisplayRole))
                detail_fusion = StandardDataService.get_by_id('fusions', Field('id', fusion_id))[1]
                
                # Если не совпадают сплав заготовки и выбранного слитка - пропускаем
                if detail_fusion != material.name:
                    continue
                
                # Если заготовка выбрана <ADDED == True>
                added_index = self.model.index(sub_row, 10, parent)
                if self.model.data(added_index, Qt.DisplayRole):
                    name: str = self.model.data(self.model.index(sub_row, 1, parent), Qt.DisplayRole)
                    length = int(self.model.data(self.model.index(sub_row, 3, parent), Qt.DisplayRole))
                    width = int(self.model.data(self.model.index(sub_row, 4, parent), Qt.DisplayRole))
                    height = float(self.model.data(self.model.index(sub_row, 5, parent), Qt.DisplayRole))
                    sizes: Sizes = (length, width, height)
                    amount = int(self.model.data(self.model.index(sub_row, 6, parent), Qt.DisplayRole))
                    priority = int(self.model.data(self.model.index(sub_row, 7, parent), Qt.DisplayRole))
                    direction_id = int(self.model.data(self.model.index(sub_row, 8, parent), Qt.DisplayRole))
                    direction_code = 3 if direction_id == 0 else 2
                    direction = Direction(direction_code)
                    # Создаём заготовки из полученных данных
                    for _ in range(amount):
                        blank = Blank(*sizes, priority, direction=direction, material=material)
                        blank.name = parent_name + '_' + name
                        details.append(blank)
        kit = Kit(details)
        kit.sort('width')
        return kit

    def predict_size(self, material: Material, kit: Kit, progress=None):
        # TODO: считать из настроек максимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        max_size = self.ingot_settings['max_size']

        bin_ = Bin(*max_size, material=material)
        root = BinNode(bin_, kit=kit)
        tree = Tree(root)

        # TODO: считать из настроек минимальные параметры слитка
        #       без припусков на фрезеровку и погрешность!
        min_size = self.ingot_settings['min_size']

        # Дерево с рассчитанным слитком
        tree = self.parent().optimal_ingot_size(
            tree, min_size, max_size, self.settings, progress=progress
        )
        efficiency = round(solution_efficiency(tree.root, list(dfs(tree.root)), is_total=True), 2)
        print(f'Эффективность после расчета: {efficiency}')

        # size_error = self.ingot_settings['size_error']
        # allowance = self.ingot_settings['allowance']

        # Получение слитка с учетом погрешности и припусков
        length = tree.root.bin.length # + size_error + 2 * allowance
        width = tree.root.bin.width # + size_error + 2 * allowance
        height = tree.root.bin.height # + size_error + 2 * allowance

        return [math.ceil(length), math.ceil(width), math.ceil(height)], tree, efficiency

    def repeatable_fusions(self, indexes: List[QModelIndex]):
        fusions_id = []
        for index in indexes:
            ingot = index.data(Qt.DisplayRole)
            if ingot['fusion_id'] in fusions_id:
                return True
            fusions_id.append(ingot['fusion_id'])
        return False

    def confirm_adding(self):
        """Добавление данных о новом заказе в базу.

        Данные собираются с формы диалогового окна и проверяются на заполнение.
        """
        # Имя и статус складирования заказа - основа записи в базе данных
        order_name = self.ui.orderName.text()
        selected_indexes = self.ui.ingotsView.selectedIndexes()

        if self.repeatable_fusions(selected_indexes):
            QMessageBox.critical(self, 'Ошибка добавления', 'Выбраны слитки одинаковых сплавов.', QMessageBox.Ok)
            return

        # Если заполнено имя, выбран хотя бы один слиток и изделие
        if not order_name or not selected_indexes or not self.choice_proxy.rowCount(QModelIndex()):
            QMessageBox.critical(
                self, 'Ошибка добавления',
                'Поле названия заказа обязательно должно быть заполнено!\n'
                'Должен быть выбран хотя бы один слиток!\n'
                'Должно быть добавлено хотя бы одно изделие!', QMessageBox.Ok
            )
            return

        creation_date = datetime.today().strftime("%d_%m_%Y")
        order_id = StandardDataService.save_record('orders', status_id=1, name=order_name, date=creation_date)
        
        if not order_id:
            QMessageBox.critical(self, 'Ошибка добавления', f'Заказ {order_name} не был добавлен в базу!', QMessageBox.Ok)
            return

        used_fusions = []
        order_status = 1
        # Проходим по всем выбранным слиткам
        for index in selected_indexes:
            ingot = self.ingot_model.data(index, Qt.DisplayRole)
            # Если текущий слиток <эфемерный>, то добавляем в базу
            if ingot['status_id'] == 4:
                predicted_tree = self.predicted_ingots[ingot['fusion_id']]['tree']
                predicted_efficiency = self.predicted_ingots[ingot['fusion_id']]['efficiency']
                ingot['id'] = StandardDataService.save_record(
                    'ingots', length=ingot['size'][0], width=ingot['size'][1], height=ingot['size'][2],
                    order_id=order_id, status_id=3, efficiency=predicted_efficiency, fusion_id=ingot['fusion_id']
                )
                self.predictedIngotSaved.emit({'id': order_id, 'date': creation_date}, ingot, predicted_tree)
                order_status = 3
            # Если текущий слиток <слиток>, то обновляем связку
            else:
                StandardDataService.update_record('ingots', Field('id', ingot['id']), order_id=order_id)
            used_fusions.append(ingot['fusion_id'])

        # Добавляем записи о комплектации заказа в целом
        articles_count = 0
        details_count = 0
        complect_counter = dict()
        for row in range(self.choice_proxy.rowCount(QModelIndex())):
            parent_proxy_index = self.choice_proxy.index(row, 0, QModelIndex())
            parent = self.choice_proxy.mapToSource(parent_proxy_index)

            # HACK: без этого работать не будет
            parent = self.model.index(parent.row(), 0, QModelIndex())

            article_id_index = self.model.index(parent.row(), 0, QModelIndex())
            article_id = self.model.data(article_id_index, Qt.DisplayRole)
            article_name_index = self.model.index(parent.row(), 1, QModelIndex())
            article_name = self.model.data(article_name_index, Qt.DisplayRole)
            articles_count += 1

            # Добавляем записи о заготовках в заказе
            for sub_row in range(self.model.rowCount(parent)):
                added_index = self.model.index(sub_row, 10, parent)

                if not self.model.data(added_index, Qt.DisplayRole):
                    continue

                name_index = self.model.index(sub_row, 1, parent)
                name = self.model.data(name_index, Qt.DisplayRole)
                depth_index = self.model.index(sub_row, 5, parent)
                depth = float(self.model.data(depth_index, Qt.DisplayRole))
                amount_index = self.model.index(sub_row, 6, parent)
                amount = int(self.model.data(amount_index, Qt.DisplayRole))
                details_count += amount
                priority_index = self.model.index(sub_row, 7, parent)
                priority = int(self.model.data(priority_index, Qt.DisplayRole))
                detail_id_index = self.model.index(sub_row, 9, parent)
                detail_id = int(self.model.data(detail_id_index, Qt.DisplayRole))
                fusion_id_index = self.model.index(sub_row, 2, parent)
                fusion_id = int(self.model.data(fusion_id_index, Qt.DisplayRole))
                status_id = 0 if fusion_id in used_fusions else 6
                StandardDataService.save_record('complects', order_id=order_id, article_id=article_id,detail_id=detail_id, amount=amount, priority=priority, status_id=status_id)
                complect_counter[article_name + '_' + name] = {
                    'detail_id': int(detail_id),
                    'depth': float(depth),
                    'amount': int(amount),
                    'fusion_id': int(fusion_id),
                }
        
        # Проходим по всем выбранным слиткам
        for fusion_id in self.predicted_ingots:
            tree = self.predicted_ingots[fusion_id]['tree']
            temp = dict()
            for leave in tree.cc_leaves:
                unplaced = leave.result.unplaced
                if leave.result.height in temp:
                    if not unplaced:
                        del temp[leave.result.height]
                        continue
                temp[leave.result.height] = unplaced

            # unplaced = list(chain.from_iterable([leave.result.unplaced for leave in tree.cc_leaves]))
            unplaced_counter = Counter([blank.name for blank in list(chain.from_iterable(temp.values()))])
            updates = UpdatableFieldsCollection(['status_id', 'total', 'order_id', 'detail_id'])
            order = Field('order_id', order_id)
            
            for name in unplaced_counter:
                if complect_counter[name]['fusion_id'] != fusion_id:
                    continue
                
                detail = Field('detail_id', complect_counter[name]['detail_id'])
                
                # Если количество заготовок совпадает с остатком
                if complect_counter[name]['amount'] == unplaced_counter[name]:
                    print(name, complect_counter[name]['amount'], unplaced_counter[name])
                    updates.append(Field('status_id', 4), Field('total', 0), order, detail)
                # Если количество заготовок не совпадает с остатком
                else:
                    updates.append(Field('status_id', 5), Field('total', complect_counter[name]['amount'] - unplaced_counter[name]), order, detail)
            
            # В конце проходимся по всем заготовкам чтобы найти пропущенные толщины
            for name in complect_counter:
                if complect_counter[name]['fusion_id'] != fusion_id:
                    continue
                
                detail = Field('detail_id', complect_counter[name]['detail_id'])
                if complect_counter[name]['depth'] not in [leave.bin.height for leave in tree.cc_leaves]:
                    updates.append(Field('status_id', 4), Field('total', 0), order, detail)
                # Если количество неразмещённых заготовок равно нулю
                elif name not in unplaced_counter:
                    updates.append(Field('status_id', 1), Field('total', complect_counter[name]['amount']), order, detail)
            OrderDataService.update_statuses(updates)

        order_efficiency = OrderDataService.efficiency(Field('order_id', order_id))
        StandardDataService.update_record('orders', Field('id', order_id), status_id=order_status, efficiency=order_efficiency)
        pack = {
            'id': order_id,
            'status_id': order_status,
            'name': order_name,
            'step': 0.0,
            'efficiency': order_efficiency,
            'date': creation_date,
            'articles': articles_count,
            'details': details_count,
        }
        self.recordSavedSuccess.emit(pack)
        logging.info('Заказ %(name)s добавлен в базу.', {'name': order_name})
        self.accept()

    def set_settings(self, settings: Dict, ingot_settings: Dict):
        self.settings = settings
        self.ingot_settings = ingot_settings


class IngotAddingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = ui_add_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Добавление слитка')

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        # Настройка списка со сплавами
        self.fusions = CatalogDataService.fusions_list()
        self.ui.fusion.addItems(list(self.fusions.keys()))

        self.ui.add.clicked.connect(self.confirm_adding)
        self.ui.cancel.clicked.connect(self.reject)

    def confirm_adding(self):
        batch = self.ui.batch.text()
        length = self.ui.length.value()
        width = self.ui.width.value()
        height = self.ui.height.value()
        fusion = self.fusions[self.ui.fusion.currentText()]

        if not batch:
            self.timer.start(1500)
            self.highlight()
            return
        
        success = StandardDataService.save_record('ingots', fusion_id=fusion, batch=batch, length=length, width=width, height=height)
        if not success:
            QMessageBox.critical(self, 'Ошибка добавления', f'Слиток из партии {batch} не был добавлен в базу!',QMessageBox.Ok)
            return
        
        QMessageBox.information(self, f'Партия {batch}', f'Слиток из партии {batch}\nуспешно добавлен!', QMessageBox.Ok)

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), 'Укажите номер партии', self.ui.batch)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class IngotReadinessDialog(QDialog):
    def __init__(self, parent: typing.Optional[QWidget]) -> None:
        super().__init__(parent)
        self.ui = ui_ready_ingot_dialog.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Подтверждение готовности')

        # Таймер для подсветки ошибки
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cooldown)

        self.ui.add.clicked.connect(self.confirm_readiness)
        self.ui.cancel.clicked.connect(self.reject)

    def set_title_data(self, id: int, sizes: List, fusion: str):
        self.id = id
        self.ui.height_label.setText(str(sizes[0]))
        self.ui.width_label.setText(str(sizes[1]))
        self.ui.depth_label.setText(str(sizes[2]))
        self.ui.fusion_label.setText(fusion)

    def get_batch(self):
        return self.ui.batch.text()

    def confirm_readiness(self):
        batch = self.ui.batch.text()
        if not batch:
            self.timer.start(1500)
            self.highlight()
            return
        
        success = StandardDataService.update_record('ingots', Field('id', self.id), status_id=1, batch=batch)
        if not success:
            QMessageBox.critical(self, 'Ошибка добавления', f'Слиток из партии {batch} не был добавлен в базу.', QMessageBox.Ok)
            return

        self.accept()

    def highlight(self):
        QToolTip.showText(self.ui.batch.mapToGlobal(QPoint(0, 0)), 'Укажите номер партии', self.ui.batch)
        self.ui.batch.setStyleSheet('QLineEdit {border: 2px solid red; padding-left: -1px;}')

    def cooldown(self):
        self.ui.batch.setStyleSheet('')


class FullScreenWindow(QDialog):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.ui = ui_full_screen.Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('Карта: полноэкранный режим')

    def set_scene(self, scene: QGraphicsScene):
        self.ui.graphicsView.setScene(scene)
