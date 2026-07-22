'''控制面板，用于切换绘图模式
'''

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtWidgets import (
    QWidget, QToolBox, QButtonGroup, QPushButton, QLabel)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSize, QTimer


__all__ = ['ModeControlPanel']


class ModeToggleButton(QPushButton):
    '''模式切换按钮。
    '''

    def __init__(self, icon: QIcon | None, text: str, parent=None):
        '''初始化按钮。按钮图标为`icon`，文字为`text`。
        不使用`QPushButton`原生功能，而是使用两个`QLabel`渲染图标与文字。
        '''
        super().__init__(parent)
        self.setCheckable(True)
        self._initUi(icon, text)

    def _initUi(self, icon: QIcon | None, text: str):
        '''初始化界面。使用两个`QLabel`上下摆放图标与文字。
        '''
        iconLabel = QLabel()      # 图标
        if icon is not None:
            iconLabel.setPixmap(icon.pixmap(32, 32))
        iconLabel.setFixedSize(32, 32)

        textLabel = QLabel(text)  # 文字
        textLabel.setFont(QFont(None, 8))
        textLabel.setWordWrap(True)
        textLabel.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        layout.addWidget(iconLabel, alignment=Qt.AlignCenter)
        layout.addWidget(textLabel, alignment=Qt.AlignCenter)


class ModeToggleButtonGroupBox(QWidget):
    '''一组模式切换按钮。支持根据控件宽度动态控制一行的按钮数量。
    '''

    def __init__(self, buttonSize: QSize = QSize(70, 80), parent=None):
        '''初始化按钮组。

        :param buttonSize: 按钮尺寸。
        :param parent: 控件的父控件，必须传入以用于获取控件宽度。
        '''
        super().__init__(parent)
        self._buttonSize: QSize = buttonSize           # 按钮尺寸
        self._buttonList: list[ModeToggleButton] = []  # 按钮列表
        self._gridColumnCount: int | None = None       # 每行按钮数量
        self._initUi()

    def _initUi(self):
        '''初始化按钮组界面。
        '''
        # 必须使用`QSizePolicy.Ignored`使控件宽度严格等于父控件宽度
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self._gridLayout: QGridLayout = QGridLayout(self)
        self._gridLayout.setSpacing(12)
        self._gridLayout.setContentsMargins(10, 10, 10, 10)
        self._gridLayout.setAlignment(Qt.AlignTop)

    def addButton(self, button: ModeToggleButton):
        '''添加一个按钮。
        '''
        button.setFixedSize(self._buttonSize)
        self._buttonList.append(button)

    def _clearButtons(self):
        '''清空所有按钮，但按钮仍保存在`self._buttonList`中。
        '''
        while self._gridLayout.count():
            item = self._gridLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)

    def relayoutButtons(self):
        '''重新布局按钮。所有按钮添加完毕后要调用一次。
        '''
        containerWidth = self.parent().contentsRect().width()
        singleButtonWidth = \
            self._buttonSize.width() + self._gridLayout.spacing()
        columnCount = max(1, containerWidth // singleButtonWidth)

        if columnCount != self._gridColumnCount:  # 只有在需要更新时重新布局
            self._clearButtons()
            self._gridColumnCount = columnCount
            for i, button in enumerate(self._buttonList):
                self._gridLayout.addWidget(
                    button, i // columnCount, i % columnCount)

    def resizeEvent(self, event):
        '''控件尺寸变化时重新布局。
        '''
        super().resizeEvent(event)
        self.relayoutButtons()


class ModeControlPanel(QToolBox):
    '''绘图模式切换控制面板。
    '''

    def __init__(self, parent=None):
        '''初始化。
        '''
        super().__init__(parent)
        self._buttonGroup = QButtonGroup(self)
        self._buttonGroup.setExclusive(True)  # 使用按钮组，只能同时选中一个绘图模式

    def addPage(self, title: str, buttonAttrs: list[dict[str, Any]]) \
            -> ModeToggleButtonGroupBox:
        '''添加一个选项卡并返回。

        :param title: 选项卡标题。
        :param buttonAttrs: 选项卡中按钮的信息。
            必须提供`text`（文本），表示按钮中的文字；
            可以提供`icon`（`QIcon`对象）、`action`（可调用对象），分别表示按钮图标与选中时的操作；
            可以提供`checked`（`bool`），表示按钮是否被选中，最多只有一个按钮会被选中。
        :returns: 创建完成的选项卡。
        '''
        page = ModeToggleButtonGroupBox(parent=self)
        for buttonAttr in buttonAttrs:
            text = buttonAttr['text']
            icon = buttonAttr.get('icon')
            action = buttonAttr.get('action')
            button = ModeToggleButton(icon, text)
            if action is not None:
                button.toggled.connect(action)
            if buttonAttr.get('checked', False):
                button.setChecked(True)
            self._buttonGroup.addButton(button)
            page.addButton(button)
        self.addItem(page, title)
        # 要等待控件宽度完成更新后重新布局按钮，不能直接调用
        QTimer.singleShot(0, page.relayoutButtons)
        return page
