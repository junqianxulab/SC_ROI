import numpy as np
from matplotlib.lines import Line2D

class Point2D:
    def __init__(self, x, y, parent):
        self.x = x
        self.y = y
        self.parent = parent

    def set(self, x, y):
        self.x = x
        self.y = y
        self.parent.update_point(self)

class Point1D:
    def __init__(self, x, parent):
        self.x = x
        self.parent = parent

    def set(self, x):
        self.x = x
        self.parent.update_point(self)



class Roi_guide:
    def __init__(self, ax):
        self.ax = ax

        self.a = Point2D(120, 42, self)
        self.b = Point2D(150, 42, self)
        self.c = Point2D(135, 32, self)
        self.d = Point2D(125, 36, self)
        self.e = Point2D(145, 36, self)

        self.f = Point1D(0.5, self)
        self.g = Point1D(0.5, self)
        self.h = Point1D(0.5, self)
        self.i = Point1D(0.5, self)
        self.j = Point1D(0.5, self)

        self.create_point2d_from_1d(self.f)
        self.create_point2d_from_1d(self.g)
        self.create_point2d_from_1d(self.h)
        self.create_point2d_from_1d(self.i)
        self.create_point2d_from_1d(self.j)

        self.points = [self.a, self.b, self.c, self.d, self.e,
                       self.f, self.g, self.h, self.i, self.j]
        self.points2d = [self.a, self.b, self.c, self.d, self.e,
                self.f2d, self.g2d, self.h2d, self.i2d, self.j2d]

        self.depend_on = {
                self.f: [self.a, self.b],
                self.g: [self.f, self.a],
                self.h: [self.f, self.d],
                self.i: [self.f, self.b],
                self.j: [self.f, self.e],
                self.f2d: [self.f],
                self.g2d: [self.g],
                self.h2d: [self.h],
                self.i2d: [self.i],
                self.j2d: [self.j],
                }
        self.set_affect()
        self.drawings = []
        self.set_drawings()

    def to_floats(self):
        return [
                self.a.x, self.a.y,
                self.b.x, self.b.y,
                self.c.x, self.c.y,
                self.d.x, self.d.y,
                self.e.x, self.e.y,
                self.f.x,
                self.g.x,
                self.h.x,
                self.i.x,
                self.j.x,
            ]

    def from_floats(self, lst_floats):
        self.a.x, self.a.y, \
                self.b.x, self.b.y, \
                self.c.x, self.c.y, \
                self.d.x, self.d.y, \
                self.e.x, self.e.y, \
                self.f.x, \
                self.g.x, \
                self.h.x, \
                self.i.x, \
                self.j.x = lst_floats

    def set_affect_of_one(self, point, exclude=[]):
        return [key for key in self.depend_on.keys() if point in self.depend_on[key] and key not in exclude]
        
    def set_affect(self):
        self.affect = {}
        leaf = set([value for lst in self.depend_on.values() for value in lst])
        for point in leaf:
            lst = self.set_affect_of_one(point)
            lst_todo = [key for key in lst if key in leaf]
            while lst_todo:
                lst_added = []
                for key in lst_todo:
                    lst_added += self.set_affect_of_one(key, exclude=lst+lst_added)
                lst += lst_added
                lst_todo = [key for key in lst_added if key in leaf]
            self.affect[point] = lst

    def verify_point(self, point):
        if point is self.a:
            if point.x >= self.b.x:
                point.x = self.b.x - 1
            if point.y <= self.c.y:
                point.y = self.c.y + 1
            if point.y <= self.d.y:
                point.y = self.d.y + 1

        elif point is self.b:
            if point.x <= self.a.x:
                point.x = self.a.x + 1
            if point.y <= self.c.y:
                point.y = self.c.y + 1
            if point.y <= self.e.y:
                point.y = self.e.y + 1

        elif point is self.c:
            if point.x <= self.a.x:
                point.x = self.a.x + 1
            if point.x >= self.b.x:
                point.x = self.b.x - 1
            if point.y >= self.a.y:
                point.y = self.a.y - 1
            if point.y >= self.b.y:
                point.y = self.b.y - 1

        elif point is self.d:
            if point.x <= self.a.x:
                point.x = self.a.x + 1
            if point.x >= self.c.x:
                point.x = self.c.x - 1
            if point.y >= self.a.y:
                point.y = self.a.y - 1

        elif point is self.e:
            if point.x <= self.c.x:
                point.x = self.c.x + 1
            if point.x >= self.b.x:
                point.x = self.b.x - 1
            if point.y >= self.b.y:
                point.y = self.b.y - 1

        else:
            if point.x < 0.1:
                point.x = 0.1
            if point.x > 0.9:
                point.x = 0.9

    def create_point2d_from_1d(self, point):
        if point is self.f:
            self.f2d = Point2D(
                    self.a.x + point.x * (self.b.x - self.a.x),
                    self.a.y + point.x * (self.b.y - self.a.y),
                    self
                    )

        elif point is self.g:
            self.g2d = Point2D(
                    self.f2d.x + point.x * (self.a.x - self.f2d.x),
                    self.f2d.y + point.x * (self.a.y - self.f2d.y),
                    self
                    )

        elif point is self.h:
            self.h2d = Point2D(
                    self.f2d.x + point.x * (self.d.x - self.f2d.x),
                    self.f2d.y + point.x * (self.d.y - self.f2d.y),
                    self
                    )
        
        elif point is self.i:
            self.i2d = Point2D(
                    self.f2d.x + point.x * (self.b.x - self.f2d.x),
                    self.f2d.y + point.x * (self.b.y - self.f2d.y),
                    self
                    )
        
        elif point is self.j:
            self.j2d = Point2D(
                    self.f2d.x + point.x * (self.e.x - self.f2d.x),
                    self.f2d.y + point.x * (self.e.y - self.f2d.y),
                    self
                    )

    def update_point1d(self, point, drawing=True):
        if point is self.f:
            self.f2d.x = self.a.x + point.x * (self.b.x - self.a.x)
            self.f2d.y = self.a.y + point.x * (self.b.y - self.a.y)

        elif point is self.g:
            self.g2d.x = self.f2d.x + point.x * (self.a.x - self.f2d.x)
            self.g2d.y = self.f2d.y + point.x * (self.a.y - self.f2d.y)

        elif point is self.h:
            self.h2d.x = self.f2d.x + point.x * (self.d.x - self.f2d.x)
            self.h2d.y = self.f2d.y + point.x * (self.d.y - self.f2d.y)

        elif point is self.i:
            self.i2d.x = self.f2d.x + point.x * (self.b.x - self.f2d.x)
            self.i2d.y = self.f2d.y + point.x * (self.b.y - self.f2d.y)
        
        elif point is self.j:
            self.j2d.x = self.f2d.x + point.x * (self.e.x - self.f2d.x)
            self.j2d.y = self.f2d.y + point.x * (self.e.y - self.f2d.y)
        
        if drawing:
            self.update_point_drawing(point)

    def is_on(self, x, y):
        pass

    def set_drawings(self):
        lw = 3.0
        self.ab = Line2D([self.a.x,   self.b.x],  [self.a.y,    self.b.y],   linestyle='-', color='coral', lw=lw, animated=True)
        self.fc = Line2D([self.f2d.x, self.c.x],  [self.f2d.y,  self.c.y],   linestyle='-', color='coral', lw=lw, animated=True)
        self.fd = Line2D([self.f2d.x, self.d.x],  [self.f2d.y,  self.d.y],   linestyle='-', color='coral', lw=lw, animated=True)
        self.fe = Line2D([self.f2d.x, self.e.x],  [self.f2d.y,  self.e.y],   linestyle='-', color='coral', lw=lw, animated=True)
        self.gh = Line2D([self.g2d.x, self.h2d.x], [self.g2d.y, self.h2d.y], linestyle='-', color='coral', lw=lw, animated=True)
        self.ij = Line2D([self.i2d.x, self.j2d.x], [self.i2d.y, self.j2d.y], linestyle='-', color='coral', lw=lw, animated=True)

        picker=2
        self.point_a = Line2D([self.a.x],   [self.a.y],   linestyle='none', marker='o', color='b', animated=True)
        self.point_b = Line2D([self.b.x],   [self.b.y],   linestyle='none', marker='o', color='b', animated=True)
        self.point_c = Line2D([self.c.x],   [self.c.y],   linestyle='none', marker='o', color='b', animated=True)
        self.point_d = Line2D([self.d.x],   [self.d.y],   linestyle='none', marker='o', color='b', animated=True)
        self.point_e = Line2D([self.e.x],   [self.e.y],   linestyle='none', marker='o', color='b', animated=True)
        self.point_f = Line2D([self.f2d.x], [self.f2d.y], linestyle='none', marker='o', color='b', animated=True)
        self.point_g = Line2D([self.g2d.x], [self.g2d.y], linestyle='none', marker='o', color='b', animated=True)
        self.point_h = Line2D([self.h2d.x], [self.h2d.y], linestyle='none', marker='o', color='b', animated=True)
        self.point_i = Line2D([self.i2d.x], [self.i2d.y], linestyle='none', marker='o', color='b', animated=True)
        self.point_j = Line2D([self.j2d.x], [self.j2d.y], linestyle='none', marker='o', color='b', animated=True)

        self.depend_on[self.ab] = [self.a, self.b]
        self.depend_on[self.fc] = [self.f, self.c]
        self.depend_on[self.fd] = [self.f, self.d]
        self.depend_on[self.fe] = [self.f, self.e]
        self.depend_on[self.gh] = [self.g, self.h]
        self.depend_on[self.ij] = [self.i, self.j]

        self.depend_on[self.point_a] = [self.a]
        self.depend_on[self.point_b] = [self.b]
        self.depend_on[self.point_c] = [self.c]
        self.depend_on[self.point_d] = [self.d]
        self.depend_on[self.point_e] = [self.e]
        self.depend_on[self.point_f] = [self.f]
        self.depend_on[self.point_g] = [self.g]
        self.depend_on[self.point_h] = [self.h]
        self.depend_on[self.point_i] = [self.i]
        self.depend_on[self.point_j] = [self.j]

        if False:
            self.ax.text(self.a.x, self.a.y, 'a')
            self.ax.text(self.b.x, self.b.y, 'b')
            self.ax.text(self.c.x, self.c.y, 'c')
            self.ax.text(self.d.x, self.d.y, 'd')
            self.ax.text(self.e.x, self.e.y, 'e')
            self.ax.text(self.f2d.x, self.f2d.y, 'f')
            self.ax.text(self.g2d.x, self.g2d.y, 'g')
            self.ax.text(self.h2d.x, self.h2d.y, 'h')
            self.ax.text(self.i2d.x, self.i2d.y, 'i')
            self.ax.text(self.j2d.x, self.j2d.y, 'j')

        self.ax.axis((110, 160, 25, 55))
        self.drawings += [
                self.ab,
                self.fc,
                self.fd,
                self.fe,
                self.gh,
                self.ij,
                self.point_a,
                self.point_b,
                self.point_c,
                self.point_d,
                self.point_e,
                self.point_f,
                self.point_g,
                self.point_h,
                self.point_i,
                self.point_j,
                ]

    def plot(self):
        self.ax.add_line(self.ab)
        self.ax.add_line(self.fc)
        self.ax.add_line(self.fd)
        self.ax.add_line(self.fe)
        self.ax.add_line(self.gh)
        self.ax.add_line(self.ij)
        self.ax.add_line(self.point_a)
        self.ax.add_line(self.point_b)
        self.ax.add_line(self.point_c)
        self.ax.add_line(self.point_d)
        self.ax.add_line(self.point_e)
        self.ax.add_line(self.point_f)
        self.ax.add_line(self.point_g)
        self.ax.add_line(self.point_h)
        self.ax.add_line(self.point_i)
        self.ax.add_line(self.point_j)

    def _plot(self):
        lw = 3.0
        self.ab = self.ax.plot([self.a.x,   self.b.x],  [self.a.y,    self.b.y],   '-', color='coral', lw=lw)[0]
        self.fc = self.ax.plot([self.f2d.x, self.c.x],  [self.f2d.y,  self.c.y],   '-', color='coral', lw=lw)[0]
        self.fd = self.ax.plot([self.f2d.x, self.d.x],  [self.f2d.y,  self.d.y],   '-', color='coral', lw=lw)[0]
        self.fe = self.ax.plot([self.f2d.x, self.e.x],  [self.f2d.y,  self.e.y],   '-', color='coral', lw=lw)[0]
        self.gh = self.ax.plot([self.g2d.x, self.h2d.x], [self.g2d.y, self.h2d.y], '-', color='coral', lw=lw)[0]
        self.ij = self.ax.plot([self.i2d.x, self.j2d.x], [self.i2d.y, self.j2d.y], '-', color='coral', lw=lw)[0]

        self.point_a = self.ax.plot(self.a.x,   self.a.y,   'o', color='b')[0]
        self.point_b = self.ax.plot(self.b.x,   self.b.y,   'o', color='b')[0]
        self.point_c = self.ax.plot(self.c.x,   self.c.y,   'o', color='b')[0]
        self.point_d = self.ax.plot(self.d.x,   self.d.y,   'o', color='b')[0]
        self.point_e = self.ax.plot(self.e.x,   self.e.y,   'o', color='b')[0]
        self.point_f = self.ax.plot(self.f2d.x, self.f2d.y, 'o', color='b')[0]
        self.point_g = self.ax.plot(self.g2d.x, self.g2d.y, 'o', color='b')[0]
        self.point_h = self.ax.plot(self.h2d.x, self.h2d.y, 'o', color='b')[0]
        self.point_i = self.ax.plot(self.i2d.x, self.i2d.y, 'o', color='b')[0]
        self.point_j = self.ax.plot(self.j2d.x, self.j2d.y, 'o', color='b')[0]

        self.depend_on[self.ab] = [self.a, self.b]
        self.depend_on[self.fc] = [self.f, self.c]
        self.depend_on[self.fd] = [self.f, self.d]
        self.depend_on[self.fe] = [self.f, self.e]
        self.depend_on[self.gh] = [self.g, self.h]
        self.depend_on[self.ij] = [self.i, self.j]

        self.depend_on[self.point_a] = [self.a]
        self.depend_on[self.point_b] = [self.b]
        self.depend_on[self.point_c] = [self.c]
        self.depend_on[self.point_d] = [self.d]
        self.depend_on[self.point_e] = [self.e]
        self.depend_on[self.point_f] = [self.f]
        self.depend_on[self.point_g] = [self.g]
        self.depend_on[self.point_h] = [self.h]
        self.depend_on[self.point_i] = [self.i]
        self.depend_on[self.point_j] = [self.j]

        if False:
            self.ax.text(self.a.x, self.a.y, 'a')
            self.ax.text(self.b.x, self.b.y, 'b')
            self.ax.text(self.c.x, self.c.y, 'c')
            self.ax.text(self.d.x, self.d.y, 'd')
            self.ax.text(self.e.x, self.e.y, 'e')
            self.ax.text(self.f2d.x, self.f2d.y, 'f')
            self.ax.text(self.g2d.x, self.g2d.y, 'g')
            self.ax.text(self.h2d.x, self.h2d.y, 'h')
            self.ax.text(self.i2d.x, self.i2d.y, 'i')
            self.ax.text(self.j2d.x, self.j2d.y, 'j')

        self.ax.axis((110, 160, 25, 55))
        self.drawings += [
                self.ab,
                self.fc,
                self.fd,
                self.fe,
                self.gh,
                self.ij,
                self.point_a,
                self.point_b,
                self.point_c,
                self.point_d,
                self.point_e,
                self.point_f,
                self.point_g,
                self.point_h,
                self.point_i,
                self.point_j,
                ]

    def update_line_drawing(self, line):
        if line is self.ab: line.set_data([self.a.x, self.b.x], [self.a.y, self.b.y])
        if line is self.fc: line.set_data([self.f2d.x, self.c.x], [self.f2d.y, self.c.y])
        if line is self.fd: line.set_data([self.f2d.x, self.d.x], [self.f2d.y, self.d.y])
        if line is self.fe: line.set_data([self.f2d.x, self.e.x], [self.f2d.y, self.e.y])
        if line is self.gh: line.set_data([self.g2d.x, self.h2d.x], [self.g2d.y, self.h2d.y])
        if line is self.ij: line.set_data([self.i2d.x, self.j2d.x], [self.i2d.y, self.j2d.y])

    def update_point_drawing(self, point):
        if point is self.a: self.point_a.set_data(self.a.x, self.a.y)
        if point is self.b: self.point_b.set_data(self.b.x, self.b.y)
        if point is self.c: self.point_c.set_data(self.c.x, self.c.y)
        if point is self.d: self.point_d.set_data(self.d.x, self.d.y)
        if point is self.e: self.point_e.set_data(self.e.x, self.e.y)
        if point is self.f: self.point_f.set_data(self.f2d.x, self.f2d.y)
        if point is self.g: self.point_g.set_data(self.g2d.x, self.g2d.y)
        if point is self.h: self.point_h.set_data(self.h2d.x, self.h2d.y)
        if point is self.i: self.point_i.set_data(self.i2d.x, self.i2d.y)
        if point is self.j: self.point_j.set_data(self.j2d.x, self.j2d.y)

    def update_point_from_event(self, point, x, y):
        if point is self.a:
            self.update_point(self.a, x, y)
        elif point is self.b:
            self.update_point(self.b, x, y)
        elif point is self.c:
            self.update_point(self.c, x, y)
        elif point is self.d:
            self.update_point(self.d, x, y)
        elif point is self.e:
            self.update_point(self.e, x, y)
        elif point is self.f2d:
            self.update_point(self.f, x, y)
        elif point is self.g2d:
            self.update_point(self.g, x, y)
        elif point is self.h2d:
            self.update_point(self.h, x, y)
        elif point is self.i2d:
            self.update_point(self.i, x, y)
        elif point is self.j2d:
            self.update_point(self.j, x, y)

        if False: # incremental
            if point is self.a:
                self.update_point(self.a, point.x+x, point.y+y)
            elif point is self.b:
                self.update_point(self.b, point.x+x, point.y+y)
            elif point is self.c:
                self.update_point(self.c, point.x+x, point.y+y)
            elif point is self.d:
                self.update_point(self.d, point.x+x, point.y+y)
            elif point is self.e:
                self.update_point(self.e, point.x+x, point.y+y)
            elif point is self.f2d:
                self.update_point(self.f, self.f2d.x+x, self.f2d.y+y)
            elif point is self.g2d:
                self.update_point(self.g, self.g2d.x+x, self.g2d.y+y)
            elif point is self.h2d:
                self.update_point(self.h, self.h2d.x+x, self.h2d.y+y)
            elif point is self.i2d:
                self.update_point(self.i, self.i2d.x+x, self.i2d.y+y)
            elif point is self.j2d:
                self.update_point(self.j, self.j2d.x+x, self.j2d.y+y)

    def update_all(self):
        for point in [self.f, self.g, self.h, self.i, self.j]:
            self.update_point1d(point, drawing=True)

        self.update_line_drawing(self.ab)
        self.update_line_drawing(self.fc)
        self.update_line_drawing(self.fd)
        self.update_line_drawing(self.fe)
        self.update_line_drawing(self.gh)
        self.update_line_drawing(self.ij)
        self.update_point_drawing(self.a)
        self.update_point_drawing(self.b)
        self.update_point_drawing(self.c)
        self.update_point_drawing(self.d)
        self.update_point_drawing(self.e)
        self.update_point_drawing(self.f)
        self.update_point_drawing(self.g)
        self.update_point_drawing(self.h)
        self.update_point_drawing(self.i)
        self.update_point_drawing(self.j)

    def update_point(self, point, x=None, y=None):
        if isinstance(point, Point2D) and x is not None and y is not None:
            point.x = x
            point.y = y
        
        self.verify_point(point)
        if point is self.a or point is self.b:
            self.update_point_drawing(point)
            self.update_point1d(self.f)
            self.update_point1d(self.g)
            self.update_point1d(self.h)
            self.update_point1d(self.i)
            self.update_point1d(self.j)
            self.update_line_drawing(self.ab)
            self.update_line_drawing(self.fc)
            self.update_line_drawing(self.fd)
            self.update_line_drawing(self.fe)
            self.update_line_drawing(self.gh)
            self.update_line_drawing(self.ij)
        elif point is self.c:
            self.update_point_drawing(point)
            self.update_line_drawing(self.fc)
        elif point is self.d:
            self.update_point_drawing(point)
            self.update_point1d(self.g)
            self.update_point1d(self.h)
            self.update_line_drawing(self.fd)
            self.update_line_drawing(self.gh)
        elif point is self.e:
            self.update_point_drawing(point)
            self.update_point1d(self.i)
            self.update_point1d(self.j)
            self.update_line_drawing(self.fe)
            self.update_line_drawing(self.ij)
        elif point is self.f:
            if x is not None and y is not None:
                # projection to ab
                ab = self.b.x-self.a.x, self.b.y-self.a.y
                ax = x -self.a.x, y -self.a.y
                point.x = (ax[0]*ab[0] + ax[1]*ab[1]) / (ab[0]*ab[0]+ab[1]*ab[1])
            self.update_point1d(self.f)
            self.update_point1d(self.g)
            self.update_point1d(self.h)
            self.update_point1d(self.i)
            self.update_point1d(self.j)
            self.update_line_drawing(self.fc)
            self.update_line_drawing(self.fd)
            self.update_line_drawing(self.fe)
            self.update_line_drawing(self.gh)
            self.update_line_drawing(self.ij)
        elif point is self.g:
            if x is not None and y is not None:
                # projection to fa
                ab = self.a.x-self.f2d.x, self.a.y-self.f2d.y
                ax = x -self.f2d.x, y -self.f2d.y
                point.x = (ax[0]*ab[0] + ax[1]*ab[1]) / (ab[0]*ab[0]+ab[1]*ab[1])
            self.update_point1d(self.g)
            self.update_line_drawing(self.gh)
        elif point is self.h:
            if x is not None and y is not None:
                # projection to fd
                ab = self.d.x-self.f2d.x, self.d.y-self.f2d.y
                ax = x -self.f2d.x, y -self.f2d.y
                point.x = (ax[0]*ab[0] + ax[1]*ab[1]) / (ab[0]*ab[0]+ab[1]*ab[1])
            self.update_point1d(self.h)
            self.update_line_drawing(self.gh)
        elif point is self.i:
            if x is not None and y is not None:
                # projection to fb
                ab = self.b.x-self.f2d.x, self.b.y-self.f2d.y
                ax = x -self.f2d.x, y -self.f2d.y
                point.x = (ax[0]*ab[0] + ax[1]*ab[1]) / (ab[0]*ab[0]+ab[1]*ab[1])
            self.update_point1d(self.i)
            self.update_line_drawing(self.ij)
        elif point is self.j:
            if x is not None and y is not None:
                # projection to fe
                ab = self.e.x-self.f2d.x, self.e.y-self.f2d.y
                ax = x -self.f2d.x, y -self.f2d.y
                point.x = (ax[0]*ab[0] + ax[1]*ab[1]) / (ab[0]*ab[0]+ab[1]*ab[1])
            self.update_point1d(self.j)
            self.update_line_drawing(self.ij)

