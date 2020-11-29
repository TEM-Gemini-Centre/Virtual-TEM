from vTEM.Rays import Ray, RayNode


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

    def __call__(self, *args, **kwargs):
        pass



    def show(self, ax, *args, **kwargs):
        ax.plot([self.x - self.size / 2, self.x + self.size / 2], [self.y, self.y], *args, **kwargs)
        ax.plot([self.x - self.size / 2, self.x + self.size / 2],
                [self.y + self.focal_length, self.y + self.focal_length], *args, **kwargs)
        ax.plot([self.x - self.size / 2, self.x + self.size / 2],
                [self.y - self.focal_length, self.y - self.focal_length], *args, **kwargs)
        ax.annotate('{self.name}'.format(self=self), xy=(self.x + self.size / 2, self.y), ha='left', va='center')
        ax.annotate('{self.name} FFP'.format(self=self), xy=(self.x + self.size / 2, self.y + self.focal_length),
                    ha='left', va='center')
        ax.annotate('{self.name} BFP'.format(self=self), xy=(self.x + self.size / 2, self.y - self.focal_length),
                    ha='left', va='center')
