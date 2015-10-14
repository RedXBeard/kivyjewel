__version__ = '1.0.0'

from kivy.app import App
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
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
    def on_transform_with_touch(self, touch):
        """take action when shape touched."""
        super(CustomScatter, self).on_transform_with_touch(touch)

        pre_x, pre_y = self.pre_pos
        touch_x, touch_y = self.pos

        if abs(pre_x - touch_x) > abs(pre_y - touch_y):
            if abs(pre_x - touch_x) > self.size[0] + 5:
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
                except IndexError:
                    pass
                self.pos = [touch_x, pre_y]

        else:
            if abs(pre_y - touch_y) > self.size[1] + 5:
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
        anim.start(self)

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)

    def get_neighbour(self, col, row):
        neighbour = None
        if (len(self.parent.cols_fill) > col >= 0 and
                len(self.parent.cols_fill[col]) > row >= 0):
            neighbour = self.parent.cols_fill[col][row]
        return neighbour

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

    def clear_bubble(self):
        bulk = []
        for i in range(0, len(COLOR)):
            same_colored = map(
                lambda x: filter(
                    lambda y: y.color_val == i, x), self.cols_fill)
            print map(
                lambda x: (x.col, x.row, x.children[0].text),
                reduce(lambda x, y: x + y, same_colored))
            break


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
                row.pos = (row.pre_pos[0], 500)
                tmp.append(row)
            self.fill_column(column=tmp)
        board.clear_bubble()

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
                label = Label(text=str(i), size_hint=(None, None), size=size)
                label.space = size[0] * 10 / 45
                color = choice(COLOR)
                color_index = COLOR.index(color)
                set_color(label, color)
                scatter.color_val = color_index
                scatter.add_widget(label)
                # board.add_widget(scatter)
                label_count += 1
                tmp.setdefault(col, [])
                tmp[col].append(scatter)
            for i in range(0, board.cols):
                board.cols_fill.append(tmp[i])
            self.fill_columns()
        else:
            label_count = (board.rows * board.cols) - 1
            for widget in board.children:
                col = (label_count / board.rows)
                row = (label_count % board.rows)
                pos = ((col * (size[0] + 5)) + padding,
                       (row * (size[0] + 5)) + 50)
                widget.size = size
                widget.pos = widget.pre_pos = pos
                for child in widget.children:
                    child.size = size
                    child.space = size[0] * 10 / 45
                label_count -= 1
                tmp.setdefault(col, [])
                tmp[col].append(widget)
            for i in range(0, board.cols):
                board.cols_fill.append(tmp[i])

    def resize_all(self, width, height):
        size = [
            min(width, height - (150 + 5 * self.board.cols)) /
            self.board.cols] * 2
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
