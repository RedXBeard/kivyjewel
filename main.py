__version__ = '1.0.0'

from kivy.app import App
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter

from random import choice

COLOR = [
    get_color_from_hex('D15F21'),  # Orange
    get_color_from_hex('0C4DA7'),  # Blue
    get_color_from_hex('C32D2C'),  # Red
    get_color_from_hex('C731C4'),  # Purple
    get_color_from_hex('089C00'),  # Green
    get_color_from_hex('9C9425'),  # Yellow
    get_color_from_hex('828677'),  # Grey
]
COLOR = map(lambda x: x[:3] + [.9], COLOR)


def get_color(obj):
    u"""Color of widget returns."""
    try:
        obj_color = filter(
            lambda x:
                str(x).find('Color') != -1, obj.canvas.before.children)[0]
    except IndexError:
        obj_color = None
    return obj_color


def set_color(obj, color):
    obj_color = get_color(obj)
    try:
        obj_color.rgba = color
    except AttributeError:
        pass


class CustomScatter(Scatter):

    def __unicode__(self):
        return "%s-%s -> %s" % (self.col, self.row, self.color_val)

    def on_transform_with_touch(self, touch):
        """take action when shape touched."""
        super(CustomScatter, self).on_transform_with_touch(touch)

        pre_x, pre_y = self.pre_pos
        touch_x, touch_y = self.pos

        if abs(pre_x - touch_x) > abs(pre_y - touch_y):
            if abs(pre_x - touch_x) > self.size[0] + 5:
                self.reset_board(touch)
            elif ((self.col == 0 and pre_x - touch_x > 0) or
                  (self.parent and
                   self.col == self.parent.cols - 1 and
                   pre_x - touch_x < 0)):
                self.reset_board(touch)
            else:
                try:
                    if touch_x > pre_x:
                        neighbour = self.parent.cols_fill[self.col + 1][self.row]
                        neighbour.pos = [(neighbour.pre_pos[0] -
                                          abs(pre_x - touch_x)),
                                         neighbour.pre_pos[1]]
                    else:
                        if self.col - 1 < 0:
                            raise IndexError
                        neighbour = self.parent.cols_fill[self.col - 1][self.row]
                        neighbour.pos = [(neighbour.pre_pos[0] +
                                          abs(pre_x - touch_x)),
                                         neighbour.pre_pos[1]]

                    if (abs(int(neighbour.pos[0]) - int(self.pos[0])) >
                            self.size[0] / 2):
                        self.swap(neighbour)
                        lines = self.get_line() + neighbour.get_line()
                        columns = self.get_column() + neighbour.get_column()
                        if not self.parent.check_bubbles(
                                lines=lines, columns=columns, check=True):
                            self.swap(neighbour)
                        self.reset_board(touch)
                except IndexError:
                    pass
                self.pos = [touch_x, pre_y]

        else:
            if abs(pre_y - touch_y) > self.size[1] + 5:
                self.reset_board(touch)
            elif ((self.row == 0 and pre_y - touch_y > 0) or
                  (self.row == self.parent.rows - 1 and
                   pre_y - touch_y < 0)):
                self.reset_board(touch)
            else:
                try:
                    if touch_y > pre_y:
                        neighbour = self.parent.cols_fill[self.col][self.row + 1]
                        neighbour.pos = [neighbour.pre_pos[0],
                                         (neighbour.pre_pos[1] -
                                          abs(pre_y - touch_y))]
                    else:
                        neighbour = self.parent.cols_fill[self.col][self.row - 1]
                        neighbour.pos = [neighbour.pre_pos[0],
                                         (neighbour.pre_pos[1] +
                                          abs(pre_y - touch_y))]

                    if (abs(int(neighbour.pos[1]) - int(self.pos[1])) >
                            self.size[1] / 2):
                        self.swap(neighbour)
                        lines = self.get_line() + neighbour.get_line()
                        columns = self.get_column() + neighbour.get_column()
                        if not self.parent.check_bubbles(
                                lines=lines, columns=columns, check=True):
                            self.swap(neighbour)
                        self.reset_board(touch)
                except IndexError:
                    pass
                self.pos = [pre_x, touch_y]

    def on_bring_to_front(self, touch):
        super(CustomScatter, self).on_bring_to_front(touch)

    def on_touch_up(self, touch):
        super(CustomScatter, self).on_touch_up(touch)
        anim = Animation(
            x=self.pre_pos[0], y=self.pre_pos[1],
            t='linear', duration=.2)
        parent = self.parent
        if parent:
            anim.fbind('on_complete', parent.check_bubbles, [], [], False)
        anim.start(self)

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)

    def swap(self, neighbour):
        neighbour_col = neighbour.col
        neighbour_row = neighbour.row
        neighbour_pre_pos = neighbour.pre_pos
        neighbour.col = self.col
        neighbour.row = self.row
        neighbour.pre_pos = self.pre_pos
        self.col = neighbour_col
        self.row = neighbour_row
        self.pre_pos = neighbour_pre_pos
        board = self.parent
        board.cols_fill[self.col][self.row] = self
        board.cols_fill[neighbour.col][neighbour.row] = neighbour

    def get_neighbour(self, col, row):
        neighbour = None
        if (len(self.parent.cols_fill) > col >= 0 and
                len(self.parent.cols_fill[col]) > row >= 0):
            neighbour = self.parent.cols_fill[col][row]
        return neighbour

    def get_line(self):
        line = []
        for col in self.parent.cols_fill:
            line.append(col[self.row])
        return line

    def get_column(self):
        return self.parent.cols_fill[self.col]

    def reset_board(self, touch):
        neighbours = [self,
                      self.get_neighbour(self.col + 1, self.row),
                      self.get_neighbour(self.col - 1, self.row),
                      self.get_neighbour(self.col, self.row + 1),
                      self.get_neighbour(self.col, self.row - 1)]
        for neighbour in neighbours:
            if neighbour:
                neighbour.on_touch_up(touch)


class Board(FloatLayout):
    cols = NumericProperty(0)
    rows = NumericProperty(0)
    cols_fill = ListProperty([])

    def check_bubbles(self, lines=[], columns=[], check=False, *args, **kwargs):
        bulk = []
        for i in range(0, len(COLOR)):
            if not lines and not columns:
                same_colored = list(set(reduce(lambda x, y: x + y, (map(
                    lambda x: filter(
                        lambda y: (y.color_val == i and
                                   not y.cleared), x), self.cols_fill)))))
            else:
                same_colored = list(set(filter(
                    lambda y: (y.color_val == i and
                               not y.cleared), lines + columns)))

            for point in same_colored:
                same_column = filter(
                    lambda x: x.col == point.col, same_colored)
                same_row = filter(
                    lambda x: x.row == point.row, same_colored)
                if len(same_column) > 2:
                    ordered = sorted(same_column, key=lambda x: x.row)
                    i = 0
                    while i < len(ordered):
                        possible_points = ordered[i:i + 3]
                        if len(possible_points) > 2:
                            start_point = possible_points[0]
                            points = map(lambda x: x.row, possible_points)
                            if not bool(set(range(
                                    start_point.row,
                                    start_point.row + 3)).difference(
                                        set(points))):
                                bulk.extend(possible_points)
                        else:
                            break
                        i += 1

                if len(same_row) > 2:
                    ordered = sorted(same_row, key=lambda x: x.col)
                    i = 0
                    while i < len(ordered):
                        possible_points = ordered[i:i + 3]
                        if len(possible_points) > 2:
                            start_point = possible_points[0]
                            points = map(lambda x: x.col, possible_points)
                            if not bool(set(range(
                                    start_point.col,
                                    start_point.col + 3)).difference(
                                        set(points))):
                                bulk.extend(possible_points)
                        else:
                            break
                        i += 1
        if check:
            return bool(bulk)
        else:
            self.clear_bubbles(bulk)

    def swift(self, *args, **kwargs):
        columns = kwargs.get('columns', [])
        index = kwargs.get('index', 0)
        for column in columns:
            # try:
            #     column = columns[index]
            # except IndexError:
            #     return
            selected_column = self.cols_fill[column]
            bombed_rows = filter(
                lambda x: x.cleared, selected_column
            )
            for bombed in bombed_rows:
                self.remove_widget(bombed)

            if bombed_rows:
                self.parent.score += (10 * len(bombed_rows) +
                                      ((len(bombed_rows) - 1) * 5))
            filled_rows = sorted(
                filter(
                    lambda x: not x.cleared, selected_column),
                key=lambda x: x.row
            )

            new_scatters = []
            for bombed in bombed_rows:
                scatter = CustomScatter(
                    size=bombed.size, size_hint=(None, None),
                    pos=(bombed.pos[0], self.upcoming + 100))
                scatter.row = 10
                scatter.col = column
                scatter.pre_pos = (0, 0)
                label = Label(size_hint=(None, None), size=bombed.size)
                label.space = bombed.size[0] * 10 / 45
                color = choice(COLOR)
                color_index = COLOR.index(color)
                set_color(label, color)
                scatter.color_val = color_index
                scatter.cleared = False
                scatter.add_widget(label)
                scatter.is_new = True
                new_scatters.append(scatter)

            if new_scatters:
                filled_rows.extend(new_scatters)
                pre_posses = map(lambda x: x.pre_pos, selected_column)

                for scatter in filled_rows:
                    scatter.row = filled_rows.index(scatter)
                    scatter.pre_pos = pre_posses[scatter.row]
                    if not scatter.parent:
                        self.add_widget(scatter)
                    selected_column[scatter.row] = scatter
                # for scatter in filled_rows:
                #     Animation.stop_all(scatter)
                #     anim = Animation(y=scatter.pre_pos[1], t='linear', duration=.1)
                #     anim.fbind(
                #         'on_complete', self.swift, columns=columns,
                #         index=index + 1)
                #     anim.start(scatter)
                self.change_pos(column=selected_column)

    def change_pos(self, *args, **kwargs):
        column = kwargs.get('column', [])
        index = kwargs.get('index', 0)
        try:
            scatter = column[index]
        except IndexError:
            # self.check_bubbles()
            # if columns:
            #     self.swift(columns=columns, index=col_index)
            return
        anim = Animation(y=scatter.pre_pos[1], t='linear', duration=.05)
        anim.fbind(
            'on_complete', self.change_pos, column=column, index=index + 1)
        anim.start(scatter)

    def clear_bubbles(self, bulk):
        # if Animation._instances:
        def check_animation():
            flag = False
            for anim in Animation._instances:
                if (anim._widgets and anim._widgets.values() and
                        anim._widgets.values()[0].get(
                        'widget', '').__class__ == CustomScatter().__class__):
                    flag = True
                    break
            return flag

        # if check_animation():
        #     Clock.schedule_once(lambda dt: self.clear_bubbles(bulk), .2)
        #     return
        bulk = set(bulk)
        cols = set([])
        for scatter in bulk:
            Animation.stop_all(scatter)
            scatter.cleared = True
            cols.add(scatter.col)
            # set_color(scatter.children[0], get_color_from_hex('303030'))
        if cols:
            self.swift(columns=list(cols))


class KivyJewel(GridLayout):
    score = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(KivyJewel, self).__init__(*args, **kwargs)

    def fill_column(self, *args, **kwargs):
        column = kwargs.get('column')
        index = kwargs.get('index', 0)
        board = self.board
        try:
            row = column[index]
        except IndexError:
            board.check_bubbles()
            return
        board.add_widget(row)
        anim = Animation(
            x=row.pre_pos[0], y=row.pre_pos[1],
            t='linear', duration=.1)
        anim.fbind('on_complete', self.fill_column, column=column, index=index + 1)
        anim.start(row)

    def fill_columns(self):
        board = self.board
        for col in board.cols_fill:
            tmp = []
            for row in col:
                row.pos = (row.pre_pos[0], board.upcoming)
                tmp.append(row)
            self.fill_column(column=tmp)

    def prepare_board(self, size, padding):
        board = self.board
        board.coll_fill = []
        tmp = {}
        if not board.children:
            label_count = 0
            for i in range(0, board.rows * board.cols):
                col = (label_count / board.rows)
                row = (label_count % board.rows)
                pos = ((col * (size[0] + 5)) + padding,
                       (row * (size[0] + 5)) + 50)
                scatter = CustomScatter(
                    size=size, size_hint=(None, None), pos=pos)
                scatter.row = row
                scatter.col = col
                scatter.pre_pos = pos
                label = Label(text=str(""), size_hint=(None, None), size=size)
                label.space = size[0] * 10 / 45
                color = choice(COLOR)
                color_index = COLOR.index(color)
                set_color(label, color)
                scatter.color_val = color_index
                scatter.cleared = False
                # label.text = str(color_index)
                scatter.add_widget(label)
                # board.add_widget(scatter)
                label_count += 1
                tmp.setdefault(col, [])
                tmp[col].append(scatter)
            for i in range(0, board.cols):
                board.cols_fill.append(tmp[i])
            self.fill_columns()
        else:
            for widget in board.children:
                col = widget.col
                row = widget.row
                pos = ((col * (size[0] + 5)) + padding,
                       (row * (size[0] + 5)) + 50)
                widget.size = size
                widget.pos = widget.pre_pos = pos
                for child in widget.children:
                    child.size = size
                    child.space = size[0] * 10 / 45
                tmp.setdefault(col, [])
                tmp[col].append(widget)

    def resize_all(self, width, height):

        size = [
            min(width, height - (150 + 5 * self.board.cols)) /
            self.board.cols] * 2
        self.board.upcoming = height - 100
        padding = (
            width - (size[0] * self.board.cols + 5 * self.board.cols)) / 2
        self.board.padding = (padding + 15, 50, padding, 50)
        self.prepare_board(size, padding)


class KivyJewelApp(App):
    def __init__(self, **kwargs):
        super(KivyJewelApp, self).__init__(**kwargs)
        Builder.load_file('assets/jewel.kv')
        self.title = 'Kivy Jewel'
        # self.icon = 'assets/images/cube.png'

    def build(self):
        game = KivyJewel()
        Window.bind(on_resize=self.resize)
        # Window.bind(on_close=self.save_board)
        game.resize_all(float(Window.width), float(Window.height))
        return game

    def resize(self, *args):
        window, width, height = args
        try:
            root = filter(
                lambda x:
                str(x).find('KivyJewel') != -1, window.children)[0]
            root.resize_all(float(root.width), float(root.height))
        except IndexError:
            pass

if __name__ == '__main__':
    # Config.set('kivy', 'desktop', 1)
    # Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    Window.clearcolor = get_color_from_hex('303030')
    KivyJewelApp().run()
