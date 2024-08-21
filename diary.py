import flet as ft


class Day(ft.Column):
    flower = 'orange'
    edit = False

    def __init__(self, number=None):
        super().__init__()

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

        # paint
        self.paint = ft.Column(
            [
                ft.IconButton(ft.icons.DELETE, on_click=self.edit_change)
            ]
        )

        # main controls
        self.controls = [self.btn]

    def color_controls(self, e):
        if self.create is True:
            if self.btn.icon_color == 'white':
                self.btn.icon_color = 'orange'
                self.btn.disabled_color = 'orange'

            else:
                self.btn.icon_color = 'white'
                self.btn.disabled_color = 'orange'

            self.update()

    @classmethod
    def edit_change(cls, e):
        if cls.create is False:
            cls.create = True
        else:
            cls.create = False


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
                ft.Row([Day(29+x) for x in range(last_week)])
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
    def __init__(self):
        super().__init__()

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
                        Month('august',3),
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

        # window
        self.window = ft.Column(
            [
                ft.Row(
                    [
                        self.table_year,
                        ft.Container(
                            width=220,
                            height=710,
                            bgcolor='black',
                            content=ft.Column(
                                [
                                    ft.Container(
                                        width=220, height=230, bgcolor='yellow', border_radius=35
                                    ),
                                    ft.Container(
                                        width=220, height=230, bgcolor='blue', border_radius=35
                                    ),
                                    ft.Container(
                                        width=220, height=230, bgcolor='orange', border_radius=35
                                    )
                                ]
                            )
                        )
                    ]
                )
            ]
        )

        # controls
        self.controls = [self.window]


# main class Book
class Book(ft.Column):
    def __init__(self):
        super().__init__()

        # pages
        self.calendar = Calendar()

        self.controls = [self.calendar]

    def __del__(self):
        print(self.__dict__)


def start(page: ft.Page):
    page.title = 'Diary'
    page.vertical_alignment = 'center'
    page.horizontal_alignment = 'center'
    page.window.width = 1280+20
    page.window.height = 720+50
    page.window.resizable = False

    app = Book()
    page.add(app)
    page.update()


ft.app(target=start)