from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from vTEM import Lens, RayNode, Ray, Source

import sys


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Load the UI Page
        uic.loadUi('./source/qtcreator/mainwindow.ui', self)


class vTEMModel(QObject):
    updated = pyqtSignal([], [bool])

    def __init__(self, *args, **kwargs):

        super(vTEMModel, self).__init__(*args, **kwargs)
        self.source = Source(0, 220, 10, name='Source')
        self.CL1 = Lens(200, 2, name='CL1')
        self.CL2 = Lens(180, 2, name='CL2')
        self.CL3 = Lens(160, 2, name='CL3')
        self.CM = Lens(140, 2, name='CM')
        self.OL = Lens(120, 2, name='OL')
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

    def change_lens(self, name, x=None, y=None, f=None):
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
        self.set_y_spinbox_limits()
        self.setup_source_control()
        self.setup_lens_control()
        self.setup_screen_control()
        self._view.plotPushButton.clicked.connect(self.show)
        self._model.updated.connect(self.show)

        for lens in self._model:
            print(lens)

    def setup_source_control(self):
        self._view.sourceXSpinBox.valueChanged.connect(lambda x: self._model.change_source(x=x))
        self._view.sourceYSpinBox.valueChanged.connect(lambda y: self._model.change_source(y=y))
        self._view.sourceSizeSpinBox.valueChanged.connect(lambda size: self._model.change_source(size=size))
        self._view.sourceAngleSpinBox.valueChanged.connect(self.show)

    def setup_screen_control(self):
        self._view.screenSpinBox.valueChanged.connect(self.show)

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
        self._view.olFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('OL', f=f))
        self._view.omFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('OM', f=f))
        self._view.il1FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL1', f=f))
        self._view.il2FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL2', f=f))
        self._view.il3FSpinBox.valueChanged.connect(lambda f: self._model.change_lens('IL3', f=f))
        self._view.plFSpinBox.valueChanged.connect(lambda f: self._model.change_lens('PL', f=f))

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
        self._view.olYSpinBox.valueChanged.connect(lambda y: self._view.omYSpinBox.setMaximum(y-1e-2))
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
        self._view.olYSpinBox.valueChanged.connect(lambda y: self._view.olYSpinBox.setMinimum(y+1e-2))
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

    def make_raytrace(self):
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
                else:
                    rays.append(transmitted_ray)
        return rays

    def show_source(self):
        self._model.source.show(self._view.plotWidget.canvas.ax)

    def show_lenses(self):
        for lens in self.get_active_lenses():
            lens.show(self._view.plotWidget.canvas.ax, lensprops={
                'ffp': {'linestyle': self._view.focalPlaneStyleComboBox.currentText(),
                        'color': self._view.focalPlaneColorComboBox.currentText(),
                        'alpha': self._view.focalPlaneAlphaSpinBox.value()},
                'bfp': {'linestyle': self._view.focalPlaneStyleComboBox.currentText(),
                        'color': self._view.focalPlaneColorComboBox.currentText(),
                        'alpha': self._view.focalPlaneAlphaSpinBox.value()},
                'lens': {'linestyle': self._view.lensStyleComboBox.currentText(),
                         'color': self._view.lensColorComboBox.currentText(),
                         'alpha': self._view.lensAlphaSpinBox.value()}})

    def show_raytrace(self):
        for ray in self.make_raytrace():
            ray.show(self._view.plotWidget.canvas.ax, arrowprops={'color': self._view.rayColorComboBox.currentText(),
                                                                  'alpha': self._view.rayAlphaSpinBox.value()})

    def show(self):
        self._view.plotWidget.canvas.ax.cla()
        self.show_source()
        self.show_lenses()
        self.show_raytrace()
        self._view.plotWidget.canvas.draw()


def main():
    myqui = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()
    model = vTEMModel()
    controller = vTEMController(view=main_window, model=model)
    main_window.show()

    sys.exit(myqui.exec_())


if __name__ == '__main__':
    main()
