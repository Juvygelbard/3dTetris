import numpy as np
from itertools import product
import tkinter


class VecUtil:
    @staticmethod
    def project(v):
        norm = 1.0 / v[-1]
        return norm * v[:-1]

    @staticmethod
    def l2sq(v1, v2=None):
        v = v1 if v2 is None else v2 - v1
        return np.sum(np.square(v))

    @staticmethod
    def l2(v1, v2=None):
        return np.sqrt(VecUtil.l2sq(v1, v2))

    @staticmethod
    def norm(p1, p2, p3):
        v12 = p2 - p1
        v13 = p3 - p1
        vn = np.cross(v12, v13)
        inv_n = 1.0 / VecUtil.l2(vn)
        return inv_n * vn


class GUI:
    def draw(self, canvas, **kwargs):
        raise NotImplementedError


class GUIRect(GUI):
    def __init__(self, l, t, w, h, color):
        self._l = l
        self._t = t
        self._r = l + w
        self._b = t + h
        self._color = color.toHTML()

    def draw(self, canvas, **kwargs):
        canvas.create_rectangle(self._l, self._t, self._r, self._b, fill=self._color, width=2)


class GUIText(GUI):
    LEFT = tkinter.LEFT
    CENTER = tkinter.CENTER
    RIGHT = tkinter.RIGHT

    def __init__(self, text, x, y, size, color, align=tkinter.LEFT):
        self._text = text
        self._x = x
        self._y = y
        self._size = size
        self._color = color.toHTML()
        self._align = align

    def draw(self, canvas, **kwargs):
        canvas.create_text(self._x, self._y, text=self._text, fill=self._color, justify=self._align, font=('Ariel', self._size))


class Position:
    """
        params: X, Y, Z are real-world coordinates [pixels]
                y, p, r are euler angles [radians]
    """
    def __init__(self, X, Y, Z, y, p, r):
        self.set_position(X, Y, Z, y, p, r)

    def set_position(self, X, Y, Z, y, p, r):
        self._loc = np.array((X, Y, Z), dtype=np.float64)
        self._ori = np.array((y, p, r), dtype=np.float64)
        self.build_tf()

    def move(self, dX, dY, dZ, dy, dp, dr):
        self._loc += np.array((dX, dY, dZ), dtype=np.float64)
        self._ori += np.array((dy, dp, dr), dtype=np.float64)
        self.build_tf()

    def tf(self):
        return self._tf_mat

    def inv_tf(self):
        return self._inv_tf

    def build_tf(self):
        tr = Position.tr4_mat(*self._loc)
        rt = Position.rt4_mat(*self._ori)
        self._tf_mat = np.dot(tr, rt)
        inv_tr = Position.tr4_mat(*(-self._loc))
        inv_rt = np.transpose(rt)
        self._inv_tf = np.dot(inv_rt, inv_tr)

    @staticmethod
    def tr4_mat(X, Y, Z):
        tr4 = np.eye(4)
        tr4[0:3, 3] = X, Y, Z
        return tr4

    @staticmethod
    def rt4_mat(y, p, r):
        sinp = np.sin(p)
        cosp = np.cos(p)
        r_x = np.array(((1.0, 0.0, 0.0),
                        (0.0, cosp, -sinp),
                        (0.0, sinp, cosp)))
        siny = np.sin(y)
        cosy = np.cos(y)
        r_y = np.array(((cosy, 0.0, siny),
                        (0.0, 1.0, 0.0),
                        (-siny, 0.0, cosy)))
        sinr = np.sin(r)
        cosr = np.cos(r)
        r_z = np.array(((cosr, -sinr, 0.0),
                        (sinr, cosr, 0.0),
                        (0.0, 0.0, 1.0)))
        rt3 = np.dot(r_z, np.dot(r_y, r_x))
        rt4 = np.eye(4)
        rt4[0:3, 0:3] = rt3
        return rt4

    def location_vec(self):
        return self._loc

    def orientation_vec(self):
        return self._ori


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    def toHTML(self, fact=1.0):
        r = min(255, int(fact * self.r))
        g = min(255, int(fact * self.g))
        b = min(255, int(fact * self.b))
        html = "#%0.2x%0.2x%0.2x" % (r, g, b)
        return html


class Cam:
    def __init__(self, focal_length, position):
        self._pos = position
        self.build_k_mat(focal_length)

    def set_position(self, X, Y, Z, y, p, r):
        self._pos.set_position(X, Y, Z, y, p, r)

    def move(self, dX, dY, dZ, dy, dp, dr):
        self._pos.move(dX, dY, dZ, dy, dp, dr)

    def build_k_mat(self, fl):
        self._k = np.eye(3)
        self._k[0, 0] = fl
        self._k[1, 1] = fl

    def extrinsic_tf(self, v):
        p_ext = np.dot(self._pos.inv_tf(), v)
        return VecUtil.project(p_ext)

    def intrinsic_tf(self, v):
        p_int = np.dot(self._k, v)
        return VecUtil.project(p_int)

    def tf_mat(self):
        return self._pos.tf()

    def inv_tf_mat(self):
        return self._pos.inv_tf()


class Renderable:
    def render(self, cam, light, screen_w, screen_h, **kwargs):
        raise NotImplementedError


class Rendered:
    def Z(self):
        raise NotImplementedError

    def draw(self, canvas):
        raise NotImplementedError


class Polygon(Rendered):
    def __init__(self, img_cord, Z, color):
        self._img_cord = img_cord
        self._Z = Z
        self._color = color

    def Z(self):
        return self._Z

    def draw(self, canvas):
        cord = list()
        for x, y in self._img_cord:
            cord.append(x)
            cord.append(y)
        canvas.create_polygon(cord, fill=self._color, outline='black', width=2)


class Line(Rendered):
    def __init__(self, p1, p2, Z, width=1, dashed=False):
        self._p1 = p1
        self._p2 = p2
        self._Z = Z
        self._width = width
        self._dash = (2, 2) if dashed else None

    def Z(self):
        return self._Z

    def draw(self, canvas):
        canvas.create_line(self._p1[0], self._p1[1], self._p2[0], self._p2[1], width=self._width, dash=self._dash)


class HGrid(Renderable):
    # tile_w, tile_h are floats
    # grid_w, grid_h are integers
    def __init__(self, position, tile_w, tile_h, grid_w, grid_h):
        self._pos = position
        w_edge = tile_w * grid_w * 0.5
        h_edge = tile_h * grid_h * 0.5
        self._grid_h = grid_h
        self._grid_w = grid_w
        w_diff = np.linspace(-w_edge, w_edge, grid_w + 1)
        h_diff = np.linspace(-h_edge, h_edge, grid_h + 1)
        self._v_diff = np.empty((self._grid_h, self._grid_w, 4))
        for i in range(self._grid_h):
            for j in range(self._grid_w):
                self._v_diff[i][j] = w_diff[j], 0.0, h_diff[i], 1.0

    def render(self, cam, light, screen_w, screen_h, **kwargs):
        cx, cy = 0.5 * screen_w, 0.5 * screen_h
        v_wld, v_cam, v_img = self.calc_vertices(cam, cx, cy)

        for i in range(self._grid_h-1):
            for j in range(self._grid_w):
                # line behind camera
                if min(v_cam[i][j][2], v_cam[i+1][j][2]) < 0.2:
                    continue

                # line is outside of frame borders
                if max(v_img[i][j][0], v_img[i+1][j][0]) < 0 or min(v_img[i][j][0], v_img[i+1][j][0]) >= screen_w:
                    continue
                if max(v_img[i][j][1], v_img[i+1][j][1]) < 0 or min(v_img[i][j][1], v_img[i+1][j][1]) >= screen_h:
                    continue

                len_ray = min(VecUtil.l2(v_cam[i][j]), VecUtil.l2(v_cam[i+1][j]))

                yield Line(v_img[i][j], v_img[i+1][j], len_ray)

        for i in range(self._grid_h):
            for j in range(self._grid_w-1):
                # line behind camera
                if min(v_cam[i][j][2], v_cam[i][j+1][2]) < 0.2:
                    continue

                # line is outside of frame borders
                if max(v_img[i][j][0], v_img[i][j+1][0]) < 0 or min(v_img[i][j][0], v_img[i][j+1][0]) >= screen_w:
                    continue
                if max(v_img[i][j][1], v_img[i][j+1][1]) < 0 or min(v_img[i][j][1], v_img[i][j+1][1]) >= screen_h:
                    continue

                len_ray = min(VecUtil.l2(v_cam[i][j]), VecUtil.l2(v_cam[i][j+1]))

                yield Line(v_img[i][j], v_img[i][j+1], len_ray)


    def calc_vertices(self, cam, cx, cy):
        v_wld = np.empty((self._grid_h, self._grid_w, 3))
        v_cam = np.empty((self._grid_h, self._grid_w, 3))
        v_img = np.empty((self._grid_h, self._grid_w, 2))
        for i in range(self._grid_h):
            for j in range(self._grid_w):
                v_rw = np.dot(self._pos.tf(), self._v_diff[i][j])
                v_wld[i][j] = VecUtil.project(v_rw)
                v_ex = cam.extrinsic_tf(v_rw)
                v_cam[i][j] = v_ex
                v_in = cam.intrinsic_tf(v_ex)
                v_img[i][j] = cx + v_in[0], cy - v_in[1]
        return v_wld, v_cam, v_img


class FracLine(Renderable):
    # p1, p2 are 3d vectors, res is an integer
    def __init__(self, p1, p2, res):
        assert(res > 0)
        self._raw_pt = list()
        for i in range(res + 1):
            p3 = p1 * (i / res) + p2 * ((res - i) / res)
            p4 = np.array((p3[0], p3[1], p3[2], 1.0))
            self._raw_pt.append(p4)

    def render(self, cam, light, screen_w, screen_h, **kwargs):
        cx, cy = 0.5 * screen_w, 0.5 * screen_h

        cam1, int1, img1 = None, None, None
        first = True
        for pt2 in self._raw_pt:
            cam2 = cam.extrinsic_tf(pt2)
            int2 = cam.intrinsic_tf(cam2)
            img2 = cx + int2[0], cy - int2[1]

            if not first:
                # line behind camera
                if min(cam1[2], cam2[2]) < 0.2:
                    cam1 = cam2
                    img1 = img2
                    continue

                # line is outside of frame borders
                if max(img1[0], img2[0]) < 0 or min(img1[0], img2[0]) >= screen_w:
                    cam1 = cam2
                    img1 = img2
                    continue
                if max(img1[1], img2[1]) < 0 or min(img1[1], img2[1]) >= screen_h:
                    cam1 = cam2
                    img1 = img2
                    continue

                len_ray = min(VecUtil.l2(cam1), VecUtil.l2(cam2))

                yield Line(img1, img2, len_ray, width=2)

            cam1 = cam2
            img1 = img2
            first = False


class HBox(Renderable):
    LINES = ((0, 1, 2), (1, 3, 1), (3, 2, 2), (2, 0, 1),
             (4, 5, 2), (5, 7, 1), (7, 6, 2), (6, 4, 1),
             (2, 6, 0), (3, 7, 0), (0, 4, 0), (1, 5, 0))

    def __init__(self, position, w, h, d):
        self._pos = position
        self._wbase = (0.5 * w, -0.5 * w)
        self._hbase = (0.5 * h, -0.5 * h)
        self._dbase = (0.5 * d, -0.5 * d)
        self._ones = (1,)
        self._dim = (w, h, d)

    def render(self, cam, light, screen_w, screen_h, **kwargs):
        v_wld = self.calc_vertices()

        for p1, p2, l in HBox.LINES:
            fl = FracLine(v_wld[p1], v_wld[p2], int(self._dim[l]))
            for f in fl.render(cam, light, screen_w, screen_h, **kwargs):
                yield f

    def calc_vertices(self):
        v_wld = list()
        for v in product(self._wbase, self._hbase, self._dbase, self._ones):
            v_rw = np.dot(self._pos.tf(), np.array(v))
            v_wld.append(VecUtil.project(v_rw))
        return v_wld


class Cube(Renderable):
    SIDES = ((0, 2, 3, 1, 'EAST'),
             (5, 7, 6, 4, 'WEST'),
             (0, 1, 5, 4, 'UP'),
             (6, 7, 3, 2, 'DOWN'),
             (4, 6, 2, 0, 'NORTH'),
             (1, 3, 7, 5, 'SOUTH'))
    H_PI = 0.5 * np.pi

    def __init__(self, position, length, color):
        self._pos = position
        self._len = length
        self._color = color
        self._base = (0.5 * self._len, -0.5 * self._len)
        self._ones = (1,)

    def render(self, cam, light, screen_w, screen_h, **kwargs):
        cx, cy = 0.5 * screen_w, 0.5 * screen_h
        v_wld, v_cam, v_img = self.calc_vertices(cam, cx, cy)

        for p1, p2, p3, p4, side in Cube.SIDES:
            render = kwargs.get(side, True)
            if not render:
                continue

            # polygon behind camera
            if min(v_cam[p1][2], v_cam[p2][2], v_cam[p3][2], v_cam[p4][2]) < 0.2:
                continue

            # polygon is outside of frame borders
            img_cord = v_img[p1], v_img[p2], v_img[p3], v_img[p4]

            img_x = [x for x, y in img_cord]
            if max(img_x) < 0 or min(img_x) >= screen_w:
                continue
            img_y = [y for x, y in img_cord]
            if max(img_y) < 0 or min(img_y) >= screen_h:
                continue

            # cube face is not visible
            mid_cam = (v_cam[p1] + v_cam[p3]) * 0.5
            nrm_cam = VecUtil.norm(v_cam[p1], v_cam[p2], v_cam[p3])
            len_ray = VecUtil.l2(mid_cam)
            nrm_ray = mid_cam / len_ray
            cosa = np.dot(nrm_cam, nrm_ray)
            theta = np.arccos(cosa)
            if abs(theta) <= Cube.H_PI:
                continue

            # get color
            mid_wld = (v_wld[p1] + v_wld[p3]) * 0.5
            nrm_wld = VecUtil.norm(v_wld[p1], v_wld[p2], v_wld[p3])
            shadow = kwargs.get("S" + side, 1.0)
            fact = light.position2factor(mid_wld, nrm_wld) * shadow
            color = self._color.toHTML(fact)

            yield Polygon(img_cord, len_ray, color)

    def calc_vertices(self, cam, cx, cy):
        v_wld, v_cam, v_img = list(), list(), list()
        for v in product(self._base, self._base, self._base, self._ones):
            v_rw = np.dot(self._pos.tf(), np.array(v))
            v_wld.append(VecUtil.project(v_rw))
            v_ex = cam.extrinsic_tf(v_rw)
            v_cam.append(v_ex)
            v_in = cam.intrinsic_tf(v_ex)
            v_sc = cx + v_in[0], cy - v_in[1]
            v_img.append(v_sc)
        return v_wld, v_cam, v_img

    def set_position(self, X, Y, Z, y, p, r):
        self._pos.set_position(X, Y, Z, y, p, r)

    def move(self, dX, dY, dZ, dy, dp, dr):
        self._pos.move(dX, dY, dZ, dy, dp, dr)


class Surface(Renderable):
    def __init__(self, position, w, h, color):
        self._pos = position
        self._color = color
        hw, hh = 0.5 * w, 0.5 * h
        self._raw_pt = [(hw, 0.0, -hh, 1.0),
                        (hw, 0.0, hh, 1.0),
                        (-hw, 0.0, hh, 1.0),
                        (-hw, 0.0, -hh, 1.0)]

    def render(self, cam, light, screen_w, screen_h, **kwargs):
        wld_pt4 = [np.dot(self._pos.tf(), pt) for pt in self._raw_pt]
        wld_pt3 = [VecUtil.project(pt) for pt in wld_pt4]
        ext_pt = [cam.extrinsic_tf(pt) for pt in wld_pt4]

        if min(map(lambda p: p[2], ext_pt)) < 0.1:
            return []

        int_pt = [cam.intrinsic_tf(pt) for pt in ext_pt]
        cx, cy = 0.5 * screen_w, 0.5 * screen_h
        img_pt = [(cx + x, cy - y) for x, y in int_pt]
        mid_cam = 0.5 * (ext_pt[0] + ext_pt[2])
        Z = VecUtil.l2(mid_cam)
        mid_wld = 0.5 * (wld_pt3[0] + wld_pt3[2])
        nrm_wld = VecUtil.norm(wld_pt3[0], wld_pt3[1], wld_pt3[2])
        shadow = kwargs.get("S", 1.0)
        fact = light.position2factor(mid_wld, nrm_wld) * shadow
        color = self._color.toHTML(fact)
        return [Polygon(img_pt, Z, color)]


class Light:
    MID_RANGE = 15

    def __init__(self, intensity, position):
        self._int = intensity
        self._loc = position.location_vec()
        self._norm = Light.euler2unit(position)

    @staticmethod
    def euler2unit(pos):
        rt = pos.tf()[0:3, 0:3]
        v = np.array((0.0, 0.0, 1.0))
        u = np.dot(rt, v)
        return u

    def position2factor(self, location, norm):
        d = VecUtil.l2(self._loc, location)
        i = Light.MID_RANGE / (d ** (2.0 * (1.0 - self._int)))
        cost = np.dot(self._norm, norm)
        t = np.arccos(cost)
        return i * t / np.pi


class Engine:
    def __init__(self, canvas):
        self._canvas = canvas
        self._cam = Cam(1000, Position(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        self._light = Light(0.5, Position(0.0, 2.0, -6.0, 0.0, np.pi * -0.1, 0.0))
        self._polygons = list()
        self._gui = list()

    def render(self, item, **kwargs):
        screen_w, screen_h = self._canvas.winfo_width(), self._canvas.winfo_height()
        for p in item.render(self._cam, self._light, screen_w, screen_h, **kwargs):
            self._polygons.append(p)

    def render_gui(self, item):
        self._gui.append(item)

    def draw(self):
        self._canvas.delete(tkinter.ALL)
        self._polygons.sort(key=lambda p: p.Z(), reverse=True)
        for p in self._polygons:
            p.draw(self._canvas)
        for g in self._gui:
            g.draw(self._canvas)
        self._polygons.clear()
        self._gui.clear()

    def set_cam(self, X, Y, Z, y, p, r):
        self._cam.set_position(X, Y, Z, y, p, r)

    def move_cam(self, dX, dY, dZ, dy, dp, dr):
        self._cam.move(dX, dY, dZ, dy, dp, dr)

    def move_cam_relative(self, dX, dY, dZ):
        v = np.array((dX, dY, dZ))
        tf = self._cam.tf_mat()
        rt = tf[0:3, 0:3]
        v_rt = np.dot(rt, v)
        self._cam.move(v_rt[0], v_rt[1], v_rt[2], 0.0, 0.0, 0.0)