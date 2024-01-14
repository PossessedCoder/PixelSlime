from datetime import datetime, timedelta

import pygame

from constants import FPS, UserEvents, SCREEN_SIZE
from utils import catch_events, post_event


class BaseSurface(pygame.Surface):
    # Since BaseSurface class supports resizing, pygame.Surface.get_width(), pygame.Surface.get_height(),
    # pygame.Surface.get_size() methods return fake (initial) values, be careful with its usage. To get actual size of
    # any surface, use BaseSurface.get_rect() method

    def __init__(self, x, y, w, h, parent=None):
        # transparent surface (pygame.SRCALPHA). If surface is transformable, fill it with transparent rect (alpha=0)
        # on every update (e.g. self.fill(255, 255, 255, 0))
        super().__init__((w, h), pygame.SRCALPHA)

        self._rect = self.get_rect(topleft=(x, y))
        self._parent = parent
        self._background = pygame.Color((0, 0, 0))

    def handle(self):
        # this method should mainly be called to update a surface, but if you wish to ignore any of methods:
        # draw() or eventloop(), you can call them separately. classes which inherit BaseSurface recommended to override
        # draw() and/or eventloop() methods, but it's also available to override handle() if required

        self.draw()
        self.eventloop()

    def draw(self):
        return

    def eventloop(self):
        return

    @property
    def parent(self):
        return self._parent

    def get_rect(self, **kwargs):
        if kwargs:
            rect = super().get_rect(**kwargs)
            try:
                rect.w, rect.h = self._rect.size
            finally:
                return rect
        return self._rect.copy()

    def get_absolute_rect(self):
        x, y = 0, 0
        surface = self

        while hasattr(surface, 'parent') and surface.parent:
            try:
                addx, addy = surface.get_rect().topleft
                x += addx
                y += addy
            finally:
                surface = surface.parent

        return pygame.Rect(x, y, self._rect.w, self._rect.h)

    def fill(self, color, rect=None, special_flags=0):
        super().fill(color, rect, special_flags)
        self._background = pygame.Color(color)

    def get_background_color(self):
        return self._background

    # fake
    def move(self, x=..., y=...):
        if x != Ellipsis:
            self._rect.x = x
        if y != Ellipsis:
            self._rect.y = y

    # fake
    def resize(self, w=..., h=...):  # anchors to center (center of the new rect will have the same center)
        # This method just resizes the rect of the surface, not the surface itself.
        # Real resize happens in the blit() method, which scales a surface to its rect size
        center = self._rect.center
        if w != Ellipsis:
            self._rect.w = w
        if h != Ellipsis:
            self._rect.h = h
        self._rect.center = center

    def blit(self, source, rect=..., **kwargs):
        if rect == Ellipsis:
            try:
                rect = source.get_rect()
            except AttributeError:
                raise ValueError(
                    f'"rect" argument must be provided for classes which does not support "get_rect()" method '
                    f'(Could not get rect of "{source.__class__.__name__}" instance)'
                ) from None

        rect = pygame.Rect(*rect)

        if rect.size != source.get_size():  # if actual size != surface initial size
            source = pygame.transform.scale(source, rect.size)  # resize to actual size

        super().blit(source, rect, **kwargs)

    # can be ignored on "del obj", use "obj.__del__()" instead
    def __del__(self):
        try:
            self.resize(0, 0)
        except AttributeError:
            return
        self.__getattribute__ = lambda: (_ for _ in ()).throw(AttributeError, 'This object has been deleted')


class BaseWindow(BaseSurface):

    def __init__(self):
        super().__init__(0, 0, *SCREEN_SIZE)
        post_event(UserEvents.SET_CWW, window=self)


class _SupportsBorder(BaseSurface):  # border-style: solid;

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._border_color = None
        self._border_width = 0
        self._border_radius = 0

    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, value):
        self._border_color = pygame.Color(value)

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        self._border_width = value

    @property
    def border_radius(self):
        return self._border_radius

    @border_radius.setter
    def border_radius(self, value):
        self._border_radius = value

    def draw(self):
        border = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(border, (255, 255, 255), (0, 0, *self.get_size()), border_radius=self.border_radius)
        self.blit(border, pygame.Rect(0, 0, *self.get_size()), special_flags=pygame.BLEND_RGBA_MIN)
        if not self.border_color:
            return
        if self.border_width != 0:
            pygame.draw.rect(self, self.border_color, (0, 0, *self.get_size()), self.border_width, self.border_radius)


class _SupportsHover(_SupportsBorder):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._default_data = {
            'content': None,
            'scale_x': 1,
            'scale_y': 1,
            'border_color': None,
            'border_width': 0,
            'border_radius': 0,
            'background_color': None
        }

        self._hover_data = self._default_data.copy()
        self._no_hover_data = self._default_data.copy()

        self._hover_emit_state = None

    @property
    def hovered(self):
        if self._hover_emit_state is not None:
            return self._hover_emit_state
        return self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos())

    def emit_hover(self, state):
        self._hover_emit_state = state

    def remove_hover(self):
        self._hover_emit_state = None

    def get_params(self, hover, *keys):
        data = {}
        c = self._hover_data if hover else self._no_hover_data

        if not keys:
            return c.copy()

        for key in keys:
            if key not in c:
                keys = ', '.join(f'"{k}"' for k in c)
                raise KeyError(f'Unknown key "{key}", available keys: {keys}') from None
            data[key] = c[key]

        return data

    @staticmethod
    def _set_view(collection, *args, **kwargs):
        collection_copy = collection.copy()

        for kw in kwargs:
            collection[kw] = kwargs[kw]
            collection_copy.pop(kw)

        for k, v in zip(collection_copy, args):
            collection[k] = v

    def set_hovered_view(
            self,
            content,
            scale_x=1.0,
            scale_y=1.0,
            border_radius=0,
            border_color=None,
            border_width=0,
            background_color=None
    ):
        self._set_view(self._hover_data, content.copy(), scale_x,
                       scale_y, border_color, border_width, border_radius, background_color)

    def set_not_hovered_view(
            self,
            content,
            scale_x=1.0,
            scale_y=1.0,
            border_color=None,
            border_width=0,
            border_radius=0,
            background_color=None
    ):
        self._set_view(self._no_hover_data, content.copy(), scale_x, scale_y,
                       border_color, border_width, border_radius, background_color)

    def _draw(self, content, scale_x, scale_y, border_color, border_width, border_radius, background_color):
        self.fill((255, 255, 255, 0) if not background_color else background_color)
        self.resize(self.get_width() * scale_x, self.get_height() * scale_y)

        # draw on an initial surface (pygame.Surface) and then resize in BaseSurface blit() method
        self.blit(content, rect=pygame.Rect(0, 0, *self.get_size()))

        try:
            self.border_color = border_color
        except TypeError:  # invalid color
            pass
        self.border_width = border_width
        self.border_radius = border_radius
        super().draw()

    def draw(self):
        self._draw(**(self._hover_data if self.hovered else self._no_hover_data).copy())


class Button(_SupportsHover):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        # Left, Wheel, Right. Keep this order, it's used in draw()
        self._callbacks_press = {'L': (), 'W': (), 'R': ()}
        self._callbacks_hold = {'L': (), 'W': (), 'R': ()}
        self._callbacks_release = {'L': (), 'W': (), 'R': ()}

        self._held = []

    @staticmethod
    def _get_callbacks(collection, button):
        return collection.get(button, ())

    def get_press_callbacks(self, button):
        return self._get_callbacks(self._callbacks_press, button)

    def get_hold_callbacks(self, button):
        return self._get_callbacks(self._callbacks_hold, button)

    def get_release_callbacks(self, button):
        return self._get_callbacks(self._callbacks_release, button)

    @staticmethod
    def _set_callbacks(collection, button, *callbacks):
        if button not in collection:
            ValueError(
                'Literals equality check failed '
                f'(invalid value for "button": expected Literal["L", "W", "R"], got Literal["{button}"] instead)'
            )
        collection[button] = callbacks

    def emit_press(self, button):
        if button in self._held:
            return

        self._invoke(*self._callbacks_press[button])
        self._held.append(button)

    def emit_release(self, button):
        if button not in self._held:
            return

        self._invoke(*self._callbacks_release[button])
        self._held.remove(button)

    def bind_press(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_press, button, *callbacks)

    def bind_hold(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_hold, button, *callbacks)

    def bind_release(self, *callbacks, button='L'):
        self._set_callbacks(self._callbacks_release, button, *callbacks)

    @staticmethod
    def _invoke(*callbacks):
        for callback in callbacks:
            callback()

    def eventloop(self):
        for event in catch_events(False):
            try:
                button = tuple(self._callbacks_press.keys())[event.button - 1]
            except (IndexError, AttributeError):
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()):
                self.emit_press(button)
            if event.type == pygame.MOUSEBUTTONUP:
                self.emit_release(button)
        for hb in self._held:
            self._invoke(*self._callbacks_hold[hb])


class Panel(BaseSurface):

    def __init__(self, minimized_rect, maximized_rect, resize_time=0.0, parent=None):
        super().__init__(*minimized_rect, parent)

        self._minimized_rect = pygame.Rect(*minimized_rect)
        self._maximized_rect = pygame.Rect(*maximized_rect)

        self._additions = tuple(
            (param_maximized - param_minimized) / (resize_time * FPS if resize_time != 0 else 1)
            for param_maximized, param_minimized in zip(self._maximized_rect, self._minimized_rect)
        )

        self._show_till = datetime.now()

    def maximize(self, duration=float('inf')):
        self._show_till = datetime.now() + timedelta(seconds=duration) if duration != float('inf') else datetime.max

    def minimize(self):
        self._show_till = datetime.now()

    def is_maximized(self):
        return self._is_referenced(maximized=True)

    def is_minimized(self):
        return self._is_referenced(maximized=False)

    def _is_referenced(self, maximized):
        rect = self._maximized_rect if maximized else self._minimized_rect

        return all(
            self._additions[idx] == 0 or abs(param - rect[idx]) < abs(self._additions[idx])
            for idx, param in enumerate(self.get_rect())
        )

    def _is_active(self):
        return self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos()) or self._show_till > datetime.now()

    def eventloop(self):
        if self._is_active() and not self.is_maximized():
            additions = self._additions
        elif not (self._is_active() or self.is_minimized()):
            additions = tuple(-addition for addition in self._additions)
        else:
            return

        rect = pygame.Rect(tuple(param + additions[idx] for idx, param in enumerate(self.get_rect())))

        self.resize(*rect.size)
        self.move(*rect.topleft)


class LowerPanel(Panel):

    def __init__(self, minimized_rect, maximized_rect, resize_time, parent=None):
        super().__init__(minimized_rect, maximized_rect, resize_time, parent=parent)

        self._buttons = []
        self._separator_points = ((self.get_rect().w / 5, 0),
                                  (self.get_rect().w / 8, self.get_rect().h))

    @property
    def separator_points(self):
        return self._separator_points

    @property
    def buttons(self):
        return self._buttons.copy()

    def add_button(self, button):
        constraints = self._get_next_button_rect()
        button.resize(*constraints.size)
        button.move(*constraints.topleft)
        button.get_width, button.get_height = lambda: constraints.w, lambda: constraints.h
        self._buttons.append(button)

    def remove_button(self, button):
        # self._calc_button_constraints relies on the length of self._buttons, so we need to clear an array to calculate
        # appropriate position for every button (excluding one to be removed) and push them to the self._buttons array
        self._buttons.remove(button)
        buttons_copy = self._buttons.copy()
        self._buttons.clear()

        for button in buttons_copy:
            button.move(*self._get_next_button_rect()[:2])
            self.add_button(button)

    def _get_next_button_rect(self):
        button_size = self._separator_points[1][0] / 5
        space_between_buttons = button_size / 2
        ttl_btn_size = (space_between_buttons + button_size)
        buttons_surface_width = self._separator_points[1][0]
        buttons_surface_height = self.get_rect().h
        buttons_in_row = int((buttons_surface_width + space_between_buttons) / ttl_btn_size)
        buttons_in_col = int((buttons_surface_height + space_between_buttons) / ttl_btn_size)
        indent_x = (buttons_surface_width - ttl_btn_size * buttons_in_row + space_between_buttons) / 2
        indent_y = (buttons_surface_height - ttl_btn_size * buttons_in_col + space_between_buttons) / 2
        x = indent_x + ttl_btn_size * (len(self._buttons) % buttons_in_row)
        y = indent_y + ttl_btn_size * (max(len(self._buttons) - 1, 0) // buttons_in_col)

        return pygame.Rect(x, y, button_size, button_size)

    def draw(self):
        self.fill((40, 43, 48))

        pygame.draw.line(self, (98, 98, 98), *self._separator_points)

        for button in self._buttons:
            button.handle()
            self.blit(button)

        if self.is_minimized():
            self.fill(self.get_background_color())

        pygame.draw.line(self, (98, 98, 98), (0, 0), (self.get_rect().w, 0))


class LineEdit(_SupportsBorder):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._is_focused = False
        self._current_text = ''
        self._placeholder_text = ''

        self._default_data = {
            'text_color': pygame.Color(0, 0, 0),
            'placeholder_color': pygame.Color(69, 69, 69),
            'font': ...,
            'border_color': pygame.Color(197, 199, 201),
            'border_width': 1,
            'border_radius': 0,
            'background_color': pygame.Color(255, 255, 255)
        }

        self._focused_data = self._default_data.copy()
        self._unfocused_data = self._default_data.copy()

        self._pressed_keys = set()
        self._bs_next_unlock = datetime.now()

    def get_params(self, focused, *keys):
        data = {}
        c = self._focused_data if focused else self._unfocused_data

        if not keys:
            return c.copy()

        for key in keys:
            if key not in c:
                keys = ', '.join(f'"{k}"' for k in c)
                raise KeyError(f'Unknown key "{key}", available keys: {keys}') from None
            data[key] = c[key]

        return data

    @staticmethod
    def _set_view(collection, *args, **kwargs):
        collection_copy = collection.copy()

        for kw in kwargs:
            collection[kw] = kwargs[kw]
            collection_copy.pop(kw)

        for k, v in zip(collection_copy, args):
            collection[k] = v

    @property
    def focused(self):
        return self._is_focused

    @focused.setter
    def focused(self, value):
        self._is_focused = value

    @property
    def text(self):
        return self._current_text

    @text.setter
    def text(self, value):
        self._current_text = value

    @property
    def placeholder_text(self):
        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value):
        self._placeholder_text = value

    def set_focused_view(
            self,
            text_color=pygame.Color(0, 0, 0),
            placeholder_color=pygame.Color(69, 69, 69),
            font=...,
            border_color=pygame.Color(115, 169, 222),
            border_width=2,
            border_radius=0,
            background_color=pygame.Color(255, 255, 255)
    ):
        self._set_view(self._focused_data, text_color, placeholder_color, font,
                       border_color, border_width, border_radius, background_color)

    def set_unfocused_view(
            self,
            text_color=pygame.Color(0, 0, 0),
            placeholder_color=pygame.Color(69, 69, 69),
            font=...,
            border_color=pygame.Color(69, 69, 69),
            border_width=1,
            border_radius=0,
            background_color=pygame.Color(255, 255, 255)
    ):
        self._set_view(self._unfocused_data, text_color, placeholder_color, font,
                       border_color, border_width, border_radius, background_color)

    def get_font(self):
        font = (self._focused_data if self.focused else self._unfocused_data).get('font')

        if font != Ellipsis:
            return font

        return pygame.font.SysFont('arial', self.get_rect().h // 2)

    def _draw(self, text, font, text_color, border_color, border_width, border_radius, background_color):
        self.fill(background_color)
        rendered = font.render(text, True, text_color)
        y = self.get_rect().h // 2 - rendered.get_rect().h // 2
        margin_left = border_radius // 2 + border_width + 3
        if self.get_rect().w < rendered.get_rect().w + margin_left * 2:
            self.blit(rendered, rect=(self.get_rect().w - rendered.get_width() - margin_left, y, *rendered.get_size()))
        else:
            self.blit(rendered, rect=(margin_left, y, *rendered.get_rect().size))

        self.border_color = border_color
        self.border_width = border_width
        self.border_radius = border_radius
        super().draw()

    def draw(self):
        if self.focused:
            draw_data = self._focused_data.copy()
        else:
            draw_data = self._unfocused_data.copy()

        pc, tc = draw_data.pop('placeholder_color'), draw_data.pop('text_color')

        if self.text:
            draw_data.update(text=self.text, text_color=tc)
        elif self.placeholder_text:
            draw_data.update(text=self.placeholder_text, text_color=pc)
        else:
            draw_data.update(text='', text_color=tc)
        draw_data.update(font=self.get_font())

        self._draw(**draw_data)

    def eventloop(self):
        pressed = pygame.key.get_pressed()

        if self.focused and (self._bs_next_unlock is None or datetime.now() > self._bs_next_unlock) \
                and (pressed[pygame.K_RETURN] or pressed[pygame.K_BACKSPACE]):
            self.text = self.text[:-1]
            delta = 40 if self._bs_next_unlock else 250
            self._bs_next_unlock = datetime.now() + timedelta(milliseconds=delta)

        if not (pressed[pygame.K_RETURN] or pressed[pygame.K_BACKSPACE]):
            self._bs_next_unlock = None

        for event in catch_events(False):
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._is_focused = self.get_absolute_rect().collidepoint(*pygame.mouse.get_pos())
            if self.focused and event.type == pygame.KEYDOWN and event.unicode and event.unicode.isprintable():
                self.text += event.unicode


class FormField(LineEdit):

    def __init__(self, w, h, secret=False, parent=None):
        # Will be moved and resized by form, but since resize is fake, size params must be greater than zero
        super().__init__(-1, -1, w, h, parent=parent)
        self._secret = secret
        self._secret_view = None
        self._secret_state = True
        self._secret_button = None

        self._errors = ()
        self._label = None

    @property
    def secret(self):
        return self._secret

    @property
    def secret_button(self):
        if self._secret is False:
            return

        return self._secret_button

    @secret_button.setter
    def secret_button(self, value):
        if self._secret is False:
            raise ValueError('Cannot set secret button for field which is not secret (.__init__(secret=False))')

        self._secret_button = value

    @property
    def secret_state(self):
        if self._secret is False:
            return

        return self._secret_state

    @secret_state.setter
    def secret_state(self, value):
        if self._secret is False:
            raise ValueError('Cannot set secret state for field which is not secret (.__init__(secret=False))')

        self._secret_state = value

    @property
    def secret_view(self):
        if self._secret is False:
            return

        return self._secret_view

    @secret_view.setter
    def secret_view(self, value):
        if self._secret is False:
            raise ValueError('Cannot set secret view for field which is not secret (.__init__(secret=False))')

        size = self.get_rect().h
        self._secret_view = pygame.transform.scale(value, (size, size))

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        self._label = value

    @property
    def errors(self):
        return self._errors

    @errors.setter
    def errors(self, values_iterable):
        self._errors = tuple(values_iterable)

    def draw(self):
        if self.secret_state is True:
            real_text = self.text
            self.text = '•' * len(real_text)
            super().draw()
            self.text = real_text
        else:
            super().draw()


class _Freezer:

    def freeze(self):
        post_event(UserEvents.FREEZE_CWW, freezer=self)

    def unfreeze(self):
        post_event(UserEvents.UNFREEZE_CWW, freezer=self)


class Form(_SupportsBorder, _Freezer):

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent=parent)

        self._title = ''
        self._title_color = pygame.Color(255, 255, 255)

        self._fields = []
        self.__secret_buttons = []
        self._submit_button = ...

        self._margin_inline = 10
        self._margin_block = ...

        self._errors_color = pygame.Color(255, 0, 0)

        self.freeze()

    @property
    def submit_button(self):
        if self._submit_button != Ellipsis:
            return self._submit_button

    @submit_button.setter
    def submit_button(self, value):
        value.bind_press(lambda: self.on_success() if self.validate() is True else None,
                         *value.get_press_callbacks(button='L'))
        self._submit_button = value

    @property
    def contents_margin_inline(self):
        return self._margin_inline

    @contents_margin_inline.setter
    def contents_margin_inline(self, value):
        self._margin_inline = value

    @property
    def contents_margin_block(self):
        if self._margin_block != Ellipsis:
            return self._margin_block

        return self._get_avg_fields_font_size()

    @contents_margin_block.setter
    def contents_margin_block(self, value):
        self._margin_block = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def title_color(self):
        return self._title_color

    @title_color.setter
    def title_color(self, value):
        self._title_color = pygame.Color(*value)

    @property
    def background_color(self):
        return self.get_background_color()

    # define background_color once and then use it on every draw() call as fill() param
    @background_color.setter
    def background_color(self, value):
        self._background = pygame.Color(*value)

    @property
    def errors_color(self):
        return self._errors_color

    @errors_color.setter
    def errors_color(self, value):
        self._errors_color = pygame.Color(*value)

    @property
    def fields(self):
        return self._fields.copy()

    def as_tuple(self):
        return tuple(field.text for field in self._fields)

    def validate(self):  # errors should be added here. returns bool
        return True

    def on_success(self):  # request db for saving data (can be accessed with as_tuple()), close form etc
        self.__del__()
        self.unfreeze()

    def add_field(self, field):
        self._fields.append(field)

    def _get_avg_fields_font_size(self):
        return round(sum(field.get_font().get_height() for field in self._fields) / len(self._fields))

    def draw(self):
        self.fill(self.background_color)
        super().draw()

        y = self.contents_margin_block

        if self._title:
            ttl = pygame.font.SysFont(
                'arial', self._get_avg_fields_font_size() // 3 * 4
            ).render(self._title, True, self._title_color)
            self.blit(ttl, rect=((self.get_rect().w - ttl.get_rect().w) // 2, self.contents_margin_block,
                                 *ttl.get_size()))

            y += ttl.get_height() + self.contents_margin_block

        for field in self.fields:
            font = field.get_font()

            if field.label:
                font.bold = True
                field_label = font.render(field.label, True, (255, 255, 255))
                self.blit(field_label, rect=(field.get_rect().x, y, *field_label.get_size()))
                y += field_label.get_height() + 5
            font.bold = False

            field.move(self.contents_margin_inline, y)
            field.handle()
            self.blit(field)
            y += field.get_rect().h

            if field.secret and not field.secret_button:
                secret_btn = Button(self.get_rect().w - self.contents_margin_inline - field.secret_view.get_rect().w, y,
                                    *field.secret_view.get_size(), parent=self)
                secret_btn.set_hovered_view(field.secret_view)
                secret_btn.set_not_hovered_view(field.secret_view)
                secret_btn.bind_press((lambda f: lambda: setattr(f, 'secret_state', not f.secret_state))(field))
                field.secret_button = secret_btn

            if field.secret_button:
                field.secret_button.handle()
                self.blit(field.secret_button)
                if not field.errors:
                    y += field.secret_button.get_rect().h

            font.italic = True
            for err in field.errors:
                y += self.contents_margin_block // 8
                text = font.render(f'• {err}', True, self._errors_color)
                self.blit(text, rect=(field.get_rect().x, y, *text.get_size()))
                y += text.get_height()
            y += self.contents_margin_block

        y = self.get_rect().h - self.contents_margin_block // 2 - self.submit_button.get_rect().h
        self.submit_button.move(self.contents_margin_inline, y)
        self.submit_button.handle()
        self.blit(self.submit_button)
