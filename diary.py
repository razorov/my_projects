import flet as ft
import pandas as pd


class Day(ft.Column):
    flower = None
    edit = False
    id = 0
    memory = {}
    mem = {}
    name_day = ['Event', 'Routine', 'Self_dev', 'Relax', 'None', 'None']

    def __init__(self, number=None):
        super().__init__()

        # id
        self.id += 1
        Day.id += 1

        # day circle
        self.btn = ft.IconButton(
            ft.icons.CIRCLE,
            on_click=self.color_controls,
            icon_color='white',
            icon_size=25,
            padding=0,
            width=25,
            height=25,
            tooltip=number,
        )

        # save and load
        self.save = ft.IconButton(
            ft.icons.DOWNLOAD_OUTLINED,
            icon_color='white',
            icon_size=30,
            padding=0,
            width=30,
            height=30,
            tooltip='save',
            on_click=Day.__memory_save
        )

        #
        self.load = ft.IconButton(
            ft.icons.UPLOAD_OUTLINED,
            icon_color='white',
            icon_size=30,
            padding=0,
            width=30,
            height=30,
            tooltip='load',
            on_click=self.__memory_load
        )

        # main save and load
        self.save_and_load = ft.Row(
            [
                self.save,
                ft.Text('', width=20),
                self.load
            ], width=200, alignment=ft.MainAxisAlignment.CENTER
        )

        # change day name
        self.change_name = ft.TextField(
            width=100,
            bgcolor='black',
            color='white',
            height=45,
            text_size=14
        )

        # change day icon
        self.change_name_accept = ft.IconButton(ft.icons.APPROVAL, icon_color='white', on_click=self.__set_name)

        # main change day
        self.main_change_name = ft.Row(
            [
                self.change_name,
                self.change_name_accept
            ], alignment=ft.MainAxisAlignment.CENTER, visible=False
        )

        # circle list for paint
        self.circle_list = ft.Column(
            [
                self.__circle_paint('orange', 'Event', 0),
                self.__circle_paint('blue', 'Routine', 1),
                self.__circle_paint('purple', 'Self_dev', 2),
                self.__circle_paint('pink', 'Relax', 3),
                self.__circle_paint('red', 'None', 4),
                self.__circle_paint('green', 'None', 5),
            ]
        )

        # main paint table
        self.paint = ft.Column(
            [
                ft.Row([ft.Text('', height=0.5)]),  # unvisible field
                ft.Row([ft.Text('paint', color='white', size=20, height=25)],
                       alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([ft.Text('', height=0.5)]),  # unvisible field
                self.circle_list,
                ft.Row([ft.Text('', height=50)]),  # unvisible field
                self.save_and_load,
                self.main_change_name
            ]
        )

        # main controls
        self.controls = [self.btn]

        # memory
        Day.__memory(self)

    # change the color
    def color_controls(self, e):
        if Day().edit is True:

            if self.btn.icon_color == 'white':
                self.btn.icon_color = Day().flower
                Day.__memory_update(self)

            else:
                self.btn.icon_color = 'white'
                Day.__memory_update(self)

            self.update()

    # creating circle
    def __circle_paint(self, color, dis, id_edit):
        icon = ft.IconButton(
            icon=ft.icons.CIRCLE,
            icon_size=30,
            icon_color=f'{color}',
            padding=0,
            width=30,
            height=30,
            on_click=self.__color_set

        )

        #
        edit = ft.IconButton(
            icon=ft.icons.EDIT,
            icon_size=25,
            icon_color="white60",
            padding=0,
            width=25,
            height=25,
            on_click=self.__name_set,
            key=id_edit

        )

        #
        text = ft.Text(f'{dis}', size=16, color='white', width=90)
        return ft.Row(
            [
                icon,
                ft.Text('->', size=16, color='white'),
                text,
                edit,
            ]
        )

    # name set
    def __name_set(self, e):
        number = e.control.key
        self.main_change_name.visible = True
        self.main_change_name.data = number
        self.change_name.value = Day.name_day[number]
        self.main_change_name.update()

    #
    def __set_name(self, e):
        number = self.main_change_name.data
        name = self.change_name.value

        self.main_change_name.visible = False
        self.main_change_name.data = None
        self.change_name.value = None

        Day.name_day[number] = name
        self.__name_update()

    #
    def __name_update(self):
        for index, value in enumerate(Day.name_day):
            self.circle_list.controls[index].controls[2].value = value

        self.circle_list.update()
        self.paint.update()

    # color choice
    def __color_set(self, e):
        default_circle = ft.icons.CIRCLE
        change_circle = ft.icons.CIRCLE_OUTLINED
        print(Day().edit)

        if e.control.icon_color == Day().flower:
            e.control.icon = default_circle
            Day().__set_color(None)
            Day().__set_edit(False)
            self.circle_list.update()

        else:
            Day().__set_edit(True)
            print(Day().edit)

            for i in self.circle_list.controls:
                i.controls[0].icon = default_circle

            e.control.icon = change_circle
            color = e.control.icon_color
            Day().__set_color(color)
            self.circle_list.update()

    #
    @classmethod
    def __set_color(cls, color):
        cls.flower = color

    #
    @classmethod
    def __set_edit(cls, edit):
        cls.edit = edit

    # memory
    @classmethod
    def __memory(cls, self):
        cls.mem[self.id] = self
        cls.memory[self.id] = self.btn.icon_color
        if self.id == 360:
            print(cls.memory)

    #
    @classmethod
    def __memory_update(cls, self):
        cls.memory[self.id] = self.btn.icon_color

    #
    @classmethod
    def __memory_save(cls, e):

        # day data paint
        data = pd.DataFrame(cls.memory.items(), columns=('key', 'value'))
        data.to_json(f"test", index=False)

        # name of paint
        paint = pd.DataFrame(cls.name_day)
        paint.to_json(f"test_paint", index=False)

    #
    def __memory_load(self, e):
        data = pd.read_json('test')
        for i, color in data.values:
            if i <= 365:
                Day.mem[i].btn.icon_color = color
                Day.memory[i] = color
                Day.mem[i].update()

        paint = pd.read_json('test_paint')
        for index, name in enumerate(paint.values):
            Day.name_day[index] = name[0]

        self.__name_update()


class Month(ft.Column):
    def __init__(self, name, last_week):
        super().__init__()
        self.name_month = name

        # week
        self.first = ft.Row([Day(1), Day(2), Day(3), Day(4), Day(5), Day(6), Day(7)])
        self.second = ft.Row([Day(8), Day(9), Day(10), Day(11), Day(12), Day(13), Day(14)])
        self.third = ft.Row([Day(15), Day(16), Day(17), Day(18), Day(19), Day(20), Day(21)])
        self.four = ft.Row([Day(22), Day(23), Day(24), Day(25), Day(26), Day(27), Day(28)])

        #
        self.weeks = ft.Column(
            [
                self.first,
                self.second,
                self.third,
                self.four,
                ft.Row([Day(29 + x) for x in range(last_week)])
            ]
        )

        # month
        self.month = ft.Container(
            width=255,
            height=230,
            bgcolor='black',
            border_radius=30,
            content=ft.Column(
                [
                    ft.Row([ft.Text('', height=0.5)]),
                    ft.Row([ft.Text(f'{self.name_month}', size=20, color='white', height=25)
                            ], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([self.weeks], alignment=ft.MainAxisAlignment.CENTER)
                ]
            )
        )

        # main controls
        self.controls = [self.month]


class Calendar(ft.Column):
    def __init__(self, back_to_menu):
        super().__init__()
        self.back_to_menu = back_to_menu

        # year
        self.year = ft.Column(
            [
                ft.Row(
                    [
                        Month('january', 3),
                        Month('february', 0),
                        Month('march', 3),
                        Month('aprile', 2),
                    ]
                ),
                ft.Row(
                    [
                        Month('may', 3),
                        Month('june', 2),
                        Month('july', 3),
                        Month('august', 3),
                    ]
                ),
                ft.Row(
                    [
                        Month('september', 2),
                        Month('october', 3),
                        Month('november', 2),
                        Month('december', 3),
                    ]
                )
            ]
        )

        # table for year
        self.table_year = ft.Container(
            width=1050,
            height=710,
            bgcolor='red',
            content=self.year
        )

        # table for paint-check
        self.table_paint = ft.Container(
            width=200,
            height=710,
            bgcolor='red',
            content=ft.Column(
                [
                    ft.Container(
                        width=220,
                        height=470,
                        bgcolor='black',
                        border_radius=30,
                        content=Day().paint
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Container(
                                        width=170,
                                        height=70,
                                        bgcolor='black',
                                        border_radius=30,
                                        on_hover=self.animation_btn,
                                        on_click=self.back_to_menu,
                                        content=ft.Row([ft.Text('MENU', size=32, font_family='Futura', color='white')], alignment=ft.MainAxisAlignment.CENTER)
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER
                            )
                        ], alignment=ft.MainAxisAlignment.CENTER, height=220
                    )

                ]
            )
        )

        # window
        self.window = ft.Column(
            [
                ft.Row(
                    [
                        self.table_year,
                        self.table_paint,
                    ]
                )
            ]
        )

        # controls
        self.controls = [self.window]

    def animation_btn(self, e):

        if e.control.border_radius == 30:
            e.control.border_radius = 31
            e.control.width += 5
            e.control.height += 5
            e.control.content.controls[0].size += 2

        else:
            e.control.border_radius = 30
            e.control.width -= 5
            e.control.height -= 5
            e.control.content.controls[0].size -= 2

        self.update()


# main class Book
class Book(ft.Column):
    def __init__(self):
        super().__init__()

        # welcome text
        self.welcome_text = ft.Row(
                                    [
                                        ft.Text('IDiary', size=64, color='white', font_family='Futura')
                                    ], width=650, alignment=ft.MainAxisAlignment.CENTER
                                )
        # menu
        self.menu = ft.Column(
            [
                self.button_menu('Days', click=self.to_Days),
                self.button_menu('Plans'),
                self.button_menu('Events'),
                self.button_menu('Mind')
            ], alignment=ft.MainAxisAlignment.CENTER
        )

        # main window
        self.window = ft.Row(
            [
                ft.Container(
                    height=720,
                    width=300,
                    bgcolor='red'
                ),
                ft.Container(
                    height=720,
                    width=650,
                    bgcolor='red',
                    content=ft.Column(
                        [
                            ft.Container(
                                width=650,
                                height=100,
                                bgcolor='black',
                                border_radius=20,
                                content=self.welcome_text
                            ),
                            ft.Container(width=650, height=75),  # empty container
                            ft.Container(
                                width=650,
                                height=450,
                                bgcolor='yellow',
                                content=self.menu
                            )
                        ]
                    )

                ),
                ft.Container(
                    height=720,
                    width=300,
                    bgcolor='red'
                )
            ]
        )

        # pages
        self.calendar = Calendar(self.to_Menu)
        self.calendar.visible = False

        self.controls = [self.window, self.calendar]

    #
    def button_menu(self, text, click=None):
        text_row = ft.Row([
            ft.Text(f'{text}', size=48, color='white', font_family='Futura')
        ], alignment=ft.MainAxisAlignment.CENTER)

        return ft.Row(
            [
                ft.Container(
                    width=450,
                    height=100,
                    bgcolor='black',
                    border_radius=35,
                    content=text_row,
                    on_hover=self.animation_button_menu,
                    on_click=click
                )
            ], width=650, alignment=ft.MainAxisAlignment.CENTER
        )

    # animation_button
    def animation_button_menu(self, e):

        if e.control.border_radius == 35:
            e.control.border_radius = 36
            e.control.width += 5
            e.control.height += 5
            e.control.content.controls[0].size += 2

        else:
            e.control.border_radius = 35
            e.control.width -= 5
            e.control.height -= 5
            e.control.content.controls[0].size -= 2

        self.update()

    # click Days
    def to_Days(self, e):
        self.controls[0].visible = False
        self.controls[1].visible = True
        self.update()

    # back to menu
    def to_Menu(self, e):
        for i in self.controls:
            i.visible = False
        self.controls[0].visible = True
        self.update()


def start(page: ft.Page):
    page.title = 'Diary'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'
    page.window.width = 1280 + 20
    page.window.height = 720 + 50
    page.window.resizable = False

    app = Book()
    page.add(app)
    page.update()


ft.app(target=start)