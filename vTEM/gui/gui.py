from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from vTEM import Lens, ObjectiveLens, RayNode, Ray, Source, RayTransmitError
from pathlib import Path
import matplotlib.pyplot as plt

import sys


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi(str(Path(__file__).parent / 'source/qtcreator/mainwindow.ui'), self)


class vTEMModel(QObject):
    updated = pyqtSignal([], [bool])

    def __init__(self, *args, **kwargs):

        super(vTEMModel, self).__init__(*args, **kwargs)
        self.source = Source(0, 220, 10, name='Source')
        self.CL1 = Lens(200, 2, name='CL1')
        self.CL2 = Lens(180, 2, name='CL2')
        self.CL3 = Lens(160, 2, name='CL3')
        self.CM = Lens(140, 2, name='CM')
        self.OL = ObjectiveLens(120, (2, 2), 10)
        self.OM = Lens(100, 2, name='OM')
        self.IL1 = Lens(80, 2, name='IL1')
        self.IL2 = Lens(60, 2, name='IL2')
        self.IL3 = Lens(40, 2, name='IL3')
        self.PL = Lens(20, 2, name='PL')

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.get_lenses()[item]
        elif isinstance(item, str):
            for lens in self:
                if lens.name == item:
                    return lens
            raise KeyError('Lens {key} not found'.format(key=item))
        raise TypeError(
            'Error when indexing using {item!r}. Indexing using objects of type {t} is not supported'.format(item=item,
                                                                                                             t=type(
                                                                                                                 item)))

    def __iter__(self):
        for lens in self.get_lenses():
            yield lens

    def get_lenses(self, sort=True):
        lenses = [self.CL1, self.CL2, self.CL3, self.CM, self.OL, self.OM, self.IL1, self.IL2, self.IL3, self.PL]
        if sort:
            lenses.sort(key=lambda x: x.y, reverse=True)
        return lenses

    def change_source(self, x=None, y=None, size=None):
        changed = False
        if x is not None:
            self.source.set_x(x)
            changed = True
        if y is not None:
            self.source.set_y(y)
            changed = True
        if size is not None:
            self.source.set_size(size)
            changed = True

        if changed:
            self.updated.emit()
        self.updated[bool].emit(changed)

    def change_lens(self, name, x=None, y=None, f=None, gap=None, prefield=None, postfield=None, couple=None):
        if not isinstance(name, str):
            raise TypeError('Name {name!r} must be of type str, not {t}'.format(name=name, t=type(name)))
        lens = self[name]
        changed = False
        if x is not None:
            lens.set_x(x)
            changed = True
        if y is not None:
            lens.set_y(y)
            changed = True
        if f is not None:
            lens.set_f(f)
            changed = True
        if isinstance(lens, ObjectiveLens) and gap is not None:
            lens.set_gap(gap)
            changed = True
        if isinstance(lens, ObjectiveLens) and prefield is not None:
            lens.set_prefield(prefield)
            changed = True
        if isinstance(lens, ObjectiveLens) and postfield is not None:
            lens.set_postfield(postfield)
            changed = True
        if isinstance(lens, ObjectiveLens) and couple is not None:
            lens.couple(couple)
            changed = True

        if changed:
            self.updated.emit()
        self.updated[bool].emit(changed)


class vTEMController(object):

    def __init__(self, view, model):
        """
        Create a controller for a vTEM
        :param view: The gui object to show and control the vTEM
        :param model: The vTEM model to control
        :type view: MainWindow
        :type model: vTEMModel
        """
        self._view = view
        self._model = model
        self.setup_lens_widgets()
        #self.set_y_spinbox_limits()
        self.setup_source_control()
        self.setup_lens_control()
        self.setup_screen_control()
        self.setup_style_control()
        self._view.plotPushButton.clicked.connect(self.show)
        self._view.exportPushButton.clicked.connect(self.export)
        self._view.autoscaleRadioButton.toggled.connect(self.show)
        self._model.updated.connect(self.show)

        self.show()

    def setup_source_control(self):
        self._view.sourceXSpinBox.valueChanged.connect(lambda x: self._model.change_source(x=x))
        self._view.sourceYSpinBox.valueChanged.connect(lambda y: self._model.change_source(y=y))
        self._view.sourceSizeSpinBox.valueChanged.connect(lambda size: self._model.change_source(size=size))
        self._view.sourceAngleSpinBox.valueChanged.connect(self.show)
        self._view.symmetricSourceCheckBox.clicked.connect(self.show)

    def setup_screen_control(self):
        self._view.screenSpinBox.valueChanged.connect(self.show)

    def setup_lens_widgets(self):
        self._view.cl1FSpinBox.setSingleStep(0.01)
        self._view.cl2FSpinBox.setSingleStep(0.01)
        self._view.cl3FSpinBox.setSingleStep(0.01)
        self._view.cmFSpinBox.setSingleStep(0.01)
        self._view.omFSpinBox.setSingleStep(0.01)
        self._view.olFSpinBox.setSingleStep(0.01)
        self._view.olPrefieldSpinBox.setSingleStep(0.01)
        self._view.il1FSpinBox.setSingleStep(0.01)
        self._view.il2FSpinBox.setSingleStep(0.01)
        self._view.il3FSpinBox.setSingleStep(0.01)
        self._view.plFSpinBox.setSingleStep(0.01)

        self._view.cl1FSpinBox.setDecimals(5)
        self._view.cl2FSpinBox.setDecimals(5)
        self._view.cl3FSpinBox.setDecimals(5)
        self._view.cmFSpinBox.setDecimals(5)
        self._view.omFSpinBox.setDecimals(5)
        self._view.olFSpinBox.setDecimals(5)
        self._view.olPrefieldSpinBox.setDecimals(5)
        self._view.il1FSpinBox.setDecimals(5)
        self._view.il2FSpinBox.setDecimals(5)
        self._view.il3FSpinBox.setDecimals(5)
        self._view.plFSpinBox.setDecimals(5)

        #Connect spinboxes to sliders
        self._view.cl1XSpinBox.valueChanged.connect(lambda x: self._view.cl1XSlider.setValue(x*1E2))
        self._view.cl2XSpinBox.valueChanged.connect(lambda x: self._view.cl2XSlider.setValue(x*1E2))
        self._view.cl3XSpinBox.valueChanged.connect(lambda x: self._view.cl3XSlider.setValue(x*1E2))
        self._view.cmXSpinBox.valueChanged.connect(lambda x: self._view.cmXSlider.setValue(x*1E2))
        self._view.olXSpinBox.valueChanged.connect(lambda x: self._view.olXSlider.setValue(x*1E2))
        self._view.omXSpinBox.valueChanged.connect(lambda x: self._view.omXSlider.setValue(x*1E2))
        self._view.il1XSpinBox.valueChanged.connect(lambda x: self._view.il1XSlider.setValue(x*1E2))
        self._view.il2XSpinBox.valueChanged.connect(lambda x: self._view.il2XSlider.setValue(x*1E2))
        self._view.il3XSpinBox.valueChanged.connect(lambda x: self._view.il3XSlider.setValue(x*1E2))
        self._view.plXSpinBox.valueChanged.connect(lambda x: self._view.plXSlider.setValue(x*1E2))

        self._view.cl1YSpinBox.valueChanged.connect(lambda x: self._view.cl1YSlider.setValue(x*1E2))
        self._view.cl2YSpinBox.valueChanged.connect(lambda x: self._view.cl2YSlider.setValue(x*1E2))
        self._view.cl3YSpinBox.valueChanged.connect(lambda x: self._view.cl3YSlider.setValue(x*1E2))
        self._view.cmYSpinBox.valueChanged.connect(lambda x: self._view.cmYSlider.setValue(x*1E2))
        self._view.olYSpinBox.valueChanged.connect(lambda x: self._view.olYSlider.setValue(x*1E2))
        self._view.omYSpinBox.valueChanged.connect(lambda x: self._view.omYSlider.setValue(x*1E2))
        self._view.il1YSpinBox.valueChanged.connect(lambda x: self._view.il1YSlider.setValue(x*1E2))
        self._view.il2YSpinBox.valueChanged.connect(lambda x: self._view.il2YSlider.setValue(x*1E2))
        self._view.il3YSpinBox.valueChanged.connect(lambda x: self._view.il3YSlider.setValue(x*1E2))
        self._view.plYSpinBox.valueChanged.connect(lambda x: self._view.plYSlider.setValue(x*1E2))

        self._view.cl1FSpinBox.valueChanged.connect(lambda x: self._view.cl1FSlider.setValue(x*1E5))
        self._view.cl2FSpinBox.valueChanged.connect(lambda x: self._view.cl2FSlider.setValue(x*1E5))
        self._view.cl3FSpinBox.valueChanged.connect(lambda x: self._view.cl3FSlider.setValue(x*1E5))
        self._view.cmFSpinBox.valueChanged.connect(lambda x: self._view.cmFSlider.setValue(x*1E5))
        self._view.olFSpinBox.valueChanged.connect(lambda x: self._view.olFSlider.setValue(x*1E5))
        self._view.olPrefieldSpinBox.valueChanged.connect(lambda x: self._view.olPrefieldSlider.setValue(x*1E5))
        self._view.omFSpinBox.valueChanged.connect(lambda x: self._view.omFSlider.setValue(x*1E5))
        self._view.il1FSpinBox.valueChanged.connect(lambda x: self._view.il1FSlider.setValue(x*1E5))
        self._view.il2FSpinBox.valueChanged.connect(lambda x: self._view.il2FSlider.setValue(x*1E5))
        self._view.il3FSpinBox.valueChanged.connect(lambda x: self._view.il3FSlider.setValue(x*1E5))
        self._view.plFSpinBox.valueChanged.connect(lambda x: self._view.plFSlider.setValue(x*1E5))

        self._view.olGapSpinBox.valueChanged.connect(lambda x: self._view.olGapSlider.setValue(x*1E2))
        self._view.olPrefieldSpinBox.valueChanged.connect(lambda x: self._view.olPrefieldSlider.setValue(x*1E5))

        #Connect sliders to spinboxes
        self._view.cl1XSlider.valueChanged.connect(lambda x: self._view.cl1XSpinBox.setValue(x*1E-2))
        self._view.cl2XSlider.valueChanged.connect(lambda x: self._view.cl2XSpinBox.setValue(x*1E-2))
        self._view.cl3XSlider.valueChanged.connect(lambda x: self._view.cl3XSpinBox.setValue(x*1E-2))
        self._view.cmXSlider.valueChanged.connect(lambda x: self._view.cmXSpinBox.setValue(x*1E-2))
        self._view.olXSlider.valueChanged.connect(lambda x: self._view.olXSpinBox.setValue(x*1E-2))
        self._view.omXSlider.valueChanged.connect(lambda x: self._view.omXSpinBox.setValue(x*1E-2))
        self._view.il1XSlider.valueChanged.connect(lambda x: self._view.il1XSpinBox.setValue(x*1E-2))
        self._view.il2XSlider.valueChanged.connect(lambda x: self._view.il2XSpinBox.setValue(x*1E-2))
        self._view.il3XSlider.valueChanged.connect(lambda x: self._view.il3XSpinBox.setValue(x*1E-2))
        self._view.plXSlider.valueChanged.connect(lambda x: self._view.plXSpinBox.setValue(x*1E-2))

        self._view.cl1YSlider.valueChanged.connect(lambda x: self._view.cl1YSpinBox.setValue(x*1E-2))
        self._view.cl2YSlider.valueChanged.connect(lambda x: self._view.cl2YSpinBox.setValue(x*1E-2))
        self._view.cl3YSlider.valueChanged.connect(lambda x: self._view.cl3YSpinBox.setValue(x*1E-2))
        self._view.cmYSlider.valueChanged.connect(lambda x: self._view.cmYSpinBox.setValue(x*1E-2))
        self._view.olYSlider.valueChanged.connect(lambda x: self._view.olYSpinBox.setValue(x*1E-2))
        self._view.omYSlider.valueChanged.connect(lambda x: self._view.omYSpinBox.setValue(x*1E-2))
        self._view.il1YSlider.valueChanged.connect(lambda x: self._view.il1YSpinBox.setValue(x*1E-2))
        self._view.il2YSlider.valueChanged.connect(lambda x: self._view.il2YSpinBox.setValue(x*1E-2))
        self._view.il3YSlider.valueChanged.connect(lambda x: self._view.il3YSpinBox.setValue(x*1E-2))
        self._view.plYSlider.valueChanged.connect(lambda x: self._view.plYSpinBox.setValue(x*1E-2))

        self._view.cl1FSlider.valueChanged.connect(lambda x: self._view.cl1FSpinBox.setValue(x*1E-5))
        self._view.cl2FSlider.valueChanged.connect(lambda x: self._view.cl2FSpinBox.setValue(x*1E-5))
        self._view.cl3FSlider.valueChanged.connect(lambda x: self._view.cl3FSpinBox.setValue(x*1E-5))
        self._view.cmFSlider.valueChanged.connect(lambda x: self._view.cmFSpinBox.setValue(x*1E-5))
        self._view.olFSlider.valueChanged.connect(lambda x: self._view.olFSpinBox.setValue(x*1E-5))
        self._view.olPrefieldSlider.valueChanged.connect(lambda x: self._view.olPrefieldSpinBox.setValue(x*1E-5))
        self._view.omFSlider.valueChanged.connect(lambda x: self._view.omFSpinBox.setValue(x*1E-5))
        self._view.il1FSlider.valueChanged.connect(lambda x: self._view.il1FSpinBox.setValue(x*1E-5))
        self._view.il2FSlider.valueChanged.connect(lambda x: self._view.il2FSpinBox.setValue(x*1E-5))
        self._view.il3FSlider.valueChanged.connect(lambda x: self._view.il3FSpinBox.setValue(x*1E-5))
        self._view.plFSlider.valueChanged.connect(lambda x: self._view.plFSpinBox.setValue(x*1E-5))

        self._view.olGapSlider.valueChanged.connect(lambda x: self._view.olGapSpinBox.setValue(x*1E-2))
        self._view.olPrefieldSlider.valueChanged.connect(lambda x: self._view.olPrefieldSpinBox.setValue(x*1E-5))
        
        #Set limits
        self._view.cl1XSlider.setMaximum(self._view.cl1XSpinBox.maximum() * 1E2)
        self._view.cl2XSlider.setMaximum(self._view.cl2XSpinBox.maximum() * 1E2)
        self._view.cl3XSlider.setMaximum(self._view.cl3XSpinBox.maximum() * 1E2)
        self._view.cmXSlider.setMaximum(self._view.cmXSpinBox.maximum() * 1E2)
        self._view.olXSlider.setMaximum(self._view.olXSpinBox.maximum() * 1E2)
        self._view.omXSlider.setMaximum(self._view.omXSpinBox.maximum() * 1E2)
        self._view.il1XSlider.setMaximum(self._view.il1XSpinBox.maximum() * 1E2)
        self._view.il2XSlider.setMaximum(self._view.il2XSpinBox.maximum() * 1E2)
        self._view.il3XSlider.setMaximum(self._view.il3XSpinBox.maximum() * 1E2)
        self._view.plXSlider.setMaximum(self._view.plXSpinBox.maximum() * 1E2)

        self._view.cl1YSlider.setMaximum(self._view.cl1YSpinBox.maximum() * 1E2)
        self._view.cl2YSlider.setMaximum(self._view.cl2YSpinBox.maximum() * 1E2)
        self._view.cl3YSlider.setMaximum(self._view.cl3YSpinBox.maximum() * 1E2)
        self._view.cmYSlider.setMaximum(self._view.cmYSpinBox.maximum() * 1E2)
        self._view.olYSlider.setMaximum(self._view.olYSpinBox.maximum() * 1E2)
        self._view.omYSlider.setMaximum(self._view.omYSpinBox.maximum() * 1E2)
        self._view.il1YSlider.setMaximum(self._view.il1YSpinBox.maximum() * 1E2)
        self._view.il2YSlider.setMaximum(self._view.il2YSpinBox.maximum() * 1E2)
        self._view.il3YSlider.setMaximum(self._view.il3YSpinBox.maximum() * 1E2)
        self._view.plYSlider.setMaximum(self._view.plYSpinBox.maximum() * 1E2)

        self._view.cl1FSlider.setMaximum(self._view.cl1FSpinBox.maximum() * 1E5)
        self._view.cl2FSlider.setMaximum(self._view.cl2FSpinBox.maximum() * 1E5)
        self._view.cl3FSlider.setMaximum(self._view.cl3FSpinBox.maximum() * 1E5)
        self._view.cmFSlider.setMaximum(self._view.cmFSpinBox.maximum() * 1E5)
        self._view.olFSlider.setMaximum(self._view.olFSpinBox.maximum() * 1E5)
        self._view.omFSlider.setMaximum(self._view.omFSpinBox.maximum() * 1E5)
        self._view.il1FSlider.setMaximum(self._view.il1FSpinBox.maximum() * 1E5)
        self._view.il2FSlider.setMaximum(self._view.il2FSpinBox.maximum() * 1E5)
        self._view.il3FSlider.setMaximum(self._view.il3FSpinBox.maximum() * 1E5)
        self._view.plFSlider.setMaximum(self._view.plFSpinBox.maximum() * 1E5)
        self._view.olPrefieldSlider.setMaximum(self._view.olPrefieldSpinBox.maximum() * 1E5)

        self._view.cl1XSlider.setMinimum(self._view.cl1XSpinBox.minimum()*1E2)
        self._view.cl2XSlider.setMinimum(self._view.cl2XSpinBox.minimum()*1E2)
        self._view.cl3XSlider.setMinimum(self._view.cl3XSpinBox.minimum()*1E2)
        self._view.cmXSlider.setMinimum(self._view.cmXSpinBox.minimum()*1E2)
        self._view.olXSlider.setMinimum(self._view.olXSpinBox.minimum()*1E2)
        self._view.omXSlider.setMinimum(self._view.omXSpinBox.minimum()*1E2)
        self._view.il1XSlider.setMinimum(self._view.il1XSpinBox.minimum()*1E2)
        self._view.il2XSlider.setMinimum(self._view.il2XSpinBox.minimum()*1E2)
        self._view.il3XSlider.setMinimum(self._view.il3XSpinBox.minimum()*1E2)
        self._view.plXSlider.setMinimum(self._view.plXSpinBox.minimum()*1E2)

        self._view.cl1YSlider.setMinimum(self._view.cl1YSpinBox.minimum()*1E2)
        self._view.cl2YSlider.setMinimum(self._view.cl2YSpinBox.minimum()*1E2)
        self._view.cl3YSlider.setMinimum(self._view.cl3YSpinBox.minimum()*1E2)
        self._view.cmYSlider.setMinimum(self._view.cmYSpinBox.minimum()*1E2)
        self._view.olYSlider.setMinimum(self._view.olYSpinBox.minimum()*1E2)
        self._view.omYSlider.setMinimum(self._view.omYSpinBox.minimum()*1E2)
        self._view.il1YSlider.setMinimum(self._view.il1YSpinBox.minimum()*1E2)
        self._view.il2YSlider.setMinimum(self._view.il2YSpinBox.minimum()*1E2)
        self._view.il3YSlider.setMinimum(self._view.il3YSpinBox.minimum()*1E2)
        self._view.plYSlider.setMinimum(self._view.plYSpinBox.minimum()*1E2)

        self._view.cl1FSlider.setMinimum(self._view.cl1FSpinBox.minimum()*1E5)
        self._view.cl2FSlider.setMinimum(self._view.cl2FSpinBox.minimum()*1E5)
        self._view.cl3FSlider.setMinimum(self._view.cl3FSpinBox.minimum()*1E5)
        self._view.cmFSlider.setMinimum(self._view.cmFSpinBox.minimum()*1E5)
        self._view.olFSlider.setMinimum(self._view.olFSpinBox.minimum()*1E5)
        self._view.omFSlider.setMinimum(self._view.omFSpinBox.minimum()*1E5)
        self._view.il1FSlider.setMinimum(self._view.il1FSpinBox.minimum()*1E5)
        self._view.il2FSlider.setMinimum(self._view.il2FSpinBox.minimum()*1E5)
        self._view.il3FSlider.setMinimum(self._view.il3FSpinBox.minimum()*1E5)
        self._view.plFSlider.setMinimum(self._view.plFSpinBox.minimum()*1E5)
        self._view.olPrefieldSlider.setMinimum(self._view.olPrefieldSpinBox.minimum()*1E5)
        
        #Set initial values:
        self._view.cl1XSlider.setValue(self._view.cl1XSpinBox.value() * 1E2)
        self._view.cl2XSlider.setValue(self._view.cl2XSpinBox.value() * 1E2)
        self._view.cl3XSlider.setValue(self._view.cl3XSpinBox.value() * 1E2)
        self._view.cmXSlider.setValue(self._view.cmXSpinBox.value() * 1E2)
        self._view.olXSlider.setValue(self._view.olXSpinBox.value() * 1E2)
        self._view.omXSlider.setValue(self._view.omXSpinBox.value() * 1E2)
        self._view.il1XSlider.setValue(self._view.il1XSpinBox.value() * 1E2)
        self._view.il2XSlider.setValue(self._view.il2XSpinBox.value() * 1E2)
        self._view.il3XSlider.setValue(self._view.il3XSpinBox.value() * 1E2)
        self._view.plXSlider.setValue(self._view.plXSpinBox.value() * 1E2)

        self._view.cl1YSlider.setValue(self._view.cl1YSpinBox.value() * 1E2)
        self._view.cl2YSlider.setValue(self._view.cl2YSpinBox.value() * 1E2)
        self._view.cl3YSlider.setValue(self._view.cl3YSpinBox.value() * 1E2)
        self._view.cmYSlider.setValue(self._view.cmYSpinBox.value() * 1E2)
        self._view.olYSlider.setValue(self._view.olYSpinBox.value() * 1E2)
        self._view.omYSlider.setValue(self._view.omYSpinBox.value() * 1E2)
        self._view.il1YSlider.setValue(self._view.il1YSpinBox.value() * 1E2)
        self._view.il2YSlider.setValue(self._view.il2YSpinBox.value() * 1E2)
        self._view.il3YSlider.setValue(self._view.il3YSpinBox.value() * 1E2)
        self._view.plYSlider.setValue(self._view.plYSpinBox.value() * 1E2)

        self._view.cl1FSlider.setValue(self._view.cl1FSpinBox.value() * 1E5)
        self._view.cl2FSlider.setValue(self._view.cl2FSpinBox.value() * 1E5)
        self._view.cl3FSlider.setValue(self._view.cl3FSpinBox.value() * 1E5)
        self._view.cmFSlider.setValue(self._view.cmFSpinBox.value() * 1E5)
        self._view.olFSlider.setValue(self._view.olFSpinBox.value() * 1E5)
        self._view.omFSlider.setValue(self._view.omFSpinBox.value() * 1E5)
        self._view.il1FSlider.setValue(self._view.il1FSpinBox.value() * 1E5)
        self._view.il2FSlider.setValue(self._view.il2FSpinBox.value() * 1E5)
        self._view.il3FSlider.setValue(self._view.il3FSpinBox.value() * 1E5)
        self._view.plFSlider.setValue(self._view.plFSpinBox.value() * 1E5)
        self._view.olPrefieldSlider.setValue(self._view.olPrefieldSpinBox.value() * 1E5)

    def setup_lens_control(self):
        self._view.cl1CheckBox.clicked.connect(self.show)
        self._view.cl2CheckBox.clicked.connect(self.show)
        self._view.cl3CheckBox.clicked.connect(self.show)
        self._view.cmCheckBox.clicked.connect(self.show)
        self._view.olCheckBox.clicked.connect(self.show)
        self._view.omCheckBox.clicked.connect(self.show)
        self._view.il1CheckBox.clicked.connect(self.show)
        self._view.il2CheckBox.clicked.connect(self.show)
        self._view.il3CheckBox.clicked.connect(self.show)
        self._view.plCheckBox.clicked.connect(self.show)

        self._view.printCL1.clicked.connect(lambda x: print(self._model.CL1))
        self._view.printCL2.clicked.connect(lambda x: print(self._model.CL2))
        self._view.printCL3.clicked.connect(lambda x: print(self._model.CL3))
        self._view.printCM.clicked.connect(lambda x: print(self._model.CM))
        self._view.printOM.clicked.connect(lambda x: print(self._model.OL))
        self._view.printOL.clicked.connect(lambda x: print(self._model.OL))
        self._view.printIL1.clicked.connect(lambda x: print(self._model.IL1))
        self._view.printIL2.clicked.connect(lambda x: print(self._model.IL2))
        self._view.printIL3.clicked.connect(lambda x: print(self._model.IL3))
        self._view.printPL.clicked.connect(lambda x: print(self._model.PL))

        self._view.cl1XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('CL1', x=x))
        self._view.cl2XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('CL2', x=x))
        self._view.cl3XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('CL3', x=x))
        self._view.cmXSpinBox.valueChanged.connect(lambda x: self._model.change_lens('CM', x=x))
        self._view.olXSpinBox.valueChanged.connect(lambda x: self._model.change_lens('OL', x=x))
        self._view.omXSpinBox.valueChanged.connect(lambda x: self._model.change_lens('OM', x=x))
        self._view.il1XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('IL1', x=x))
        self._view.il2XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('IL2', x=x))
        self._view.il3XSpinBox.valueChanged.connect(lambda x: self._model.change_lens('IL3', x=x))
        self._view.plXSpinBox.valueChanged.connect(lambda x: self._model.change_lens('PL', x=x))

        self._view.cl1YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('CL1', y=y))
        self._view.cl2YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('CL2', y=y))
        self._view.cl3YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('CL3', y=y))
        self._view.cmYSpinBox.valueChanged.connect(lambda y: self._model.change_lens('CM', y=y))
        self._view.olYSpinBox.valueChanged.connect(lambda y: self._model.change_lens('OL', y=y))
        self._view.omYSpinBox.valueChanged.connect(lambda y: self._model.change_lens('OM', y=y))
        self._view.il1YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('IL1', y=y))
        self._view.il2YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('IL2', y=y))
        self._view.il3YSpinBox.valueChanged.connect(lambda y: self._model.change_lens('IL3', y=y))
        self._view.plYSpinBox.valueChanged.connect(lambda y: self._model.change_lens('PL', y=y))

        self._view.cl1FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('CL1', f=f))
        self._view.cl2FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('CL2', f=f))
        self._view.cl3FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('CL3', f=f))
        self._view.cmFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('CM', f=f))
        self._view.olFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('OL', postfield=f))
        self._view.olPrefieldSpinBox.valueChanged.connect(lambda f: self._model.change_lens('OL', prefield=f))
        self._view.omFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('OM', f=f))
        self._view.il1FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL1', f=f))
        self._view.il2FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL2', f=f))
        self._view.il3FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL3', f=f))
        self._view.plFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('PL', f=f))

        self._view.olGapSpinBox.valueChanged.connect(lambda gap: self._model.change_lens('OL', gap=gap))
        self._view.olCoupledCheckBox.clicked.connect(lambda: self._model.change_lens('OL', couple=self._view.olCoupledCheckBox.isChecked()))
        self._view.olCoupledCheckBox.clicked.connect(lambda: self._model.change_lens('OL', postfield=self._view.olFSpinBox.value(), prefield=self._view.olPrefieldSpinBox.value()))
        self._view.olCoupledCheckBox.clicked.connect(lambda: self._view.olPrefieldSpinBox.setDisabled(self._view.olCoupledCheckBox.isChecked()))
        #self._view.olFSpinBox.valueChanged.connect(lambda f: )

    def setup_style_control(self):
        self._view.lensStyleComboBox.currentIndexChanged.connect(self.show)
        self._view.lensColorComboBox.currentIndexChanged.connect(self.show)
        self._view.lensLinewidthSpinBox.valueChanged.connect(self.show)
        self._view.lensAlphaSpinBox.valueChanged.connect(self.show)
        self._view.lensLabelCheckBox.clicked.connect(self.show)

        self._view.focalPlaneStyleComboBox.currentIndexChanged.connect(self.show)
        self._view.focalPlaneColorComboBox.currentIndexChanged.connect(self.show)
        self._view.focalPlaneLinewidthSpinBox.valueChanged.connect(self.show)
        self._view.focalPlaneAlphaSpinBox.valueChanged.connect(self.show)
        self._view.focalPlaneLabelCheckBox.clicked.connect(self.show)

        self._view.imagePlaneStyleComboBox.currentIndexChanged.connect(self.show)
        self._view.imagePlaneColorComboBox.currentIndexChanged.connect(self.show)
        self._view.imagePlaneLinewidthSpinBox.valueChanged.connect(self.show)
        self._view.imagePlaneAlphaSpinBox.valueChanged.connect(self.show)
        self._view.imagePlaneLabelCheckBox.clicked.connect(self.show)

        self._view.rayColorComboBox.currentIndexChanged.connect(self.show)
        self._view.rayLinewidthSpinBox.valueChanged.connect(self.show)
        self._view.rayAlphaSpinBox.valueChanged.connect(self.show)
        self._view.rayLabelCheckBox.clicked.connect(self.show)

        self._view.xminSpinBox.valueChanged.connect(self.show)
        self._view.xmaxSpinBox.valueChanged.connect(self.show)
        self._view.yminSpinBox.valueChanged.connect(self.show)
        self._view.ymaxSpinBox.valueChanged.connect(self.show)

        self._view.manualRadioButton.toggled.connect(
            lambda: self._view.xminSpinBox.setEnabled(self._view.manualRadioButton.isChecked()))
        self._view.manualRadioButton.toggled.connect(
            lambda: self._view.xmaxSpinBox.setEnabled(self._view.manualRadioButton.isChecked()))
        self._view.manualRadioButton.toggled.connect(
            lambda: self._view.yminSpinBox.setEnabled(self._view.manualRadioButton.isChecked()))
        self._view.manualRadioButton.toggled.connect(
            lambda: self._view.ymaxSpinBox.setEnabled(self._view.manualRadioButton.isChecked()))

    def set_y_spinbox_limits(self):
        self._view.cl1YSpinBox.setMaximum(self._model.source.y-1e-2)
        self._view.cl2YSpinBox.setMaximum(self._model.CL1.y - 1e-2)
        self._view.cl3YSpinBox.setMaximum(self._model.CL2.y - 1e-2)
        self._view.cmYSpinBox.setMaximum(self._model.CL3.y - 1e-2)
        self._view.olYSpinBox.setMaximum(self._model.CM.y - 1e-2)
        self._view.omYSpinBox.setMaximum(self._model.OL.y - 1e-2)
        self._view.il1YSpinBox.setMaximum(self._model.OM.y - 1e-2)
        self._view.il2YSpinBox.setMaximum(self._model.IL1.y - 1e-2)
        self._view.il3YSpinBox.setMaximum(self._model.IL2.y - 1e-2)
        self._view.plYSpinBox.setMaximum(self._model.IL3.y - 1e-2)
        self._view.screenSpinBox.setMaximum(self._view.plYSpinBox.value() -1e-2)

        self._view.sourceYSpinBox.setMinimum(self._model.CL1.y + 1e-2)
        self._view.cl1YSpinBox.setMinimum(self._model.CL2.y + 1e-2)
        self._view.cl2YSpinBox.setMinimum(self._model.CL3.y + 1e-2)
        self._view.cl3YSpinBox.setMinimum(self._model.CM.y + 1e-2)
        self._view.cmYSpinBox.setMinimum(self._model.OL.y + 1e-2)
        self._view.olYSpinBox.setMinimum(self._model.OM.y + 1e-2)
        self._view.omYSpinBox.setMinimum(self._model.IL1.y + 1e-2)
        self._view.il1YSpinBox.setMinimum(self._model.IL2.y + 1e-2)
        self._view.il2YSpinBox.setMinimum(self._model.IL3.y + 1e-2)
        self._view.il3YSpinBox.setMinimum(self._model.PL.y + 1e-2)
        self._view.plYSpinBox.setMinimum(self._view.screenSpinBox.value())
        
        self._view.sourceYSpinBox.valueChanged.connect(lambda y: self._view.cl1YSpinBox.setMaximum(y-1e-2))
        self._view.cl1YSpinBox.valueChanged.connect(lambda y: self._view.cl2YSpinBox.setMaximum(y-1e-2))
        self._view.cl2YSpinBox.valueChanged.connect(lambda y: self._view.cl3YSpinBox.setMaximum(y-1e-2))
        self._view.cl3YSpinBox.valueChanged.connect(lambda y: self._view.cmYSpinBox.setMaximum(y-1e-2))
        self._view.cmYSpinBox.valueChanged.connect(lambda y: self._view.olYSpinBox.setMaximum(y-1e-2))
        #self._view.olYSpinBox.valueChanged.connect(lambda y: self._view.omYSpinBox.setMaximum(y-1e-2))
        self._view.omYSpinBox.valueChanged.connect(lambda y: self._view.il1YSpinBox.setMaximum(y-1e-2))
        self._view.il1YSpinBox.valueChanged.connect(lambda y: self._view.il2YSpinBox.setMaximum(y-1e-2))
        self._view.il2YSpinBox.valueChanged.connect(lambda y: self._view.il3YSpinBox.setMaximum(y-1e-2))
        self._view.il3YSpinBox.valueChanged.connect(lambda y: self._view.plYSpinBox.setMaximum(y-1e-2))
        self._view.plYSpinBox.valueChanged.connect(lambda y: self._view.sceenSpinBox.setMaximum(y-1e-2))

        self._view.screenSpinBox.valueChanged.connect(lambda y: self._view.plYSpinBox.setMinimum(y + 1e-2))
        self._view.plYSpinBox.valueChanged.connect(lambda y: self._view.il1YSpinBox.setMinimum(y+1e-2))
        self._view.il1YSpinBox.valueChanged.connect(lambda y: self._view.il2YSpinBox.setMinimum(y+1e-2))
        self._view.il2YSpinBox.valueChanged.connect(lambda y: self._view.il3YSpinBox.setMinimum(y+1e-2))
        self._view.il3YSpinBox.valueChanged.connect(lambda y: self._view.omYSpinBox.setMinimum(y+1e-2))
        #self._view.olYSpinBox.valueChanged.connect(lambda y: self._view.olYSpinBox.setMinimum(y+1e-2))
        self._view.omYSpinBox.valueChanged.connect(lambda y: self._view.cmYSpinBox.setMinimum(y+1e-2))
        self._view.cmYSpinBox.valueChanged.connect(lambda y: self._view.cl3YSpinBox.setMinimum(y+1e-2))
        self._view.cl3YSpinBox.valueChanged.connect(lambda y: self._view.cl2YSpinBox.setMinimum(y+1e-2))
        self._view.cl2YSpinBox.valueChanged.connect(lambda y: self._view.cl1YSpinBox.setMinimum(y+1e-2))
        self._view.cl1YSpinBox.valueChanged.connect(lambda y: self._view.sourceYSpinBox.setMinimum(y+1e-2))

    def get_active_lenses(self, names=False):
        active_lenses = []
        if self._view.cl1CheckBox.isChecked():
            active_lenses.append(self._model.CL1)
        if self._view.cl2CheckBox.isChecked():
            active_lenses.append(self._model.CL2)
        if self._view.cl3CheckBox.isChecked():
            active_lenses.append(self._model.CL3)
        if self._view.cmCheckBox.isChecked():
            active_lenses.append(self._model.CM)
        if self._view.olCheckBox.isChecked():
            active_lenses.append(self._model.OL)
        if self._view.omCheckBox.isChecked():
            active_lenses.append(self._model.OM)
        if self._view.il1CheckBox.isChecked():
            active_lenses.append(self._model.IL1)
        if self._view.il2CheckBox.isChecked():
            active_lenses.append(self._model.IL2)
        if self._view.il3CheckBox.isChecked():
            active_lenses.append(self._model.IL3)
        if self._view.plCheckBox.isChecked():
            active_lenses.append(self._model.PL)
        active_lenses.sort(key=lambda x: x.y, reverse=True)
        if names:
            return [lens.name for lens in active_lenses]
        return active_lenses

    def make_raytrace(self, initial_ray=None):
        if initial_ray is None:
            initial_ray = self._model.source.emit_ray(self._view.sourceAngleSpinBox.value(), 1)
        rays = [initial_ray]
        lenses = self._model.get_lenses()#self.get_active_lenses()
        active_lenses = self.get_active_lenses()
        for lens in lenses:
            if lens.name in self.get_active_lenses(names=True):
                try:
                    transmitted_ray = lens(rays[-1])
                except ZeroDivisionError:
                    break
                except RayTransmitError:
                    pass
                else:
                    if isinstance(transmitted_ray, list):
                        [rays.append(ray) for ray in transmitted_ray]
                    else:
                        rays.append(transmitted_ray)
        return rays

    def resize_lenses(self, left, right):
        """"
        Resizes the lenses to span at least to left or right, whichever is farthest from the lens centre
        """
        for lens in self.get_active_lenses():
            left_offset = left - lens.x
            right_offset = right - lens.x
            size = 2*max([abs(left_offset), abs(right_offset)])
            lens.set_size(size)

    def show_source(self):
        self._model.source.show(self._view.plotWidget.canvas.ax)

    def show_lenses(self):
        for lens in self.get_active_lenses():
            lens.show(self._view.plotWidget.canvas.ax, lensprops={
                'ffp': {'linestyle': self._view.focalPlaneStyleComboBox.currentText(),
                        'linewidth': self._view.focalPlaneLinewidthSpinBox.value(),
                        'color': self._view.focalPlaneColorComboBox.currentText(),
                        'alpha': self._view.focalPlaneAlphaSpinBox.value()},
                'bfp': {'linestyle': self._view.focalPlaneStyleComboBox.currentText(),
                        'linewidth': self._view.focalPlaneLinewidthSpinBox.value(),
                        'color': self._view.focalPlaneColorComboBox.currentText(),
                        'alpha': self._view.focalPlaneAlphaSpinBox.value()},
                'lens': {'linestyle': self._view.lensStyleComboBox.currentText(),
                         'linewidth': self._view.lensLinewidthSpinBox.value(),
                         'color': self._view.lensColorComboBox.currentText(),
                         'alpha': self._view.lensAlphaSpinBox.value()}},
                      label_lens = self._view.lensLabelCheckBox.isChecked(),
                      label_focal_planes = self._view.focalPlaneLabelCheckBox.isChecked())

    def show_raytrace(self, initial_ray=None):
        raytraces = self.make_raytrace(initial_ray)
        for ray in raytraces:
            ray.show(self._view.plotWidget.canvas.ax, show_label=self._view.rayLabelCheckBox.isChecked(), arrowprops={'color': self._view.rayColorComboBox.currentText(), 'alpha': self._view.rayAlphaSpinBox.value(),'lw': self._view.rayLinewidthSpinBox.value()})

        return raytraces

    def show(self):
        xlims = self._view.plotWidget.canvas.ax.get_xlim()
        ylims = self._view.plotWidget.canvas.ax.get_ylim()
        self._view.plotWidget.canvas.ax.cla()
        self.show_source()
        raytraces = self.show_raytrace()
        if self._view.symmetricSourceCheckBox.isChecked():
            symmetric_rays = self.show_raytrace(initial_ray = self._model.source.emit_ray(-self._view.sourceAngleSpinBox.value(), -1))
            raytraces = raytraces + symmetric_rays

        self.resize_lenses(min([ray.stop.x for ray in raytraces]), max([ray.stop.x for ray in raytraces]))
        self.show_lenses()
        if self._view.autoscaleRadioButton.isChecked():
            self._view.plotWidget.canvas.ax.set_xlim(min([lens.x - lens.size / 2 for lens in self.get_active_lenses()]), max([lens.x + lens.size / 2 for lens in self.get_active_lenses()]))
        elif self._view.manualRadioButton.isChecked():
            self._view.plotWidget.canvas.ax.set_xlim(self._view.xminSpinBox.value(), self._view.xmaxSpinBox.value())
            self._view.plotWidget.canvas.ax.set_ylim(self._view.yminSpinBox.value(), self._view.ymaxSpinBox.value())
        elif self._view.lockRadioButton.isChecked():
            self._view.plotWidget.canvas.ax.set_xlim(xlims[0], xlims[1])
            self._view.plotWidget.canvas.ax.set_ylim(ylims[0], ylims[1])
        self._view.xmaxSpinBox.setValue(self._view.plotWidget.canvas.ax.get_xlim()[1])
        self._view.xminSpinBox.setValue(self._view.plotWidget.canvas.ax.get_xlim()[0])
        self._view.ymaxSpinBox.setValue(self._view.plotWidget.canvas.ax.get_ylim()[1])
        self._view.yminSpinBox.setValue(self._view.plotWidget.canvas.ax.get_ylim()[0])

        self._view.plotWidget.canvas.draw()

    def export(self):
        name = QtWidgets.QFileDialog.getSaveFileName(None, 'Save File')[0]
        print(name)
        if name is not None:
            self._view.plotWidget.canvas.fig.savefig(name, dpi=self._view.dpiSpinBox.value())

def run_gui():
    main()

def main():
    myqui = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    model = vTEMModel()
    controller = vTEMController(view=main_window, model=model)
    main_window.show()

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
