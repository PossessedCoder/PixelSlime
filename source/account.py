import pygame.font

from constants import Images, UserEvents
from exceptions import UserAlreadyExistsError
from utils import load_media, post_event, DataBase
from templates import Form, FormField, BaseSurface, Button, Freezer


class _BaseAuth(Form):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self.title_color = (209, 203, 203)
        self.background_color = (54, 53, 53)
        self.border_radius = 30
        self.border_width = 1
        self.border_color = (105, 105, 105)
        self.errors_color = (235, 64, 52)

        # label, secret
        fields_data = (('Логин', False), ('Пароль', True))

        for label, secret in fields_data:
            fld = FormField(self.get_rect().w - self.contents_margin_inline * 2, 35,
                            secret=secret, parent=self)
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
            self.add_field(fld)
        view = BaseSurface(-1, -1, *self.fields[0].get_rect().size)
        font = self.fields[0].get_font()
        font.bold = True
        submit_text = font.render('Продолжить', True, (255, 255, 255))
        view.blit(submit_text, rect=((view.get_rect().w - submit_text.get_width()) // 2,
                                     (view.get_rect().h - submit_text.get_height()) // 2, *submit_text.get_size()))
        submit_btn = Button(*view.get_rect(), parent=self)
        submit_btn.set_hovered_view(view, background_color=(102, 121, 213), border_radius=15)
        submit_btn.set_not_hovered_view(view, background_color=(85, 106, 208), border_radius=15)
        self.submit_button = submit_btn

    def validate(self):
        for fld in self.fields:
            fld.errors.clear()

        if not self.as_tuple()[0]:
            self.fields[0].errors.append('Это поле не может быть пустым')
        if not self.as_tuple()[1]:
            self.fields[1].errors.append('Это поле не может быть пустым')

        if not self.fields[0].errors and not self.fields[1].errors:
            return True

        return False

    def on_success(self):
        super().on_success()
        self.parent.on_form_success()


class _RegistrationForm(_BaseAuth):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self.title = 'Регистрация'

    def validate(self):
        v = super().validate()
        if not v:
            return False

        if len(self.as_tuple()[0]) < 6:
            self.fields[1].errors.append('Пароль слишком короткий')

        try:
            DataBase().create_user(*self.as_tuple())
            return True
        except UserAlreadyExistsError:
            self.fields[0].errors.append('Это имя занято')
            return False


class _AuthenticationForm(_BaseAuth):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)
        self.title = 'Авторизация'

    def validate(self):
        v = super().validate()

        if (uid := DataBase().get_uid(self.as_tuple()[0])) is None and self.as_tuple()[0]:
            self.fields[0].errors.append('Пользователь с таким именем не найден')
            return False

        if not v:
            return False

        if not DataBase().is_correct_password(uid, self.as_tuple()[1]):
            self.fields[1].errors.append('Неверный пароль')
            return False

        return True


class AuthTabs(BaseSurface, Freezer):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self.freeze()

        self._switch_tab_button_text_font_size = 14
        self._switch_tab_button_texts = ('Еще нет аккаунта? Зарегистрироваться', 'Уже есть аккаунт? Авторизироваться')
        rect = (0, 0, w, h - self._switch_tab_button_text_font_size - 3)
        self._tabs = [_AuthenticationForm(*rect, parent=self), _RegistrationForm(*rect, parent=self)]
        self._current_tab = self._tabs[0]
        self._switch_tab_button_text = self._switch_tab_button_texts[0]

    @property
    def current_tab(self):
        return self._current_tab

    def _switch_tab(self):
        try:
            idx = 0 if self._tabs.index(self._current_tab) == 1 else 1
        except ValueError:
            idx = 0

        self._current_tab = self._tabs[idx]
        self._switch_tab_button_text = self._switch_tab_button_texts[idx]

    def draw(self):
        self.fill((255, 255, 255, 0))

        font = pygame.font.SysFont('arial', self._switch_tab_button_text_font_size)
        hovered_text = font.render(self._switch_tab_button_text, True, (197, 197, 197))
        not_hovered_text = font.render(self._switch_tab_button_text, True, (172, 172, 172))

        btn_switch = Button(self.get_rect().w // 2 - not_hovered_text.get_width() // 2, self._current_tab.get_rect().h,
                            *not_hovered_text.get_size(), parent=self)
        btn_switch.set_hovered_view(hovered_text)
        btn_switch.set_not_hovered_view(not_hovered_text)
        btn_switch.bind_press(self._switch_tab)

        self._current_tab.handle()
        self.blit(self._current_tab)
        btn_switch.handle()
        self.blit(btn_switch)

    def on_form_success(self):
        self.__del__()
        post_event(UserEvents.UNFREEZE_CWW, freezer=self)
        post_event(UserEvents.START_SESSION, uid=DataBase().get_uid(self._current_tab.as_tuple()[0]))
