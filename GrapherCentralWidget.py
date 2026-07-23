'''GeoGrapher的顶层控件，直接供主程序使用
'''

from __future__ import annotations
from typing import Any, Callable

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSplitter)
from PySide6.QtGui import QPainter, QIcon, QImage, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QSize, QSizeF
import qtawesome as qta

from .GeoGraphScene import GeoGraphScene
from .GeoGraphView import GeoGraphView
from .ModeControlPanel import ModeControlPanel
from .Constants import GeoMainMode, GeoSecondaryMode


__all__ = ['GrapherCentralWidget']


def _svgToIcon(path: str, size: QSize = QSize(32, 32)) -> QIcon:
    '''将位于`path`的SVG图像文件转换为大小为`size`的`QIcon`对象。

    :param path: 相对于项目根目录的路径字符串。
    :param size: 期望的大小。会将SVG等比例缩放以放入此大小。
    :returns: `QIcon`对象。
    '''
    renderer = QSvgRenderer(str(Path(__file__).parent.resolve() / path))
    img = QImage(renderer.viewBoxF().size().scaled(
        QSizeF(size), Qt.AspectRatioMode.KeepAspectRatio).toSize(),
        QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    painter = QPainter(img)
    renderer.render(painter)
    painter.end()
    return QIcon(QPixmap.fromImage(img))


class ToolbarAbovePanel(QWidget):
    '''控制面板上方的工具栏。
    '''

    def __init__(self, buttonAttrs: list[dict[str, Any]], parent=None):
        '''根据`buttonAttrs`初始化工具栏。

        :param buttonAttrs: 按钮参数。列表的每个字典元素代表一个按钮，
            应该提供`icon`和`action`字段，分别表示图标和动作。
            `icon`字段为`QIcon`对象，`action`字段为可调用对象。
        :param parent: 工具栏的父控件。
        '''
        super().__init__(parent)
        self._initUi(buttonAttrs)

    def _initUi(self, buttonAttrs: list[dict[str, Any]]):
        '''初始化界面。
        '''
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        for buttonAttr in buttonAttrs:
            button = QPushButton(buttonAttr['icon'], '', self)
            button.clicked.connect(buttonAttr['action'])
            layout.addWidget(button)
        self.setLayout(layout)


class GrapherCentralWidget(QWidget):
    '''绘图工具的顶层控件。
    '''

    def __init__(
            self, xAxis: tuple[int, int] = (-10000, 10000),
            yAxis: tuple[int, int] = (-10000, 10000), parent=None):
        '''初始化。

        :param xAxis: 绘图区横坐标的范围。
        :param yAxis: 绘图区纵坐标的范围。
        :param parent: 控件的父控件。
        '''
        super().__init__(parent)
        (self._xMin, self._xMax), (self._yMin, self._yMax) = xAxis, yAxis
        self._xLen, self._yLen = \
            self._xMax - self._xMin, self._yMax - self._yMin  # 计算绘图区宽高
        self.PANEL_PAGES = [
            {
                'title': 'Selection', 'buttons': [
                    {
                        'text': 'Selection Mode', 'checked': True,
                        'action': self.mainModeToggleAction('SELECT'),
                        'icon': _svgToIcon('Assets/Selection.svg'),
                    },
                ],
            }, {
                'title': 'Points', 'buttons': [
                    {
                        'text': 'Point',
                        'action': self.secondaryModeToggleAction('POINT'),
                        'icon': _svgToIcon('Assets/Point.svg'),
                    }, {
                        'text': 'Intersection',
                        'action': self.secondaryModeToggleAction(
                            'INTERSECTION'),
                        'icon': _svgToIcon('Assets/Intersection.svg'),
                    },
                ],
            }, {
                'title': 'Segments', 'buttons': [
                    {
                        'text': 'Segment',
                        'action': self.secondaryModeToggleAction('SEGMENT'),
                        'icon': _svgToIcon('Assets/Segment.svg'),
                    },
                ],
            }, {
                'title': 'Circles', 'buttons': [
                    {
                        'text': 'Circle',
                        'action': self.secondaryModeToggleAction('CIRCLE'),
                        'icon': _svgToIcon('Assets/Circle.svg'),
                    },
                ],
            },
        ]
        self.TOOLBAR_BUTTONS = [
            {
                'icon': qta.icon('ri.zoom-in-line'),
                'action': self.zoomInAction(),
            }, {
                'icon': qta.icon('ri.zoom-out-line'),
                'action': self.zoomOutAction(),
            },
        ]
        self._initUi()

    def _initUi(self):
        '''初始化界面。
        '''
        # 绘图场景视图
        scene = GeoGraphScene(self)
        scene.setSceneRect(self._xMin, self._yMin, self._xLen, self._yLen)
        self._view = GeoGraphView(scene, self)
        self._view.setMinimumWidth(300)

        # 控制面板
        panel = ModeControlPanel(self)
        panel.setMinimumWidth(240)
        for pageAttrs in self.PANEL_PAGES:
            panel.addPage(pageAttrs['title'], pageAttrs['buttons'])

        # 工具栏
        toolbar = ToolbarAbovePanel(self.TOOLBAR_BUTTONS, self)
        toolbar.setMinimumWidth(240)

        # 左侧所有内容
        panelLayout = QVBoxLayout()
        panelLayout.setContentsMargins(0, 0, 0, 0)
        panelLayout.addWidget(toolbar)
        panelLayout.addWidget(panel)
        panelWidget = QWidget(self)
        panelWidget.setLayout(panelLayout)

        # 分隔控件，用户可以手动调整左右宽度
        splitter = QSplitter(self)
        splitter.addWidget(panelWidget)
        splitter.addWidget(self._view)

        centralLayout = QHBoxLayout()
        centralLayout.addWidget(splitter)
        self.setLayout(centralLayout)

    def mainModeToggleAction(self, modeName: str) -> Callable[[], None]:
        '''返回一个可调用对象，表示将主绘图模式切换为`modeName`的动作。
        '''
        return lambda: self._view.toggleMainMode(
            getattr(GeoMainMode, modeName))

    def secondaryModeToggleAction(self, modeName: str) -> Callable[[], None]:
        '''返回一个可调用对象，表示将次绘图模式切换为`modeName`的动作。
        '''
        return lambda: self._view.toggleSecondaryMode(
            getattr(GeoSecondaryMode, modeName))

    def zoomInAction(self) -> Callable[[], None]:
        '''返回一个可调用对象，表示放大视图的动作。
        '''
        return lambda: self._view.zoomScaleChanged(1.25)

    def zoomOutAction(self) -> Callable[[], None]:
        '''返回一个可调用对象，表示缩小视图的动作。
        '''
        return lambda: self._view.zoomScaleChanged(.8)
