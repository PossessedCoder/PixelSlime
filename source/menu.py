from constants import Images
from editor import Editor
from templates import BaseWindow, Button, BaseSurface, Form, FormField
from utils import load_media
from levels import Levels


class Menu(BaseWindow):

    def __init__(self):
        super().__init__()

        self._auth_form = Form(5, 5, 350, 400, parent=self)
        self._auth_form.title = 'Войти в учетную запись'
        self._auth_form.title_color = (209, 203, 203)
        self._auth_form.background_color = (54, 53, 53)
        self._auth_form.border_radius = 30
        self._auth_form.border_width = 1
        self._auth_form.border_color = (105, 105, 105)
        self._auth_form.errors_color = (179, 9, 9)

        # label, secret
        fields_data = (('Логин', False), ('Пароль', True))

        for label, secret in fields_data:
            fld = FormField(self._auth_form.get_rect().w - self._auth_form.contents_margin_inline * 2, 35,
                            secret=secret, parent=self._auth_form)
            fld.placeholder_text = label
            if secret:
                fld.secret_view = load_media(Images.EYE)
            fld.set_focused_view(
                border_radius=8,
                border_color=(85, 106, 208),
                background_color=(54, 53, 53),
                text_color=(209, 203, 203),
                placeholder_color=(125, 125, 125)
            )
            fld.set_unfocused_view(
                border_radius=8,
                border_width=0,
                background_color=(38, 38, 39),
                text_color=(209, 203, 203),
                placeholder_color=(125, 125, 125)
            )
            fld.errors = ('Обязательное поле не заполнено', 'Некорректный тип данных')
            self._auth_form.add_field(fld)
        view = BaseSurface(-1, -1, *self._auth_form.fields[0].get_rect().size)
        font = self._auth_form.fields[0].get_font()
        font.bold = True
        submit_text = font.render('Войти', True, (255, 255, 255))
        view.blit(submit_text, rect=((view.get_rect().w - submit_text.get_width()) // 2,
                                     (view.get_rect().h - submit_text.get_height()) // 2, *submit_text.get_size()))
        submit_btn = Button(*view.get_rect(), parent=self._auth_form)
        submit_btn.set_hovered_view(view, background_color=(102, 121, 213), border_radius=15)
        submit_btn.set_not_hovered_view(view, background_color=(85, 106, 208), border_radius=15)
        self._auth_form.submit_button = submit_btn

        self._title_frames = load_media('title.gif')

        self._button_levels = Button(520, 400, 300, 200, parent=self)
        self._button_levels.set_hovered_view(load_media(Images.LEVELS_PREVIEW), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_levels.set_not_hovered_view(load_media(Images.LEVELS_PREVIEW), background_color=(78, 78, 78),
                                                 border_radius=25)
        self._button_editor = Button(1100, 400, 300, 200, parent=self)
        self._button_editor.set_hovered_view(load_media(Images.WRENCH), background_color=(69, 69, 69),
                                             border_radius=15, scale_x=1.03, scale_y=1.03)
        self._button_editor.set_not_hovered_view(load_media(Images.WRENCH), background_color=(78, 78, 78),
                                                 border_radius=25)
        self._button_editor.bind_press(lambda: Editor())
        self._button_levels.bind_press(lambda: Levels())

    def eventloop(self):
        self._button_editor.eventloop()
        self._button_levels.eventloop()

    def draw(self):
        self.fill((54, 57, 62))

        frame = next(self._title_frames)
        self.blit(frame, rect=frame.get_rect(center=(self.get_rect().centerx, 100)))

        self._button_levels.draw()
        self.blit(self._button_levels)
        self._button_editor.draw()
        self.blit(self._button_editor)
