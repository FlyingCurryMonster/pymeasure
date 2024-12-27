import datetime
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from .plot_widget import PlotWidget

import logging

import pyqtgraph as pg

from ..curves import ResultsCurve
from ..Qt import QtCore, QtWidgets
from .tab_widget import TabWidget
from .plot_frame import PlotFrame

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class DatetimeAxisItem(pg.AxisItem):
    """
    Custom AxisItem to format x-axis as datetime.
    """
    def __init__(self, *args, **kwargs):
        kwargs['orientation'] = 'bottom'
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Convert axis tick values (assumed to be UTC timestamps) to human-readable datetime."""
        return [datetime.datetime.utcfromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S") for value in values]
        return [datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S") for value in values]

class PlotWidget_datetimeaxis(PlotWidget, TabWidget, QtWidgets.QWidget):
    """
    A PlotWidget subclass that supports UTC datetime on the x-axis.
    """
    def __init__(self, name, columns, x_axis=None, y_axis=None, refresh_time=0.2,
                 check_status=True, linewidth=1, parent=None):
        super().__init__(name, columns, x_axis, y_axis, refresh_time, check_status, linewidth, parent)

    def _setup_ui(self):
        """Override to use DatetimeAxisItem for the x-axis."""
        self.columns_x_label = QtWidgets.QLabel(self)
        self.columns_x_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_x_label.setText('X Axis:')
        self.columns_y_label = QtWidgets.QLabel(self)
        self.columns_y_label.setMaximumSize(QtCore.QSize(45, 16777215))
        self.columns_y_label.setText('Y Axis:')

        self.columns_x = QtWidgets.QComboBox(self)
        self.columns_y = QtWidgets.QComboBox(self)
        for column in self.columns:
            self.columns_x.addItem(column)
            self.columns_y.addItem(column)
        self.columns_x.activated.connect(self.update_x_column)
        self.columns_y.activated.connect(self.update_y_column)

        # Use a custom plot frame with a datetime-aware x-axis
        axis_items = {'bottom': DatetimeAxisItem()}
        self.plot_frame = PlotFrame(
            self.columns[0],
            self.columns[1],
            self.refresh_time,
            self.check_status,
            axis_items=axis_items,
            parent=self,
        )
        self.updated = self.plot_frame.updated
        self.plot = self.plot_frame.plot
        self.columns_x.setCurrentIndex(0)
        self.columns_y.setCurrentIndex(1)

    def new_curve(self, results, color=pg.intColor(0), **kwargs):
        """Override new_curve to ensure compatibility with datetime x-axis."""
        if 'pen' not in kwargs:
            kwargs['pen'] = pg.mkPen(color=color, width=self.linewidth)
        if 'antialias' not in kwargs:
            kwargs['antialias'] = False
        curve = ResultsCurve(results,
                             wdg=self,
                             x=self.plot_frame.x_axis,
                             y=self.plot_frame.y_axis,
                             **kwargs,
                             )
        curve.setSymbol(None)
        curve.setSymbolBrush(None)
        return curve

    def update_x_column(self, index):
        """Override update_x_column to ensure x-axis data is properly formatted."""
        axis = self.columns_x.itemText(index)
        self.plot_frame.change_x_axis(axis)
        # Assume x-axis data is in UTC timestamps
        self.plot_frame.plot.setXRange(np.min(self.plot_frame.data[axis]), np.max(self.plot_frame.data[axis]))

    def preview_widget(self, parent=None):
        """Override preview_widget to return an instance of PlotWidget_datetime."""
        return PlotWidget_datetimeaxis("Plot preview",
                                    self.columns,
                                    self.plot_frame.x_axis,
                                    self.plot_frame.y_axis,
                                    parent=parent)
