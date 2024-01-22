__all__ = (
    'AuthTabs',
)

import pygame

from constants import UserEvents
from utils import post_event, DataBase
from templates import BaseSurface, Button, Freezer, StyledForm


class _BaseAuth(StyledForm):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent, closeable=False)

        self.add_field(placeholder='Логин')
        self.add_field(placeholder='Пароль', secret=True)

    def validate(self):
        for fld in self.fields:
            fld.errors.clear()

        if not self.as_tuple()[0]:
            self.fields[0].errors.append('Не может быть пустым')
        if not self.as_tuple()[1]:
            self.fields[1].errors.append('Не может быть пустым')

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

        if len(self.as_tuple()[1]) < 6:
            self.fields[1].errors.append('Пароль слишком короткий')
            return False

        try:
            DataBase().create_user(*self.as_tuple())
            return True
        except OverflowError:
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
        self.unfreeze()
        post_event(UserEvents.START_SESSION, uid=DataBase().get_uid(self._current_tab.as_tuple()[0]))
