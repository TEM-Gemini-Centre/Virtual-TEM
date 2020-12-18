from vTEM.Rays import Ray, RayNode
from math import atan

class Error(Exception):
    pass

class RayTransmitError(Error):
    pass

class Lens(object):
    """
    A lens object for creating images of objects and bending rays
    """

    def __init__(self, y, focal_length, x=0, size=1, name=''):
        """
        Create a lens object.
        :param y: The position of the lens along the optical axis
        :param focal_length: The strength of the lens
        :param x: The position of the center of the lens perpendicular to the optical axis. Default is 0
        :param size: The size of the lens. Default is 1.
        :param name: The name of the lens. Default is ""
        :type y: float
        :type focal_length: float
        :type x: float
        :type size: float
        :type name: str
        """

        self.y = float(y)
        self.focal_length = abs(float(focal_length))
        self.x = float(x)
        self.size = abs(float(size))
        self.name = str(name)

    def __repr__(self):
        return '{self.__class__.__name__}({self.y!r}, {self.focal_length!r}, x={self.x!r}, size={self.size!r}, ' \
               'name={self.name!r})'.format(self=self)

    def __format__(self, format_spec):
        return '{self.y:{f}} ({self.focal_length:{f}})'.format(self=self, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self:.2f} | {self.x:.2f}/{self.size:.2f}'.format(self=self)

    def __lt__(self, other):
        return self.y < other

    def __le__(self, other):
        return self.y <= other

    def __gt__(self, other):
        return self.y > other

    def __ge__(self, other):
        return self.y >= other

    def __eq__(self, other):
        return self.y == other

    def __iadd__(self, other):
        self.y = self.y + other
        return self

    def __isub__(self, other):
        self.y = self.y - other
        return self

    def __add__(self, other):
        return self.y + other

    def __radd__(self, other):
        return other + self.y

    def __sub__(self, other):
        return self.y - other

    def __rsub__(self, other):
        return other - self.y

    def __mul__(self, other):
        return self.y * other

    def __rmul__(self, other):
        return other * self.y

    def __truediv__(self, other):
        return self.y / other

    def __rtruediv__(self, other):
        return other / self.y

    def __pow__(self, power, modulo=None):
        return self.y.__pow__(power, modulo)

    def __call__(self, ray, *args, **kwargs):
        if not isinstance(ray, Ray):
            raise TypeError('Ray {ray!r} must be type Ray, not {t}'.format(ray=ray, t=type(ray)))

        if not self < ray.start:
            raise RayTransmitError('Lens {self} must be positioned after start of ray {ray}'.format(self=self, ray=ray))
        ray.extend(self.y)
        transmitted_ray = Ray(ray.stop, RayNode(self.x, self.y - self.focal_length))
        transmitted_ray.set_angle(ray.angle(deg=False) - atan((transmitted_ray.start.x - self.x) / self.focal_length),
                                  deg=False)
        if transmitted_ray.start < transmitted_ray.stop:
            transmitted_ray = Ray(RayNode(transmitted_ray.stop), RayNode(transmitted_ray.start),
                                  name=transmitted_ray.name)
        transmitted_ray.extend(self.y - self.focal_length)
        transmitted_ray.cut(self.y)
        return transmitted_ray

    def set_x(self, x):
        self.x = float(x)

    def set_f(self, f):
        self.focal_length = abs(float(f))

    def set_y(self, y):
        self.y = float(y)

    def set_size(self, size):
        self.size = abs(float(size))

    def show(self, ax, *args, lensprops=None, label_lens = True, label_focal_planes=True):  # , **kwargs):
        plotstyle = {'ffp': {'linestyle': '--', 'color': 'k', 'alpha': 0.2},
                     'bfp': {'linestyle': '--', 'color': 'k', 'alpha': 0.2},
                     'lens': {'linestyle': '-', 'color': 'k', 'alpha': 0.5},
                     'axis': {'linestyle': '-', 'color': 'k', 'alpha': 0.2}}
        if lensprops is None:
            lensprops = {}
        plotstyle.update(lensprops)
        ax.plot([self.x - self.size / 2, self.x + self.size / 2], [self.y, self.y], *args, **plotstyle.get('lens'))
        ax.plot([self.x - self.size / 2, self.x + self.size / 2],
                [self.y + self.focal_length, self.y + self.focal_length], *args, **plotstyle.get('ffp'))
        ax.plot([self.x - self.size / 2, self.x + self.size / 2],
                [self.y - self.focal_length, self.y - self.focal_length], *args, **plotstyle.get('bfp'))
        ax.plot([self.x, self.x], [self.y + self.focal_length, self.y + self.focal_length], *args, **plotstyle.get('axis'))

        if label_lens:
            ax.annotate('{self.name}'.format(self=self), xy=(self.x + self.size / 2, self.y), ha='left', va='center')
        if label_focal_planes:
            ax.annotate('{self.name} FFP'.format(self=self), xy=(self.x + self.size / 2, self.y + self.focal_length),
                        ha='left', va='center')
            ax.annotate('{self.name} BFP'.format(self=self), xy=(self.x + self.size / 2, self.y - self.focal_length),
                        ha='left', va='center')

class ObjectiveLens(object):
    def __init__(self, y, focal_lengths, gap, x=0.0, size=1, name='OL', coupled=False):
        """
        Create an objective lens with a prefield and a postfield acting as coupled or decoupled lenses.
        :param y: The position of the middle of the objective lens along the optical axis.
        :param focal_lengths: The focal lengths of the pre- and postfields.
        :param gap: The gap between the prefield and the postfield.
        :param x: The position of the centre of the lens perpendicular to the optical axis. Default is 0.0
        :param size: The size of the lens. Default is 1
        :param name: The name of the lens. Default is "OL".
        :param coupled: Whether to couple the prefield and postfield.
        :type y: float
        :type focal_length: tuple
        :type gap: float
        :type x: float
        :type size: float
        :type name: str
        :type coupled: bool
        """
        self.gap = abs(float(gap))
        self.y = float(y)
        self.x = float(x)
        self.size = abs(float(size))
        self.focal_lengths = (abs(float(focal_lengths[0])), abs(float(focal_lengths[1])))
        self.name = str(name)
        self.coupled = bool(coupled)

    def __repr__(self):
        return '{self.__class__.__name__}({self.y!r}, {self.focal_lengths!r}, {self.gap!r}, x={self.x!r}, size={self.size!r}, ' \
               'name={self.name!r})'.format(self=self)

    def __format__(self, format_spec):
        return '{self.y:{f}} ({pre:{f}}, {post:{f}})'.format(self=self, pre=self.get_prefield().focal_length, post = self.get_postfield().focal_length, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} {self.name}: {self:.2f} | {self.x:.2f}/{self.size:.2f}/{self.gap:.2f}'.format(self=self)

    def __lt__(self, other):
        return self.y +self.gap/2 < other

    def __le__(self, other):
        return self.y + self.gap/2<= other

    def __gt__(self, other):
        return self.y - self.gap/2 > other

    def __ge__(self, other):
        return self.y -self.gap/2>= other

    def __eq__(self, other):
        return self.y == other

    def __iadd__(self, other):
        self.y = self.y + other
        return self

    def __isub__(self, other):
        self.y = self.y - other
        return self

    def __add__(self, other):
        return self.y + other

    def __radd__(self, other):
        return other + self.y

    def __sub__(self, other):
        return self.y - other

    def __rsub__(self, other):
        return other - self.y

    def __mul__(self, other):
        return self.y * other

    def __rmul__(self, other):
        return other * self.y

    def __truediv__(self, other):
        return self.y / other

    def __rtruediv__(self, other):
        return other / self.y

    def __pow__(self, power, modulo=None):
        return self.y.__pow__(power, modulo)

    def __call__(self, ray, *args, **kwargs):
        prefield = self.get_prefield()
        postfield = self.get_postfield()
        prefield_ray = prefield(ray)
        postfield_ray = postfield(prefield_ray)
        return [prefield_ray, postfield_ray]

    def couple(self, couple=True):
        self.coupled = bool(couple)

    def set_x(self, x):
        self.x = float(x)

    def set_f(self, f):
        self.set_postfield(f)
        self.set_prefield(f)

    def set_prefield(self, f):
        if self.coupled:
            self.focal_lengths = (abs(float(f)), abs(float(f)))
        else:
            self.focal_lengths = (abs(float(f)), self.focal_lengths[1])

    def set_postfield(self, f):
        self.focal_lengths = (self.focal_lengths[0], abs(float(f)))
        if self.coupled:
            self.focal_lengths = (abs(float(f)), abs(float(f)))
        else:
            self.focal_lengths = (self.focal_lengths[0], abs(float(f)))

    def set_y(self, y):
        self.y = float(y)

    def set_gap(self, gap):
        self.gap = abs(float(gap))

    def set_size(self, size):
        self.size = abs(float(size))

    def get_prefield(self):
        return Lens(self.y + self.gap / 2, focal_length=self.focal_lengths[0], x=self.x, size=self.size,
                    name='{name} prefield'.format(name=self.name))

    def get_postfield(self):
        return Lens(self.y - self.gap / 2, focal_length=self.focal_lengths[1], x=self.x, size=self.size,
                    name='{name} postfield'.format(name=self.name))

    def show(self, ax, *args, **kwargs):
        self.get_prefield().show(ax, *args, **kwargs)
        self.get_postfield().show(ax, *args, **kwargs)


class Source(object):
    """
    A source capable of emitting rays
    """

    def __init__(self, x, y, size, name=''):
        """
        Create a new source
        :param x: x-position of source (position of source centre perpendicular to the optical axis)
        :param y: y-position of source (position of source along the optical axis)
        :param size: Size of the source
        :param name: Name of the source. Default is ""
        :type x: float
        :type y: float
        :type size: float
        :type name: str
        """
        self.x = float(x)
        self.y = float(y)
        self.size = abs(float(size))
        self.name = str(name)

    def __str__(self):
        return '{self.__class__.__name__} {self.name} with size {self.size:.2f} at ({self.x:.2f}, {self.y:.2f})'.format(
            self=self)

    def set_x(self, x):
        self.x = float(x)

    def set_y(self, y):
        self.y = float(y)

    def set_size(self, size):
        self.size = abs(float(size))

    def show(self, ax, *args, **kwargs):
        """
        Show the source
        :param ax: matplotlib.pyplot.Axes object
        :param args: optional positional arguments passed to ax.plot()
        :param kwargs: Optional keyword arguments passed to ax.plot()
        :return:
        """
        ax.plot((self.x - self.size / 2, self.x + self.size / 2), (self.y, self.y))

    def emit_ray(self, angle, position=0, length=1):
        """
        Return a ray emitted from the source
        :param length: The length of the emitted ray along the optical axis.
        :param angle: The angle of the emitted ray in degrees
        :param position: The initial point of the ray in a fraction of the size of the source size
        :return: The emitted ray
        :rtype: Ray
        """
        start = RayNode(self.x + (position * self.size / 2), self.y)
        stop = RayNode(self.x, self.y - abs(length))
        ray = Ray(start, stop, angle=angle, name='Emitted from {self.name}'.format(self=self))
        # ray.extend(abs(length), relative=True)
        return ray
