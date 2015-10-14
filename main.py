__version__ = '1.0.0'

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.properties import NumericProperty
from kivy.uix.label import Label
from kivy.uix.scatter import Scatter
from kivy.uix.floatlayout import FloatLayout

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


class Board(FloatLayout):
    cols = NumericProperty(0)
    rows = NumericProperty(0)


class KivyJewel(GridLayout):
    score = NumericProperty(0)

    def __init__(self, *args, **kwargs):
        super(KivyJewel, self).__init__(*args, **kwargs)

    def prepare_board(self, size, padding):
        board = self.board
        if not board.children:
            label_count = 0
            for i in range(0, board.rows * board.cols):
                pos = (((label_count / board.rows) * (size[0] + 5)) + padding,
                       ((label_count % board.rows) * (size[0] + 5)) + 5)
                scatter = Scatter(
                    size=size, size_hint=(None, None), pos=pos)
                label = Label(text=str(""), size_hint=(None, None), size=size)
                set_color(label, choice(COLOR))
                scatter.add_widget(label)
                board.add_widget(scatter)
                label_count += 1
        else:
            label_count = (board.rows * board.cols) - 1
            for widget in board.children:
                pos = (((label_count / board.rows) * (size[0] + 5)) + padding,
                       ((label_count % board.rows) * (size[0] + 5)) + 5)
                widget.size = size
                widget.pos = pos
                for child in widget.children:
                    child.size = size
                label_count -= 1

    def resize_all(self, width, height):
        size = [
            min(width, height - (105 + 5 * self.board.cols)) /
            self.board.cols] * 2
        padding = (
            width - (size[0] * self.board.cols + 5 * self.board.cols)) / 2
        self.board.padding = padding
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
