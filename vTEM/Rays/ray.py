import matplotlib.pyplot as plt
import numpy as np
from math import nan, pi, sqrt, inf, sin, cos, tan, asin, acos, atan


class RayNode(object):
    """
    A node object for controlling the start and stop end points of a ray
    """

    def __init__(self, *args, name=''):
        """
        Create a new node.

        If another RayNode is provided, creates a copy of that node. If an iterable is provided, uses its content as x and y coordinates. If two floats are provided, uses these as x and y coordinates respectively
        :param args: Optional positional arguments.
        :param name: Name of node. Optional. Default is empty string
        :type name: str
        """
        if len(args) == 0:
            x = nan
            y = nan
        elif len(args) == 1:
            pos = args[0]
            if isinstance(pos, RayNode):
                x = pos.x
                y = pos.y
                name = RayNode.name
            elif isinstance(pos, (tuple, list, np.ndarray)):
                if not len(pos) == 2:
                    raise TypeError(
                        'The length of the iterable must be 2, not {pos!r} of length {l}'.format(pos=pos, l=len(pos)))
                x = pos[0]
                y = pos[1]
            else:
                raise TypeError('Could not extract x and y from {pos!r}!'.format(pos=pos))
        elif len(args) == 2:
            x = args[0]
            y = args[1]
        else:
            raise TypeError('Could not extract x and y coordinates with {args!r} as arguments'.format(args=args))

        if not isinstance(x, (int, float)):
            raise TypeError('Parameter "x" must be type float, recieved {x!r} of type {t}'.format(x=x, t=type(x)))
        if not isinstance(y, (int, float)):
            raise TypeError('Parameter "y" must be type float, recieved {y!r} of type {t}'.format(y=y, t=type(y)))
        if not isinstance(name, str):
            raise TypeError(
                'Parameter "name" must be type str, recieved {name!r} of type {t}'.format(name=name, t=type(name)))

        self.x = x
        self.y = y
        self.name = name

    @property
    def position(self):
        return np.array([self.x, self.y])

    @position.setter
    def position(self, pos):
        if not isinstance(pos, (tuple, list, np.ndarray)):
            raise TypeError(
                'Can only set position using a tuple, list, or np.ndarray, not by using {pos!r} of type {t}'.format(
                    pos=pos, t=type(pos)))
        if not len(pos) == 2:
            raise TypeError(
                'Can only set position using an iterable of length 2, not {pos!r} of length {l}'.format(pos=pos,
                                                                                                        l=len(pos)))
        if not all([isinstance(p, float) for p in pos]):
            raise TypeError('Values in position must be type float, not {pos!r} with types {types!r}'.format(pos=pos,
                                                                                                             types=[
                                                                                                                 type(p)
                                                                                                                 for p
                                                                                                                 in
                                                                                                                 pos]))
        self.x = pos[0]
        self.y = pos[1]

    def __hash__(self):
        return hash(tuple([self.x, self.y, self.name]))

    def __add__(self, other):
        if isinstance(other, RayNode):
            return self.position + other.position
        return self.position + other

    def __radd__(self, other):
        return other + self.position

    def __sub__(self, other):
        if isinstance(other, RayNode):
            return self.position - other.position
        return self.position - other

    def __rsub__(self, other):
        return other - self.position

    def __mul__(self, other):
        if isinstance(other, RayNode):
            return self.position * other.position
        return self.position * other

    def __rmul__(self, other):
        return other * self.position

    def __truediv__(self, other):
        if isinstance(other, RayNode):
            return self.position / other.position
        return self.position / other

    def __rtruediv__(self, other):
        return other / self.position

    def __pow__(self, power, modulo=None):
        return self.position.__pow__(power, modulo)

    def __neg__(self):
        return -self.position

    def __eq__(self, other):
        if isinstance(other, RayNode):
            return self.position == other.position
        return self.position == other

    def __ne__(self, other):
        if isinstance(other, RayNode):
            return self.position != other.position
        return self.position != other

    def __ge__(self, other):
        if isinstance(other, RayNode):
            return self.y != other.y
        return self.y >= other

    def __gt__(self, other):
        if isinstance(other, RayNode):
            return self.y <= other.y
        return self.y > other

    def __le__(self, other):
        if isinstance(other, RayNode):
            return self.y <= other.y
        return self.y <= other

    def __lt__(self, other):
        if isinstance(other, RayNode):
            return self.y < other.y
        return self.y < other

    def __abs__(self):
        return abs(self.position)

    def __format__(self, format_spec):
        return '({self.x:{f}}, {self.y:{f}})'.format(self=self, f=format_spec)

    def __str__(self):
        return '{self.__class__.__name__} "{self.name}": {self:.2f}'.format(self=self)

    def __repr__(self):
        return '{self.__class__.__name__}({self.x}, {self.y}, name={self.name})'.format(self=self)

    def show(self, ax, *args, **kwargs):
        """
        Show the node in the axes.

        :param ax: a matplotlib.pyplot.axes object
        :param args: Optional arguments passed to ax.plot()
        :param kwargs: Optional keyword arguments passed to ax.plot()
        :return:
        """
        ax.plot(self.x, self.y, *args, **kwargs)


class RaySegment(object):
    """
    A ray object describing a ray path
    """

    def __init__(self, start, stop, angle=None, name=''):
        """
        Create a new ray.

        If neither stop nor angle is provided. creates a ray node (point) with start=stop.

        :param start: The start point of the ray
        :param stop: The endpoint of the ray.
        :param angle: The angle of the ray relative to the optical axis. Optional. Default is None
        :param name: The name of the ray.
        :type start: RayNode
        :type stop: RayNode, None
        :type angle: tuple, None
        :type name: str
        """
        if not isinstance(start, RayNode):
            raise TypeError(
                'Startpoint must be a RayNode, not {start!r} of type {t}'.format(start=start, t=type(start)))
        if not isinstance(stop, RayNode):
            raise TypeError(
                'Endpoint must be a RayNode, not {stop!r} of type {t}'.format(stop=stop, t=type(stop)))
        self.start = start
        self.stop = stop
        self.start.name = '{name} (start)'.format(name=name)
        self.stop.name = '{name} (end)'.format(name=name)
        self.name = name

        if angle is not None:
            length = abs(float(stop.y - start.y))  # Length along optical axis
            if length > 0:
                self.set_angle(angle, fixed='start')

    def __repr__(self):
        return '{self.__class__.__name__}({self.start!r}, stop={self.stop!r}, name={self.name!r})'.format(self=self)

    def __format__(self, format_spec):
        return '{self.start:{f}} -> {self.stop:{f}} ({angle:{f}} deg)'.format(self=self, f=format_spec,
                                                                              angle=self.angle())

    def __str__(self):
        return '{self.__class__.__name__} "{self.name}": {self:.2f}'.format(self=self)

    def dx(self):
        """
        Return pathlength perpendicular to optical axis
        :return: pathlength
        :rtype: float
        """
        return self.stop.x - self.start.x

    def dy(self):
        """
        Return pathlength along optical axis.
        :return: pathlength
        :rtype: float
        """
        return self.stop.y - self.start.y

    def length(self):
        """
        Return length of ray
        :return: length
        :rtype: float
        """
        return np.sqrt(np.sum((self.stop - self.start) ** 2))

    def angle(self, deg=True):
        """
        Return angle of ray
        :param deg: Whether to return angle in degrees or not. Default is True
        :type deg: bool
        :return: angle of ray
        :rtype: float

        """
        angle = acos(self.dy() / self.length()) * 180. / pi

        if self.dx() < 0:
            angle = angle - 180
        else:
            angle = 180 - angle

        if not deg:
            angle = angle * pi / 180
        return angle

    def set_angle(self, angle, fixed='start', deg=True):
        """Change the angle of the ray

        :param angle: The angle set for the ray. Positive counterclockwise
        :type angle: int or float
        :param fixed: Which point to use as a fixed point. Default is "start".
        :type fixed: str
        :param deg: Whether the angle is given in degrees or not. Default is True
        :type deg: bool
        """

        if fixed == 'start':
            fixed_point = self.start
            variable_point = self.stop
            sign = 1
        elif fixed == 'stop':
            fixed_point = self.stop
            variable_point = self.start
            sign = -1
        else:
            raise ValueError(
                'Fixed position {fixed!r} not recognized. Please specify "start" or "stop"'.format(fixed=fixed))

        if not deg:
            angle = angle * 180 / pi

        length = abs(self.dy())  # length of ray along optical axis

        reduced_angle = reduce_angle(angle)  # Angle reduced to (-180, 180)
        if reduced_angle == 0:
            x = fixed_point.x
            y = fixed_point.y - sign * length
        elif reduced_angle == 180:
            x = fixed_point.x
            y = fixed_point.y + sign * length
        elif reduced_angle % 90 == 0:
            if reduced_angle < 0:
                x = -inf
            else:
                x = inf
            y = fixed_point.y
        else:
            if abs(reduced_angle) < 90:
                x = fixed_point.x + sign * tan(reduced_angle * pi / 180.) * length
                y = fixed_point.y - sign * length
            else:
                x = fixed_point.x - sign * tan(reduced_angle * pi / 180.) * length
                y = fixed_point.y + sign * length
        variable_point.x = x
        variable_point.y = y

    def tilt(self, angle, fixed='start', deg=True):
        """
        Tilt the ray by a certain angle
        :param angle: The angle to tilt the ray with. Positive counterclockwise
        :param fixed: Which point to be fixed. Default is "start"
        :param deg: Whether the angle is gicen in degrees or not. Default is True
        :type angle: int or float
        :type fixed: str
        :type deg: bool
        :return:
        """
        self.set_angle(self.angle() + angle, fixed, deg)

    def extend(self, y, relative=False):
        """
        Extend (or shrink) ray to end at new position.
        :param y: The new end position in absolute position (`relative=False`) or in relative position (`relative=True`)
        :param relative: Whether the termination point is relative or not. Default is False
        :type y: int, float
        :type relative: bool
        :return:
        """
        angle = self.angle()
        if relative:
            self.stop.y = self.start.y + y
        else:
            self.stop.y = y
        self.set_angle(angle, fixed='start')

    def x_at_y(self, y, relative = False):
        """
        Return the x-position at position y along line.
        :param y: The position to "extrapolate" to.
        :type y: float
        :param relative: Whether y is relative to start of ray or absolute
        :type relative: bool
        :return: The x-position at y along line
        :rtype: float
        """
        if not self.start.y > y > self.stop.y:
            raise ValueError('Position {y!r} does not lie within y-range of raysegment {self!r}'.format(y=y, self=self))
        if relative:
            dy = y
        else:
            dy = self.start.y - y
        return dy * tan(self.angle(deg=False))

    def show(self, ax, *args, **kwargs):
        """
        Show the ray in the axes
        :param ax: The axes to show the ray in.
        :param args: Optional positional arguments passed to ax.plot()
        :param kwargs: Optional keyword arguments passed to ax.plot()
        :type ax: matplotlib.pyplot.axes
        :return:
        """
        self.start.show(ax, 'kx')
        self.stop.show(ax, 'kx')
        ax.plot((self.start.x, self.stop.x), (self.start.y, self.stop.y), *args, **kwargs)


class Ray(object):
    """
    A ray consisting of several segments between nodes.
    """

    def __init__(self, source, end):
        """
        Create a ray between a source and an end with nodes in between.
        :param source: The source of the ray
        :param end: The end of the ray
        :type source: RayNode
        :type end: RayNode
        """

        if not isinstance(source, RayNode):
            raise TypeError(
                'Source must be a RayNode, not {source!r} of type {t}'.format(source=source, t=type(source)))

        if not isinstance(end, RayNode):
            raise TypeError('End must be a RayNode, not {end!r} of type {t}'.format(end=end, t=type(end)))

        self.source = source
        self.end = end
        # self.nodes = list([self.source, self.end])
        self.segments = list([RaySegment(self.source, self.end)])

        # self.nodes.sort(key=lambda x: x.y)
        # if self.source not in self.nodes:
        #    self.nodes.insert(0, self.source)
        # if self.end not in self.nodes:
        #    self.nodes.insert(-1, self.end)
        # self.segments = [RaySegment(A, B) for A, B in zip(self.nodes[:-1], self.nodes[1:])]

    def __repr__(self):
        return '{self.__class__.__name__}({self.source!r}, {self.end!r})'.format(self=self)

    def __format__(self, format_spec):
        return '\n'.join(['{segment:{f}}'.format(segment=segment, f=format_spec) for segment in self.segments])

    def __str__(self):
        return '{self.__class__.__name__} with segments:\n{self:.2f}'.format(self=self)

    # def __setitem__(self, key, value):
    #     if not isinstance(value, RayNode):
    #         raise TypeError('Only RayNode objects can be set in a Ray')
    #     self.nodes[key] = value

    def __getitem__(self, item):
        return self.segments[item]

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def __iadd__(self, other):
        self.add_node(other)
        return self

    def __isub__(self, other):
        self.remove_node(other)
        return self

    def add_node(self, node):
        if not isinstance(node, RayNode):
            raise TypeError('Only RayNodes may be added to a Ray')
        added = False
        for segment_number, segment in enumerate(self):
            if segment.start >= node.y >= segment.stop:
                new_segment = RaySegment(node, segment.stop)
                segment.stop = node
                self.segments.insert(segment_number + 1, new_segment)
                added = True
                break
        if not added:
            raise ValueError(
                'Could not add Node {node!r} to {self!r}. It does not fit between {self.source!r} and {self.end!r}'.format(
                    node=node, self=self))

    def remove_node(self, node):
        if not isinstance(node, RayNode):
            raise TypeError('Only RayNodes may be removed from a Ray')
        removed = False
        for segment_number, segment in enumerate(self):
            if segment.stop is node:
                segment.stop = self[segment_number + 1].stop
                self[segment_number + 1].start = segment.start
                removed = True
                break
        if not removed:
            raise ValueError(
                'Node {node!r} could not be removed from {self!r}. It was not found in the segments.'.format(node=node, self=self))

    def get_nodes(self):
        return [segment.start for segment in self].append(self[-1].stop)

    def show(self, ax, *args, **kwargs):
        [segment.show(ax, *args, **kwargs) for segment in self]


def reduce_angle(angle):
    """
    Reduces an angle to (-180, 180)
    :param angle: The angle to reduce
    :type angle: int, float
    :return: reduced angle
    :rtype: float
    """
    angle = float(angle)
    angle = angle % 360
    if angle > 180:
        angle = angle - 360
    return angle
