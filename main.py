import datetime
import os # Para verificar la existencia de imágenes
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton, ToggleButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, ListProperty, StringProperty, ObjectProperty, DictProperty, ColorProperty
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.factory import Factory
from kivy.event import EventDispatcher
from kivy.storage.jsonstore import JsonStore
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserIconView


# --- Clase Base para el Gesto de Deslizamiento a la Derecha ---
class SwipeRightToMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._touch_start_pos = None
        self._swipe_started_inside = False
        self.SWIPE_THRESHOLD_X = dp(75)
        self.SWIPE_TOLERANCE_Y = dp(50)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_start_pos = touch.pos
            self._swipe_started_inside = True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self._swipe_started_inside and self._touch_start_pos and self.collide_point(*touch.pos):
            diff_x = touch.x - self._touch_start_pos[0]
            diff_y_abs = abs(touch.y - self._touch_start_pos[1])

            if diff_x > self.SWIPE_THRESHOLD_X and diff_y_abs < self.SWIPE_TOLERANCE_Y:
                app_instance = App.get_running_app()
                print(f"INFO: Gesto de deslizamiento derecho detectado en la pantalla '{self.name}'. Volviendo al menú.")
                if self.name == 'add_product' and hasattr(self, 'clear_and_go_to_menu'):
                    self.clear_and_go_to_menu()
                elif self.name == 'sale' and hasattr(self, 'go_to_menu_action'):
                    self.go_to_menu_action()
                elif self.name in ['view_products', 'history', 'settings']:
                    if app_instance and app_instance.sm:
                        app_instance.sm.current = 'menu'
                else:
                    if app_instance and app_instance.sm:
                        print(f"ADVERTENCIA: Pantalla '{self.name}' no tiene acción de menú específica definida para deslizamiento, usando app.sm.current = 'menu'.")
                        app_instance.sm.current = 'menu'
                self._touch_start_pos = None
                self._swipe_started_inside = False
                return True
        self._touch_start_pos = None
        self._swipe_started_inside = False
        return super().on_touch_up(touch)

# --- Definiciones de Clases Python Personalizadas (ANTES de kv_string) ---
class MyTitleLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_theme_colors)
            self.update_theme_colors()

    def update_theme_colors(self, *args):
        app = App.get_running_app()
        if app:
            self.color = app.theme_config.get("MyTitleLabel_color", (0.9, 0.9, 0.95, 1))

class MyHeaderLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_theme_colors)
            self.update_theme_colors()

    def update_theme_colors(self, *args):
        app = App.get_running_app()
        if app:
            self.color = app.theme_config.get("MyHeaderLabel_color", (0.85, 0.85, 0.9, 1))

class MyActionButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_theme_colors)
            self.update_theme_colors()

    def update_theme_colors(self, *args):
        app = App.get_running_app()
        if app:
            if self.text.lower() == 'salir':
                 self.background_color = app.theme_config.get("ExitButton_rgba", (0.85, 0.25, 0.25, 1))
            else:
                 self.background_color = app.theme_config.get("MyActionButton_rgba", (0.25, 0.45, 0.65, 1))


class MySmallActionButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_theme_colors)
            self.update_theme_colors()

    def update_theme_colors(self, *args):
        app = App.get_running_app()
        if app:
            self.background_color = app.theme_config.get("MySmallActionButton_rgba", (0.3, 0.6, 0.4, 1))

class MyInputLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_theme_colors)
            self.update_theme_colors()

    def update_theme_colors(self, *args):
        app = App.get_running_app()
        if app:
            self.color = app.theme_config.get("MyInputLabel_color", (0.85,0.85,0.9,1))


class MyPaddedBoxLayout(BoxLayout):
    pass

class ProductoData(EventDispatcher):
    numero = NumericProperty(0)
    nombre = StringProperty("")
    precio = NumericProperty(0)
    cantidad = NumericProperty(0)
    precio_formateado = StringProperty("")
    imagen_path = StringProperty("")

class ProductCard(ToggleButtonBehavior, BoxLayout):
    product_data = DictProperty({})
    view_product_screen_ref = ObjectProperty(None)
    background_color_normal = ColorProperty([0.22, 0.24, 0.27, 1])
    background_color_selected = ColorProperty([0.35, 0.55, 0.8, 1])
    border_color_normal = ColorProperty([0.32, 0.34, 0.37, 1])
    border_color_selected = ColorProperty([0.5, 0.7, 0.95, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_colors_from_theme)
            self.update_colors_from_theme()

    def update_colors_from_theme(self, *args):
        app = App.get_running_app()
        if not app: return
        theme = app.theme_config
        self.background_color_normal = theme.get("ProductCard_bg_normal_rgba", [0.22, 0.24, 0.27, 1])
        self.background_color_selected = theme.get("ProductCard_bg_selected_rgba", [0.35, 0.55, 0.8, 1])
        self.border_color_normal = theme.get("ProductCard_border_normal_rgba", [0.32, 0.34, 0.37, 1])
        self.border_color_selected = theme.get("ProductCard_border_selected_rgba", [0.5, 0.7, 0.95, 1])

    def edit_product(self):
        if self.view_product_screen_ref and self.product_data:
            self.view_product_screen_ref.edit_product_action(self.product_data)

    def delete_product(self):
        if self.view_product_screen_ref and self.product_data:
            self.view_product_screen_ref.delete_product_popup(self.product_data)

class SelectableProductRow(ToggleButtonBehavior, BoxLayout):
    product_dict = ObjectProperty(None)
    background_color_normal = ColorProperty([0.22, 0.24, 0.27, 1])
    background_color_selected = ColorProperty([0.35, 0.55, 0.8, 1])
    border_color_normal = ColorProperty([0.32, 0.34, 0.37, 1])
    border_color_selected = ColorProperty([0.5, 0.7, 0.95, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_colors_from_theme)
            self.update_colors_from_theme()

    def update_colors_from_theme(self, *args):
        app = App.get_running_app()
        if not app: return
        theme = app.theme_config
        self.background_color_normal = theme.get("SelectableProductRow_normal_rgba", [0.22, 0.24, 0.27, 1])
        self.background_color_selected = theme.get("SelectableProductRow_selected_rgba", [0.35, 0.55, 0.8, 1])

class CartItemCard(BoxLayout): 
    item_data = DictProperty({})
    background_color_cart_item = ColorProperty([0.20, 0.22, 0.25, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app:
            app.bind(theme_config=self.update_colors_from_theme)
            self.update_colors_from_theme()

    def update_colors_from_theme(self, *args):
        app = App.get_running_app()
        if not app: return
        theme = app.theme_config
        self.background_color_cart_item = theme.get("CartItemCard_bg_rgba", [0.20, 0.22, 0.25, 1])


# --- Definición de la interfaz de usuario en lenguaje KV ---
kv_string = """
#:import Window kivy.core.window.Window
#:import dp kivy.metrics.dp
#:import os os

<MyTitleLabel>:
    font_size: '32sp'
    size_hint_y: None
    height: self.texture_size[1] + dp(20)
    halign: 'center'
    bold: True

<MyHeaderLabel>:
    font_size: '24sp'
    bold: True
    size_hint_y: None
    height: self.texture_size[1] + dp(5)

<MyActionButton>:
    press_shift: dp(2.5)
    padding: [self.press_shift, self.press_shift, -self.press_shift, -self.press_shift] if self.state == 'down' else [0,0,0,0]
    size_hint_y: None
    height: dp(60)
    size_hint_x : 1
    font_size: '25sp'
    background_normal: ''
    background_down: ''
    background_disabled_normal: ''
    color: (1,1,1,1)
    canvas.before:
        Color:
            rgba: (self.background_color[0]*0.8, self.background_color[1]*0.8, self.background_color[2]*0.8, self.background_color[3]) if self.state == 'down' else self.background_color
        RoundedRectangle:
            pos: (self.x + self.press_shift, self.y - self.press_shift) if self.state == 'down' else self.pos
            size: (self.width - self.press_shift*1.5, self.height - self.press_shift*1.5) if self.state == 'down' else self.size
            radius: [dp(12)]
    canvas.after:
        Color:
            rgba: (0.85, 0.85, 0.95, 0.6)
        Line:
            rounded_rectangle: ((self.x + self.press_shift, self.y - self.press_shift, self.width - self.press_shift*1.5, self.height - self.press_shift*1.5, dp(12)) if self.state == 'down' else (self.x, self.y, self.width, self.height, dp(12)))
            width: dp(1.5)

<MySmallActionButton>:
    press_shift: dp(2)
    padding: [self.press_shift, self.press_shift, -self.press_shift, -self.press_shift] if self.state == 'down' else [0,0,0,0]
    size_hint_y: None
    height: dp(45)
    font_size: '19sp'
    background_normal: ''
    background_down: ''
    background_disabled_normal: ''
    color: (1,1,1,1)
    canvas.before:
        Color:
            rgba: (self.background_color[0]*0.8, self.background_color[1]*0.8, self.background_color[2]*0.8, self.background_color[3]) if self.state == 'down' else self.background_color
        RoundedRectangle:
            pos: (self.x + self.press_shift, self.y - self.press_shift) if self.state == 'down' else self.pos
            size: (self.width - self.press_shift, self.height - self.press_shift) if self.state == 'down' else self.size
            radius: [dp(10)]
    canvas.after:
        Color:
            rgba: (0.85, 0.85, 0.95, 0.6)
        Line:
            rounded_rectangle: ((self.x + self.press_shift, self.y - self.press_shift, self.width - self.press_shift, self.height - self.press_shift, dp(10)) if self.state == 'down' else (self.x, self.y, self.width, self.height, dp(10)))
            width: dp(1.5)

<MyInputLabel>:
    font_size: '20sp'
    halign: 'left'
    valign: 'middle'
    text_size: self.width, None

<MyPaddedBoxLayout>:
    padding: dp(15)
    spacing: dp(10)

<AttractiveLoadingPopup@Popup>:
    size_hint: None, None
    size: dp(200), dp(170)
    auto_dismiss: False
    separator_height: 0
    title: "Cargando..."
    title_align: 'center'
    title_color: (0.9, 0.9, 0.95, 1)
    title_size: '18sp'
    background: ''
    background_color: [0, 0, 0, 0]

    BoxLayout:
        pos: self.pos
        size: self.size
        padding: dp(5)
        canvas.before:
            Color:
                rgba: [0.08, 0.08, 0.11, 0.92]
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(15)]
        Image:
            source: 'load.gif'
            size_hint: (1, 1)
            allow_stretch: True
            anim_loop: 0
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}


<QuantityPopup@Popup>:
    title: "Ingresar Cantidad"
    title_align: 'center'
    title_size: '22sp'
    size_hint: 0.85, None
    height: dp(350)
    auto_dismiss: False
    separator_color: (0.3,0.3,0.3,1)
    background_color: (0,0,0,0)
    background: ''
    BoxLayout:
        orientation: 'vertical'
        padding: (dp(1), dp(1))
        canvas.before:
            Color:
                rgba: app.theme_config.get("Popup_bg_rgba", (0.1, 0.1, 0.12, 0.98))
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
        Label:
            size_hint_y: None
            height: dp(40)
        BoxLayout:
            orientation: 'vertical'
            padding: [dp(20), dp(10), dp(20), dp(20)]
            spacing: dp(15)
            Label:
                id: popup_product_name_label
                text: "Producto: [Nombre]"
                font_size: '20sp'
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(5)
            Label:
                id: popup_stock_label
                text: "Stock disponible: [Stock]"
                font_size: '18sp'
                size_hint_y: None
                height: self.texture_size[1] + dp(5)
            TextInput:
                id: popup_quantity_input
                hint_text: "Cantidad a agregar"
                input_type: 'number'
                multiline: False
                font_size: '20sp'
                size_hint_y: None
                height: dp(48)
                padding: [dp(8), (self.height - self.line_height) / 2 if self.line_height > 0 else dp(8)]
                text: "1"
            MySmallActionButton:
                id: popup_accept_button
                text: "Aceptar"
                on_press: root.accept_quantity()
                background_color: app.theme_config.get("Popup_Accept_Button_rgba", app.theme_config.get("MySmallActionButton_rgba", (0.2, 0.65, 0.3, 1)))
            MySmallActionButton:
                id: popup_cancel_button
                text: "Cancelar"
                on_press: root.dismiss()
                background_color: app.theme_config.get("Popup_Cancel_Button_rgba", (0.85, 0.25, 0.25, 1))

<VueltoPopup@Popup>:
    title: "Calcular Vuelto"
    title_align: 'center'
    title_size: '22sp'
    size_hint: 0.85, None
    height: dp(360)
    auto_dismiss: False
    separator_color:(0.3,0.3,0.3,1)
    background_color : (0,0,0,0)
    background : ''
    BoxLayout:
        orientation: 'vertical'
        padding: (dp(1), dp(1))
        canvas.before:
            Color:
                rgba: app.theme_config.get("Popup_bg_rgba", (0.1, 0.1, 0.12, 0.98))
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(10)]
        Label:
            size_hint_y: None
            height: dp(40)
        BoxLayout:
            orientation: 'vertical'
            padding: [dp(20), dp(10), dp(20), dp(20)]
            spacing: dp(15)
            Label:
                id: popup_total_a_pagar_label
                text: "Total a Pagar: $0"
                font_size: '23sp'
                size_hint_y: None
                height: self.texture_size[1] + dp(5)
                bold: True
            BoxLayout:
                size_hint_y: None
                height: dp(48)
                spacing: dp(10)
                Label:
                    text: "Paga con:"
                    font_size: '21sp'
                    size_hint_x: 0.45
                    text_size: self.width, None
                    halign: 'left'
                    valign: 'middle'
                TextInput:
                    id: popup_monto_pagado_input
                    input_type: 'number'
                    multiline: False
                    font_size: '21sp'
                    hint_text: "0.00"
                    padding: [dp(6), (self.height - self.line_height) / 2 if self.line_height > 0 else dp(6)]
                    size_hint_y: None
                    height: dp(45)
                    valign: 'middle'
            MySmallActionButton:
                id: popup_calcular_button
                text: "Calcular Vuelto"
                on_press: root.calculate_popup_vuelto()
            Label:
                id: popup_vuelto_calculado_label
                text: " $0"
                font_size: '23sp'
                bold: True
                size_hint_y: None
                height: self.texture_size[1] + dp(5)
                color: (0.8, 0.8, 0.3, 1)
            BoxLayout:
                size_hint_y: None
                height: dp(50)
                spacing: dp(15)
                padding: [0, dp(5),0,0]
                MySmallActionButton:
                    text: "Aceptar"
                    on_press: root.accept_vuelto()
                MySmallActionButton:
                    text: "Cancelar"
                    background_color: (0.85,0.25,0.25,1)
                    on_press: root.dismiss()

<ProductCard>: 
    orientation: 'vertical'
    size_hint_y: None
    height: dp(215)
    padding: dp(8)
    spacing: dp(5)
    canvas.before:
        Color:
            rgba: root.background_color_selected if root.state == 'down' else root.background_color_normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
        Color:
            rgba: root.border_color_selected if root.state == 'down' else root.border_color_normal
        Line:
            rounded_rectangle: (self.x + dp(1), self.y + dp(1), self.width - dp(2), self.height - dp(2), dp(9))
            width: dp(1.8) if root.state == 'down' else dp(1.2)

    Image:
        id: card_image
        source: root.product_data.get('imagen_path', 'placeholder.png') if root.product_data.get('imagen_path') and os.path.exists(root.product_data.get('imagen_path')) else 'placeholder.png'
        size_hint_y: 0.45
        allow_stretch: True
        keep_ratio: False
        fit_mode: "cover"

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.35
        padding: [dp(5), 0]
        spacing: dp(2)
        Label:
            id: card_nombre
            text: root.product_data.get('nombre', 'No Disp.')
            font_size: '16sp'
            bold: True
            color: app.theme_config.get("MyInputLabel_color", (0.95,0.95,0.98,1))
            halign: 'center'
            valign: 'top'
            text_size: self.width, None
            shorten: True
            shorten_from: 'right'
            size_hint_y: 0.4
        Label:
            id: card_precio
            text: "Precio: $" + (f"{int(root.product_data.get('precio', 0)):,}".replace(",", "_").replace(".", ",").replace("_", ".")) if root.product_data else "Precio: $0"
            font_size: '14sp'
            color: app.theme_config.get("MyInputLabel_color", (0.85,0.85,0.9,1))
            halign: 'center'
            valign: 'center'
            text_size: self.width, None
            size_hint_y: 0.3
        Label:
            id: card_stock
            text: "Stock: " + str(root.product_data.get('cantidad', 0))
            font_size: '13sp'
            color: app.theme_config.get("MyInputLabel_color", (0.80,0.80,0.85,1))
            halign: 'center'
            valign: 'bottom'
            text_size: self.width, None
            size_hint_y: 0.3

    BoxLayout:
        id: action_buttons_layout
        orientation: 'horizontal'
        size_hint_y: None
        height: dp(48) if root.state == 'down' else 0
        opacity: 1 if root.state == 'down' else 0
        spacing: dp(8)
        padding: [0, dp(2), 0, dp(2)]

        MySmallActionButton:
            text: "Editar"
            on_press: root.edit_product()
            disabled: root.state == 'normal'
        MySmallActionButton:
            text: "Eliminar"
            on_press: root.delete_product()
            disabled: root.state == 'normal'
            background_color: app.theme_config.get("ProductCard_DeleteButton_rgba", app.theme_config.get("ExitButton_rgba", (0.85,0.25,0.25,1)))

<SelectableProductRow>: 
    orientation: 'vertical' 
    size_hint_y: None
    height: dp(160) 
    group: "productos_seleccionables"
    allow_no_selection: True 
    padding: [dp(6), dp(6), dp(6), dp(6)] 
    spacing: dp(4) 

    canvas.before:
        Color:
            rgba: root.background_color_selected if root.state == 'down' else root.background_color_normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8)]
        Color: 
            rgba: (0.5, 0.7, 0.95, 1) if root.state == 'down' else (0.32, 0.34, 0.37, 1)
        Line:
            rounded_rectangle: (self.x + dp(1), self.y + dp(1), self.width - dp(2), self.height - dp(2), dp(7))
            width: dp(1.8) if root.state == 'down' else dp(1.2)

    Image:
        id: prod_row_image
        source: root.product_dict.imagen_path if root.product_dict and root.product_dict.imagen_path and os.path.exists(root.product_dict.imagen_path) else "placeholder.png"
        size_hint_y: 0.55 
        allow_stretch: True
        keep_ratio: False 
        fit_mode: "contain" 
        pos_hint: {'center_x': 0.5}

    BoxLayout: 
        orientation: 'vertical'
        size_hint_y: 0.45 
        padding: [dp(4), dp(2)]
        spacing: dp(1)
        
        Label:
            id: nombre_prod_label
            text: root.product_dict.nombre if root.product_dict else "Nombre Producto"
            font_size: '12sp' 
            bold: True
            color: (0.95, 0.95, 0.98, 1)
            halign: 'center' 
            valign: 'top'
            text_size: self.width, None
            shorten: True
            shorten_from: 'right'
            size_hint_y: None 
            height: self.texture_size[1] + dp(2)

        Label:
            id: precio_prod_label
            text: ("Precio: $" + root.product_dict.precio_formateado) if root.product_dict else "Precio: $0"
            font_size: '12sp' 
            color: (0.75, 0.95, 0.1, 1)
            halign: 'center' 
            valign: 'center'
            text_size: self.width, None
            size_hint_y: None 
            height: self.texture_size[1] + dp(2)

        Label:
            id: stock_prod_label
            text: ("Stock: " + str(root.product_dict.cantidad)) if root.product_dict else "Stock: 0"
            font_size: '12sp' 
            color: (0.10,0.80,0.95,1)
            halign: 'center' 
            valign: 'bottom'
            text_size: self.width, None
            size_hint_y: None 
            height: self.texture_size[1] + dp(2)

<CartItemCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(110) 
    padding: dp(4)
    spacing: dp(2)
    canvas.before:
        Color:
            rgba: root.background_color_cart_item
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(6)]
        Color:
            rgba: (0.3, 0.32, 0.35, 1) 
        Line:
            rounded_rectangle: (self.x + dp(0.5), self.y + dp(0.5), self.width - dp(1), self.height - dp(1), dp(5.5))
            width: dp(1)

    Image:
        id: cart_item_image
        source: root.item_data.get('imagen_path', 'placeholder.png') if root.item_data.get('imagen_path') and os.path.exists(root.item_data.get('imagen_path')) else 'placeholder.png'
        size_hint_y: 0.50
        allow_stretch: True
        keep_ratio: False
        fit_mode: "contain"

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.50
        padding: [dp(3), dp(1)]
        spacing: dp(1)

        Label:
            id: cart_item_nombre
            text: root.item_data.get('nombre', 'N/A')
            font_size: '10sp'
            bold: True
            color: app.theme_config.get("CartItems_text_color", (0.92,0.92,0.95,1))
            halign: 'center'
            valign: 'top'
            text_size: self.width, None
            shorten: True
            shorten_from: 'right'
            size_hint_y: None
            height: self.texture_size[1] + dp(1)

        Label:
            id: cart_item_cantidad
            text: "Cant: " + str(root.item_data.get('cantidad', 0))
            font_size: '9sp'
            color: app.theme_config.get("CartItems_text_color", (0.90,0.90,0.93,1))
            halign: 'center'
            size_hint_y: None
            height: self.texture_size[1] + dp(1)

        Label:
            id: cart_item_subtotal
            text: "Sub: $" + (f"{int(root.item_data.get('precio_unitario', 0) * root.item_data.get('cantidad', 0)):,}".replace(",", "_").replace(".", ",").replace("_", ".")) if root.item_data else "Sub: $0"
            font_size: '9sp'
            color: app.theme_config.get("CartItems_text_color", (0.88,0.88,0.92,1))
            halign: 'center'
            valign: 'bottom'
            size_hint_y: None
            height: self.texture_size[1] + dp(1)

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(50), dp(10), dp(50), dp(30)]
        spacing: dp(20)
        BoxLayout:
            size_hint_y: None
            height: dp(70)
            padding: [dp(10), 0, dp(10), dp(10)]
            Button:
                id: settings_button
                size_hint_x: None
                width: dp(50)
                height: dp(50)
                pos_hint: {'center_y': 0.5}
                on_press: app.sm.current = 'settings'
                background_normal: 'boton_configuracion.png' 
                background_down: 'boton_configuracion.png'
                background_color: (1,1,1,1)
                border: (0,0,0,0)
            Label:
                size_hint_x: 1
        Image:
            source: 'título.png' 
            size_hint_y: None
            height: dp(140)
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_x': 0.5}
        MyActionButton:
            text: 'Agregar Producto'
            on_press: root.go_to_add_product_screen()
        MyActionButton:
            text: 'Mis Productos'
            on_press: app.sm.current = 'view_products'
        MyActionButton:
            text: 'Nueva Venta'
            on_press: app.sm.current = 'sale'
        MyActionButton:
            text: 'Historial Ventas'
            on_press: app.sm.current = 'history'
        BoxLayout:
            size_hint_y: 1 
        MyActionButton:
            text: 'Salir'
            on_press: app.stop()
            background_color: app.theme_config.get("ExitButton_rgba", (0.85, 0.25, 0.25, 1))

<AddProductScreen>:
    product_to_edit: None
    BoxLayout:
        orientation: 'vertical'
        padding: [dp(25), dp(50), dp(25), dp(20)]
        spacing: dp(15)
        Image:
            id: add_screen_image
            source: 'agregar_producto.png' 
            size_hint_y: None
            height: dp(140)
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_x': 0.5}
        GridLayout:
            cols: 2
            spacing: dp(12)
            size_hint_y: None
            height: self.minimum_height
            MyInputLabel:
                text: ' Nombre:'
                font_size: '29sp'
            TextInput:
                id: nombre_input
                multiline: False
                size_hint_y: None
                height: dp(45)
                font_size: '20sp'
            MyInputLabel:
                text: ' Precio ($):'
                font_size: '29sp'
            TextInput:
                id: precio_input
                multiline: False
                input_type: 'number'
                hint_text: "0.00"
                size_hint_y: None
                height: dp(45)
                font_size: '20sp'
            MyInputLabel:
                text: ' Cantidad :'
                font_size: '29sp'
            TextInput:
                id: cantidad_input
                multiline: False
                input_type: 'number'
                hint_text: "0"
                size_hint_y: None
                height: dp(45)
                font_size: '20sp'
            MyInputLabel:
                text: ' Imagen:'
                font_size: '29sp'
                valign: 'center'
            BoxLayout:
                size_hint_y: None
                height: dp(60)
                spacing: dp(10)
                valign: 'center'
                Image:
                    id: image_preview
                    source: 'placeholder.png'
                    size_hint_x: 0.4
                    allow_stretch: True
                    keep_ratio: True
                    fit_mode: 'contain'
                    canvas.before:
                        Color:
                            rgba: (0.15, 0.16, 0.18, 1)
                        Rectangle:
                            pos: self.pos
                            size: self.size
                        Color:
                            rgba: (0.4, 0.4, 0.45, 1)
                        Line:
                            rectangle: self.x + dp(1), self.y + dp(1), self.width - dp(2), self.height - dp(2)
                            width: dp(1.1)
                MySmallActionButton:
                    text: "Buscar"
                    size_hint_x: 0.6
                    pos_hint: {'center_y': 0.5}
                    on_press: root.open_file_chooser()

        BoxLayout:
            size_hint_y: None
            height: dp(25) 
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            size_hint_y: None
            height: self.minimum_height
            padding: [dp(10), dp(10), dp(10), dp(5)]
            MyActionButton:
                id: save_button 
                text: 'Guardar Producto' 
                on_press: root.save_product_action()
        Label:
            text: "" 
            size_hint_y: 1

<ViewProductsScreen>:
    MyPaddedBoxLayout:
        orientation: 'vertical'
        Image:
            source: 'mis_productos.png' 
            size_hint_y: None
            height: dp(130)
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_x': 0.5}

        ScrollView:
            id: view_products_scrollview
            size_hint_y: 1
            bar_width: dp(4)
            canvas.before:
                Color:
                    group: 'bg_color'
                    rgba: app.theme_config.get("product_list_bg_rgba", [0,0,0,0]) 
                Rectangle:
                    pos: self.pos
                    size: self.size
            GridLayout:
                id: products_grid_cards 
                cols: 2
                spacing: dp(8)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(-40) 

<SaleScreen>:
    MyPaddedBoxLayout:
        orientation: 'vertical'
        spacing: dp(12)
        Image:
            source: 'seleccionar_producto.png' 
            size_hint_y: None
            height: dp(125)
            allow_stretch: True
            keep_ratio: True
            pos_hint: {'center_x': 0.5}
        ScrollView:
            id: sale_products_scrollview
            size_hint_y: 0.48
            canvas.before:
                Color:
                    group: 'bg_color'
                    rgba: app.theme_config.get("product_list_bg_rgba", [0,0,0,0])
                Rectangle:
                    pos: self.pos
                    size: self.size
            GridLayout:
                id: sale_products_grid 
                cols: 4 
                spacing: dp(6) 
                padding: (dp(6), dp(6)) 
                size_hint_y: None
                height:self.minimum_height
        MyActionButton:
            id: add_to_cart_button
            text: "Agregar al Carro"
            font_size: '22sp'
            size_hint_y: None
            height: dp(55)
            disabled: root.selected_product_widget is None
            on_press: root.open_quantity_popup()
        Label:
            text: "~Carro De Compra~"
            font_size: '30sp'
            size_hint_y: None
            height: dp(35)
            bold: True
            color: (0.9,0.9,0.95,1)
        ScrollView:
            size_hint_y: 0.25 
            bar_width: dp(3)
            GridLayout:
                id: cart_items_layout 
                cols: 4 
                spacing: dp(5) 
                padding: [dp(5), dp(0), dp(5), dp(1)]
                size_hint_y: None
                height: self.minimum_height
        GridLayout:
            cols: 1
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(10)
            padding: [20, dp(8)]
            Label:
                id: total_label
                text: "Total: $0"
                font_size: '35sp'
                bold: True
                size_hint_y: None
                height: dp(30)
                color: (0.85, 0.95, 0.3, 1)
            BoxLayout: 
                size_hint_y: None
                height: dp(46)
                spacing: dp(10)
                MySmallActionButton:
                    text: "Vuelto"
                    size_hint_x: 0.5
                    on_press: root.open_vuelto_popup()
                    disabled: root.total_temp == 0
                Label:
                    id: vuelto_label
                    text: " $0"
                    font_size: '25sp'
                    size_hint_x: 0.6
                    size_hint_y: 0
                    padding: [20, dp(10)]
                    text_size: self.width, None
                    color: (0.4, 0.8, 0.3, 1)
        GridLayout: 
            cols: 2 
            size_hint_y: None
            height: dp(45)
            spacing: dp(10)
            padding: [dp(10), dp(-3), dp(10), dp(10)]
            MyActionButton:
                text: "Confirmar"
                on_press: root.confirm_purchase_action()
            MyActionButton:
                text: "Cancelar"
                on_press: root.cancel_purchase_action()
                background_color: (0.85, 0.25, 0.25, 1)

<HistoryScreen>:
    MyPaddedBoxLayout:
        orientation: 'vertical'
        MyTitleLabel:
            text: 'Historial de Ventas'
        ScrollView:
            id: history_scrollview
            size_hint_y: 1
            BoxLayout:
                id: history_layout 
                orientation: 'vertical'
                spacing: dp(15)
                padding: (dp(8), dp(8))
                size_hint_y: None
                height: self.minimum_height
        Label:
            id: total_dia_label 
            text: "Total Ventas Hoy: $ 0"
            font_size: '24sp'
            bold: True
            color: (0.9, 0.9, 0.55, 1)
            size_hint_y: None
            height: self.texture_size[1] + dp(20)
            padding: [dp(10), dp(10)]
            halign: 'center'
            valign: 'middle'
        BoxLayout: 
            size_hint_y: None
            height: dp(-10) 

<SettingsScreen>: 
    FloatLayout:
        id: settings_root_layout
        canvas.before:
            Color:
                group: 'bg_color'
                rgba: app.theme_config.get("SettingsScreen_bg_rgba", [0.12, 0.13, 0.15, 0.85]) 
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            size_hint: 1, 1

            MyTitleLabel:
                text: "Configuración "
            ScrollView:
                size_hint_y: 1
                GridLayout:
                    cols: 1
                    spacing: dp(20)
                    padding: dp(10)
                    size_hint_y: None
                    height: self.minimum_height

                    MyHeaderLabel:
                        text: "Color Botón Principal"
                        halign: 'left'
                    GridLayout: 
                        cols: 4
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(45)
                        ToggleButton:
                            id: btn_action_default
                            text:"Azul Def."
                            group: "action_button_color_group"
                            allow_no_selection: False
                            on_press: root.set_button_color_preset('MyActionButton_rgb', [0.25,0.45,0.65])
                        ToggleButton:
                            id: btn_action_green
                            text:"Verde"
                            group: "action_button_color_group"
                            allow_no_selection: False
                            on_press: root.set_button_color_preset('MyActionButton_rgb', [0.2,0.6,0.3])
                        ToggleButton:
                            id: btn_action_red
                            text:"Rojo"
                            group: "action_button_color_group"
                            allow_no_selection: False
                            on_press: root.set_button_color_preset('MyActionButton_rgb', [0.7,0.2,0.2])
                        ToggleButton:
                            id: btn_action_orange
                            text:"Naranja"
                            group: "action_button_color_group"
                            allow_no_selection: False
                            on_press: root.set_button_color_preset('MyActionButton_rgb', [0.9,0.5,0.1])

                    MyHeaderLabel:
                        text: "Opacidad de Botones"
                        halign: 'left'
                    BoxLayout: 
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        Slider:
                            id: button_opacity_slider
                            min: 0.0
                            max: 1.0
                            value: app.theme_config.get("button_opacity", 1.0)
                            on_value: root.update_preview_theme('button_opacity', self.value)
                        Label:
                            id: button_opacity_label
                            text: f"{button_opacity_slider.value:.2f}"
                            size_hint_x: 0.2

                    MyHeaderLabel:
                        text: "Opacidad Fondo Tarjetas"
                        halign: 'left'
                    BoxLayout: 
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        Slider:
                            id: card_opacity_slider
                            min: 0.0
                            max: 1.0
                            value: app.theme_config.get("card_background_opacity", 1.0)
                            on_value: root.update_preview_theme('card_background_opacity', self.value)
                        Label:
                            id: card_opacity_label
                            text: f"{card_opacity_slider.value:.2f}"
                            size_hint_x: 0.2

                    MyHeaderLabel:
                        text: "Opacidad Fondo Listas"
                        halign: 'left'
                    BoxLayout: 
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        Slider:
                            id: product_list_opacity_slider
                            min: 0.0
                            max: 1.0
                            value: app.theme_config.get("product_list_bg_opacity", 0.0)
                            on_value: root.update_preview_theme('product_list_bg_opacity', self.value)
                        Label:
                            id: product_list_opacity_label
                            text: f"{product_list_opacity_slider.value:.2f}"
                            size_hint_x: 0.2

                    MyHeaderLabel:
                        text: "Opacidad Fondo Configuración"
                        halign: 'left'
                    BoxLayout: 
                        orientation: 'horizontal'
                        size_hint_y: None
                        height: dp(40)
                        Slider:
                            id: settings_bg_opacity_slider
                            min: 0.0
                            max: 1.0
                            value: app.theme_config.get("settings_screen_bg_opacity", app.default_theme_settings["settings_screen_bg_opacity"])
                            on_value: root.update_preview_theme('settings_screen_bg_opacity', self.value)
                        Label:
                            id: settings_bg_opacity_label
                            text: f"{settings_bg_opacity_slider.value:.2f}"
                            size_hint_x: 0.2

                    MyHeaderLabel:
                        text: ""
                        halign: 'left'
                    MySmallActionButton:
                        text: "Restaurar Ajustes"
                        on_press: root.restore_default_preview()
                        background_color: (0.2, 0.65, 0.8, 1) 
            BoxLayout: 
                size_hint_y: None
                height: dp(60)
                spacing: dp(10) 
                padding: [dp(0), dp(0), dp(0), dp(0)] 
                MyActionButton:
                    text: "Guardar Cambios"
                    on_press: root.apply_and_save_theme_changes()
                    background_color: (0.2, 0.65, 0.3, 1) 
                    size_hint_x: 1 
"""
Builder.load_string(kv_string)

# --- Clases de Popups ---
class AttractiveLoadingPopup(Popup):
    pass

class QuantityPopup(Popup):
    sale_screen_ref = ObjectProperty(None)
    product_to_add = ObjectProperty(None) 

    def __init__(self, sale_screen_ref, product_to_add, **kwargs):
        super().__init__(**kwargs)
        self.sale_screen_ref = sale_screen_ref
        self.product_to_add = product_to_add
        self.ids.popup_product_name_label.text = f"Producto: {self.product_to_add.nombre}"
        self.ids.popup_stock_label.text = f"Stock disponible: {self.product_to_add.cantidad}"
        self.ids.popup_quantity_input.text = "1"

    def accept_quantity(self):
        app = App.get_running_app()
        try:
            cantidad_str = self.ids.popup_quantity_input.text
            if not cantidad_str:
                app.show_popup("Error", "Por favor, ingrese una cantidad.")
                return
            cantidad_a_vender = int(cantidad_str)

            if cantidad_a_vender <= 0:
                app.show_popup("Error", "La cantidad debe ser mayor a 0.")
                return
            
            # OPTIMIZACIÓN: Usar el product_map para una búsqueda más rápida
            producto_original_dict = app.product_map.get(self.product_to_add.numero)
            if not producto_original_dict:
                app.show_popup("Error", "El producto no se encuentra en el inventario principal.")
                self.dismiss()
                return

            cantidad_ya_en_carrito = 0
            item_existente_en_carrito = next((item for item in self.sale_screen_ref.carrito_temp if item['numero_prod'] == self.product_to_add.numero), None)
            if item_existente_en_carrito:
                cantidad_ya_en_carrito = item_existente_en_carrito['cantidad']

            stock_real_disponible_en_inventario = producto_original_dict['cantidad'] 

            if cantidad_a_vender > (stock_real_disponible_en_inventario - cantidad_ya_en_carrito):
                 app.show_popup("Stock Insuficiente", f"No hay suficiente stock para {self.product_to_add.nombre}.\nDisponibles para añadir (real): {stock_real_disponible_en_inventario - cantidad_ya_en_carrito}")
                 return
            
            self.sale_screen_ref.add_to_cart_action_from_popup(self.product_to_add, cantidad_a_vender) 
            self.dismiss()

        except ValueError:
            app.show_popup("Error", "Ingrese una cantidad numérica válida.")
        except Exception as e:
            app.show_popup("Error Inesperado", f"Ocurrió un error en el popup de cantidad: {str(e)}")

class VueltoPopup(Popup):
    total_a_pagar = NumericProperty(0)
    sale_screen_ref = ObjectProperty(None)

    def __init__(self, total_a_pagar, sale_screen_ref, **kwargs):
        super().__init__(**kwargs)
        self.total_a_pagar = total_a_pagar
        self.sale_screen_ref = sale_screen_ref
        self.ids.popup_total_a_pagar_label.text = f"Total a Pagar: $ {int(self.total_a_pagar):,}".replace(",", "_").replace(".", ",").replace("_", ".")
        self.ids.popup_vuelto_calculado_label.text = " $0"

    def calculate_popup_vuelto(self):
        app = App.get_running_app()
        try:
            pago_str = self.ids.popup_monto_pagado_input.text
            if not pago_str:
                app.show_popup("Error ", "Ingrese el monto del pago.")
                return
            pago = float(pago_str)

            if pago < self.total_a_pagar:
                self.ids.popup_vuelto_calculado_label.text = " PAGO INSUFICIENTE"
                self.ids.popup_vuelto_calculado_label.color = (0.9, 0.2, 0.2, 1) 
                return

            vuelto = pago - self.total_a_pagar
            vuelto_f = f"$ {int(vuelto):,}".replace(",", "_").replace(".", ",").replace("_", ".")
            self.ids.popup_vuelto_calculado_label.text = f" {vuelto_f}"
            self.ids.popup_vuelto_calculado_label.color = (0.8, 0.8, 0.3, 1) 
        except ValueError:
            app.show_popup("Error", "Ingrese un monto de pago válido.")

    def accept_vuelto(self):
        if "PAGO INSUFICIENTE" not in self.ids.popup_vuelto_calculado_label.text and \
           self.ids.popup_monto_pagado_input.text.strip():
            if self.sale_screen_ref:
                self.sale_screen_ref.ids.vuelto_label.text = self.ids.popup_vuelto_calculado_label.text
            self.dismiss()
        else:
            App.get_running_app().show_popup("Error", "El pago es insuficiente o no se ha calculado el vuelto correctamente.")


# --- Clases de Pantallas y Lógica de la Aplicación ---
class MenuScreen(Screen):
    def go_to_add_product_screen(self):
        add_screen = App.get_running_app().sm.get_screen('add_product')
        add_screen.product_to_edit = None 
        App.get_running_app().sm.current = 'add_product'


class AddProductScreen(SwipeRightToMenuScreen):
    product_to_edit = ObjectProperty(None, allownone=True)
    selected_image_path = StringProperty('')

    def on_enter(self):
        self.ids.add_screen_image.source = 'agregar_producto.png'
        
        if self.product_to_edit:
            self.ids.save_button.text = "Actualizar Producto"
            self.ids.nombre_input.text = self.product_to_edit.get('nombre', '')
            self.ids.precio_input.text = str(self.product_to_edit.get('precio', ''))
            self.ids.cantidad_input.text = str(self.product_to_edit.get('cantidad', ''))
            
            image_path = self.product_to_edit.get('imagen_path', '')
            self.selected_image_path = image_path

            if image_path and os.path.exists(image_path):
                self.ids.image_preview.source = image_path
            else:
                self.ids.image_preview.source = 'placeholder.png'
        else:
            self.ids.save_button.text = "Guardar Producto"
            self.clear_inputs()

    def clear_inputs(self):
        self.ids.nombre_input.text = ""
        self.ids.precio_input.text = ""
        self.ids.cantidad_input.text = ""
        self.selected_image_path = ""
        
        self.ids.add_screen_image.source = 'agregar_producto.png'
        self.ids.add_screen_image.reload()
        self.ids.image_preview.source = 'placeholder.png'
        self.ids.image_preview.reload()
        
        self.product_to_edit = None

    def save_product_action(self): 
        app = App.get_running_app()
        nombre = self.ids.nombre_input.text.strip().capitalize()
        precio_str = self.ids.precio_input.text.strip()
        cantidad_str = self.ids.cantidad_input.text.strip()
        ruta_imagen_str = self.selected_image_path

        if not nombre or not precio_str or not cantidad_str:
            app.show_popup("Error", "Los campos Nombre, Precio y Cantidad son obligatorios.")
            return
        try:
            precio = float(precio_str)
            cantidad = int(cantidad_str)

            if precio <= 0 or cantidad < 0:
                app.show_popup("Error", "El Precio debe ser mayor a 0 y la Cantidad no puede ser negativa.")
                return

            if ruta_imagen_str and not os.path.exists(ruta_imagen_str):
                 app.show_popup("Advertencia", f"La imagen '{ruta_imagen_str}' no fue encontrada. La imagen no se mostrará.")
            elif not ruta_imagen_str:
                ruta_imagen_str = "placeholder.png" 


            if self.product_to_edit: 
                # OPTIMIZACIÓN: Búsqueda rápida en el diccionario
                found_product = app.product_map.get(self.product_to_edit['numero'])
                if found_product:
                    if found_product['nombre'].lower() != nombre.lower(): 
                        if any(p['nombre'].lower() == nombre.lower() and p['numero'] != found_product['numero'] for p in app.productos):
                            app.show_popup("Error", f"Ya existe otro producto con el nombre '{nombre}'.")
                            return

                    found_product['nombre'] = nombre
                    found_product['precio'] = precio
                    found_product['cantidad'] = cantidad
                    found_product['imagen_path'] = ruta_imagen_str
                    
                    # OPTIMIZACIÓN: Actualizar el producto en el diccionario también
                    app.product_map[found_product['numero']] = found_product
                    
                    app.show_popup("Éxito", f"Producto '{nombre}' actualizado correctamente.")
                else:
                    app.show_popup("Error", "No se pudo encontrar el producto para actualizar.")
                    return
            else: 
                if any(prod['nombre'].lower() == nombre.lower() for prod in app.productos):
                    app.show_popup("Error", f"El producto '{nombre}' ya existe en el inventario.")
                    return
                
                new_product = {
                    'numero': app.numero_producto,
                    'nombre': nombre,
                    'precio': precio,
                    'cantidad': cantidad,
                    'imagen_path': ruta_imagen_str
                }
                app.productos.append(new_product)
                
                # OPTIMIZACIÓN: Añadir el nuevo producto al diccionario
                app.product_map[app.numero_producto] = new_product
                
                app.numero_producto += 1
                app.show_popup("Éxito", f"Producto '{nombre}' agregado. [Nº {app.numero_producto - 1}] ✓")

            app.save_products_to_store() 
            self.clear_inputs()
            app.sm.current = 'view_products' 

        except ValueError:
            app.show_popup("Error", "Precio y Cantidad deben ser números válidos.")
        except Exception as e:
            app.show_popup("Error Inesperado", f"Ocurrió un error al guardar el producto: {str(e)}")

    def clear_and_go_to_menu(self): 
        self.clear_inputs()
        App.get_running_app().sm.current = 'menu'
        
    def open_file_chooser(self):
        content = BoxLayout(orientation='vertical', spacing=dp(5))
        try:
            app_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            app_path = os.getcwd()

        filechooser = FileChooserIconView(path=app_path, filters=['*.png', '*.jpg', '*.jpeg', '*.gif'])
        content.add_widget(filechooser)

        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        select_button = MySmallActionButton(text="Seleccionar")
        cancel_button = MySmallActionButton(text="Cancelar", background_color=(0.85, 0.25, 0.25, 1))
        buttons.add_widget(select_button)
        buttons.add_widget(cancel_button)
        content.add_widget(buttons)

        popup = Popup(title="Seleccionar imagen de producto", content=content, size_hint=(0.9, 0.9))
        select_button.bind(on_press=lambda x: self.file_selected(filechooser.selection, popup))
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def file_selected(self, selection, popup):
        if selection:
            file_path = selection[0]
            self.selected_image_path = file_path
            
            if os.path.exists(file_path):
                self.ids.image_preview.source = file_path
                self.ids.image_preview.reload()
        
        popup.dismiss()


class ViewProductsScreen(SwipeRightToMenuScreen): 
    def on_enter(self):
        try:
            app = App.get_running_app()
            bg_color = app.theme_config.get("product_list_bg_rgba", [0,0,0,0])
            color_instruction = self.ids.view_products_scrollview.canvas.before.get_group('bg_color')[0]
            color_instruction.rgba = bg_color
        except (AttributeError, IndexError) as e:
            print(f"Advertencia: No se pudo actualizar el color de fondo de ViewProductsScreen: {e}")
            
        self.update_products_list()
        for card_widget in self.ids.products_grid_cards.children:
            if isinstance(card_widget, ProductCard):
                card_widget.state = 'normal'

    def update_products_list(self): 
        app = App.get_running_app()
        products_grid = self.ids.products_grid_cards
        products_grid.clear_widgets() 

        if not app.productos:
            no_products_label = Label(
                text="¡No hay productos en el inventario!",
                size_hint_y=None, height=dp(60),
                font_size='19sp', halign='center',
                color=app.theme_config.get("ViewProducts_text_color", (0.9,0.9,0.92,1))
            )
            products_grid.cols = 1 
            products_grid.add_widget(no_products_label)
            return

        products_grid.cols = 2 
        sorted_productos = sorted(app.productos, key=lambda p: p['numero']) 

        for prod_dict in sorted_productos:
            card = ProductCard(
                product_data=prod_dict, 
                view_product_screen_ref=self,
                group="product_card_selector", 
                allow_no_selection=True
            )
            products_grid.add_widget(card)

    def edit_product_action(self, product_data_dict): 
        app = App.get_running_app()
        add_screen = app.sm.get_screen('add_product')
        add_screen.product_to_edit = product_data_dict 
        app.sm.current = 'add_product' 

    def delete_product_popup(self, product_data_dict): 
        app = App.get_running_app()

        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(10))
        message = Label(
            text=f"¿Seguro que quieres eliminar '{product_data_dict['nombre']}'?",
            halign='center', font_size='18sp',
            text_size=(Window.width * 0.7, None), 
            size_hint_y=None
        )
        message.bind(texture_size=message.setter('size')) 
        content_layout.add_widget(message)

        buttons_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        confirm_button = MySmallActionButton(text="Eliminar", background_color=app.theme_config.get("ExitButton_rgba", (0.85,0.25,0.25,1)))
        cancel_button = MySmallActionButton(text="Cancelar")
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        content_layout.add_widget(buttons_layout)

        popup_height = message.height + buttons_layout.height + dp(20) + dp(15) + dp(40) 

        popup = Popup(
            title="Confirmar Eliminación", title_size='20sp', title_align='center',
            content=content_layout,
            size_hint=(0.8, None), height=max(dp(220), popup_height), 
            auto_dismiss=False,
            separator_color=app.theme_config.get("Popup_separator_color", (0.3,0.3,0.3,1)),
            background_color = (0,0,0,0), background = '' 
        )
        with content_layout.canvas.before:
            Color(rgba=app.theme_config.get("Popup_bg_rgba", (0.1, 0.1, 0.12, 0.98)))
            content_layout.bg_rect = RoundedRectangle(pos=content_layout.pos, size=content_layout.size, radius=[dp(10)])
        def update_bg(instance, _): 
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        content_layout.bind(pos=update_bg, size=update_bg)


        confirm_button.bind(on_press=lambda x: self.confirm_delete_product(product_data_dict, popup))
        cancel_button.bind(on_press=popup.dismiss)
        popup.open()

    def confirm_delete_product(self, product_to_delete_dict, popup_instance): 
        app = App.get_running_app()
        product_numero = product_to_delete_dict['numero']
        
        app.productos = [p for p in app.productos if p['numero'] != product_numero]
        
        # OPTIMIZACIÓN: Eliminar el producto del diccionario
        if product_numero in app.product_map:
            del app.product_map[product_numero]
            
        app.save_products_to_store() 
        app.show_popup("Eliminado", f"Producto '{product_to_delete_dict['nombre']}' eliminado correctamente.")
        self.update_products_list() 
        popup_instance.dismiss()


class SaleScreen(SwipeRightToMenuScreen): 
    carrito_temp = ListProperty([]) 
    total_temp = NumericProperty(0.0) 
    selected_product_widget = ObjectProperty(None, allownone=True) 

    def on_enter(self):
        try:
            app = App.get_running_app()
            bg_color = app.theme_config.get("product_list_bg_rgba", [0,0,0,0])
            color_instruction = self.ids.sale_products_scrollview.canvas.before.get_group('bg_color')[0]
            color_instruction.rgba = bg_color
        except (AttributeError, IndexError) as e:
            print(f"Advertencia: No se pudo actualizar el color de fondo de SaleScreen: {e}")
            
        self.reset_sale_screen_state() 
        if hasattr(self.ids, 'add_to_cart_button'):
             self.ids.add_to_cart_button.disabled = True 

    def reset_sale_screen_state(self, *args): # Se añade *args para que Clock pueda llamarlo
        self.carrito_temp = []
        self.total_temp = 0.0
        if self.selected_product_widget:
            if self.selected_product_widget.parent:
                self.selected_product_widget.state = 'normal'
            self.selected_product_widget = None
        
        if hasattr(self.ids, 'vuelto_label'): 
            self.ids.vuelto_label.text = "$0"
        
        self.update_products_for_sale() 
        self.update_cart_display()      

        if hasattr(self.ids, 'add_to_cart_button'): 
            self.ids.add_to_cart_button.disabled = True


    def update_products_for_sale(self): 
        app = App.get_running_app()
        sale_products_layout = self.ids.sale_products_grid
        sale_products_layout.clear_widgets()

        quantities_in_cart = {item['numero_prod']: item['cantidad'] for item in self.carrito_temp}
        productos_ordenados = sorted(app.productos, key=lambda p: p['nombre'])
        products_actually_displayed = 0

        for prod_dict_original in productos_ordenados:
            stock_in_main_inventory = prod_dict_original['cantidad']
            already_in_cart_qty = quantities_in_cart.get(prod_dict_original['numero'], 0)
            effective_stock_for_card = stock_in_main_inventory - already_in_cart_qty

            if effective_stock_for_card > 0: 
                prod_data_obj_for_row = ProductoData(
                    numero=prod_dict_original['numero'],
                    nombre=prod_dict_original['nombre'],
                    precio=prod_dict_original['precio'],
                    cantidad=effective_stock_for_card, 
                    precio_formateado=f"{int(prod_dict_original['precio']):,}".replace(",", "_").replace(".", ",").replace("_", "."),
                    imagen_path=prod_dict_original.get('imagen_path', 'placeholder.png')
                )
                product_row_widget = Factory.SelectableProductRow(product_dict=prod_data_obj_for_row)
                product_row_widget.bind(on_press=self.on_product_button_press)
                sale_products_layout.add_widget(product_row_widget)
                products_actually_displayed += 1
        
        if products_actually_displayed == 0:
            no_stock_label = Label(text="No hay productos con stock disponible para agregar.",
                                   size_hint_y=None, height=dp(48),
                                   font_size='18sp', halign='center', color=(0.8,0.8,0.8,1))
            sale_products_layout.cols = 1 
            sale_products_layout.add_widget(no_stock_label)
        else:
            sale_products_layout.cols = 4 
            

    def on_product_button_press(self, instance_row_widget): 
        if instance_row_widget.state == 'down': 
            if self.selected_product_widget and self.selected_product_widget != instance_row_widget:
                self.selected_product_widget.state = 'normal' 
            self.selected_product_widget = instance_row_widget
            if hasattr(self.ids, 'add_to_cart_button'):
                self.ids.add_to_cart_button.disabled = False 
        else: 
            if self.selected_product_widget == instance_row_widget: 
                self.selected_product_widget = None
                if hasattr(self.ids, 'add_to_cart_button'):
                    self.ids.add_to_cart_button.disabled = True 


    def open_quantity_popup(self): 
        app = App.get_running_app()
        if not self.selected_product_widget:
            app.show_popup("Error", "Ningún producto seleccionado.")
            return

        product_data_for_popup = self.selected_product_widget.product_dict
        
        # OPTIMIZACIÓN: Búsqueda rápida en el diccionario
        producto_actual_en_inventario_dict = app.product_map.get(product_data_for_popup.numero)
        
        if product_data_for_popup.cantidad <= 0 or (producto_actual_en_inventario_dict and producto_actual_en_inventario_dict['cantidad'] <=0) :
            app.show_popup("Stock Agotado", f"El producto {product_data_for_popup.nombre} ya no tiene stock disponible para agregar.")
            self.update_products_for_sale() 
            if hasattr(self.ids, 'add_to_cart_button'):
                 self.ids.add_to_cart_button.disabled = True
            if self.selected_product_widget: 
                 self.selected_product_widget.state = 'normal'
                 self.selected_product_widget = None
            return

        popup = QuantityPopup(sale_screen_ref=self, product_to_add=product_data_for_popup)
        popup.open()


    def add_to_cart_action_from_popup(self, product_data_obj_del_boton, cantidad_a_vender): 
        app = App.get_running_app()
        # OPTIMIZACIÓN: Búsqueda rápida en el diccionario
        producto_original_dict = app.product_map.get(product_data_obj_del_boton.numero)
        
        if not producto_original_dict:
            app.show_popup("Error Crítico", "Producto no encontrado en el inventario principal.")
            return

        cantidad_ya_en_carrito = 0
        item_existente_en_carrito = next((item for item in self.carrito_temp if item['numero_prod'] == producto_original_dict['numero']), None)
        if item_existente_en_carrito:
            cantidad_ya_en_carrito = item_existente_en_carrito['cantidad']

        stock_real_disponible_en_inventario = producto_original_dict['cantidad']

        if cantidad_a_vender > (stock_real_disponible_en_inventario - cantidad_ya_en_carrito):
            mensaje_stock = f"Stock insuficiente para {producto_original_dict['nombre']}.\n"
            disponible_para_anadir = stock_real_disponible_en_inventario - cantidad_ya_en_carrito
            mensaje_stock += f"Puedes añadir hasta {disponible_para_anadir} más." if disponible_para_anadir > 0 else "No hay más stock disponible para añadir."
            app.show_popup("Stock Insuficiente", mensaje_stock)
            return

        if item_existente_en_carrito: 
            item_existente_en_carrito['cantidad'] += cantidad_a_vender
        else: 
            self.carrito_temp.append({
                'numero_prod': producto_original_dict['numero'],
                'nombre': producto_original_dict['nombre'],
                'cantidad': cantidad_a_vender,
                'precio_unitario': producto_original_dict['precio'], 
                'imagen_path': producto_original_dict.get('imagen_path', 'placeholder.png')
            })
        self.total_temp += producto_original_dict['precio'] * cantidad_a_vender 
        
        self.update_cart_display() 
        self.update_products_for_sale() 

        if self.selected_product_widget: 
            self.selected_product_widget.state = 'normal'
            self.selected_product_widget = None
        if hasattr(self.ids, 'add_to_cart_button'):
            self.ids.add_to_cart_button.disabled = True 

    def update_cart_display(self):
        cart_items_layout = self.ids.cart_items_layout
        cart_items_layout.clear_widgets()
        
        text_color_cart_empty = App.get_running_app().theme_config.get("CartItems_text_color", (0.92,0.92,0.95,1))

        if not self.carrito_temp:
            cart_items_layout.cols = 1 
            cart_items_layout.add_widget(Label(
                text="Carrito vacío",
                size_hint_y=None,
                height=dp(65), 
                font_size='19sp',
                color=text_color_cart_empty,
                halign='center',
                valign='middle'
            ))
        else:
            cart_items_layout.cols = 4 
            for item_dict in self.carrito_temp:
                cart_card = CartItemCard(item_data=item_dict)
                cart_items_layout.add_widget(cart_card)

        total_general_f = f"$ {int(self.total_temp):,}".replace(",", "_").replace(".", ",").replace("_", ".")
        self.ids.total_label.text = f"Total: {total_general_f}"
        
        if self.total_temp == 0 and hasattr(self.ids, 'vuelto_label'):
             self.ids.vuelto_label.text = "$0"


    def open_vuelto_popup(self): 
        app = App.get_running_app()
        if self.total_temp == 0:
            app.show_popup("Carrito Vacío", "No hay productos para calcular el vuelto.")
            return
        popup = VueltoPopup(total_a_pagar=self.total_temp, sale_screen_ref=self)
        popup.open()

    # --- CÓDIGO SÚPER OPTIMIZADO ---
    def confirm_purchase_action(self): 
        app = App.get_running_app()
        gif_duration = 2.5
        
        if not self.carrito_temp:
            app.show_popup("Carrito Vacío", "No hay productos para confirmar la compra.")
            return

        # 1. Validación de stock usando el rápido product_map
        for item_venta in self.carrito_temp:
            # Búsqueda instantánea en el diccionario
            prod_en_stock_dict = app.product_map.get(item_venta['numero_prod'])
            if not prod_en_stock_dict or prod_en_stock_dict['cantidad'] < item_venta['cantidad']:
                app.show_popup("Error de Stock Final", f"Stock insuficiente para '{item_venta['nombre']}'. Venta cancelada.")
                # No reseteamos la UI aquí para no causar lag, el usuario puede corregir el carro.
                return

        # 2. Mostrar el GIF INMEDIATAMENTE para feedback del usuario.
        app.show_gif_popup('listo.gif', duration=gif_duration)

        # 3. Preparar todos los datos en memoria (esto es rápido)
        productos_vendidos_historial = {}
        for item_venta in self.carrito_temp:
            prod_a_actualizar = app.product_map[item_venta['numero_prod']]
            prod_a_actualizar['cantidad'] -= item_venta['cantidad']

            productos_vendidos_historial[str(item_venta['numero_prod'])] = {
                'nombre': item_venta['nombre'],
                'cantidad': item_venta['cantidad'],
                'precio_unitario_venta': item_venta['precio_unitario'],
                'imagen_path': item_venta.get('imagen_path', 'placeholder.png')
            }

        fecha_venta = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        app.historial_ventas.append({'fecha': fecha_venta, 'productos': productos_vendidos_historial, 'total': self.total_temp})

        # 4. Programar las operaciones lentas (I/O de disco) con un pequeño retraso.
        Clock.schedule_once(lambda dt: app.save_products_to_store(), 0.1)
        Clock.schedule_once(lambda dt: app.save_sales_history_to_store(), 0.1)
        
        # 5. Programar la reconstrucción de la UI (que también es pesada)
        #    para DESPUÉS de que el GIF haya desaparecido.
        Clock.schedule_once(self.reset_sale_screen_state, gif_duration)


    def cancel_purchase_action(self): 
        self.reset_sale_screen_state() 
        App.get_running_app().show_popup("Cancelado", "Compra cancelada.")

    def go_to_menu_action(self): 
        self.reset_sale_screen_state() 
        if self.manager:
            self.manager.current = 'menu'

class HistoryScreen(SwipeRightToMenuScreen): 
    def on_enter(self):
        self.update_history_list()

    def update_history_list(self): 
        app = App.get_running_app()
        history_layout = self.ids.history_layout
        history_layout.clear_widgets()

        history_item_font_size = '18sp'
        history_total_font_size = '20sp'
        text_color_history = app.theme_config.get("History_text_color", (0.9,0.9,0.95,1))
        img_size_hist = dp(45) 
        text_total_dia_default = "Total Venta del Día: $ 0"

        if not app.historial_ventas:
            history_layout.add_widget(Label(text="No hay historial de ventas.", size_hint_y=None, height=dp(45), font_size=history_item_font_size, color=text_color_history))
            if hasattr(self.ids, 'total_dia_label'):
                self.ids.total_dia_label.text = text_total_dia_default
            return

        for venta in reversed(app.historial_ventas): 
            venta_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8), padding=(dp(12)))
            venta_box.bind(minimum_height=venta_box.setter('height')) 

            with venta_box.canvas.before:
                Color(rgba=app.theme_config.get("History_entry_bg_rgba", [0.18,0.20,0.23,0.75]))
                venta_box.bg_rect_instruction = RoundedRectangle(size=venta_box.size, pos=venta_box.pos, radius=[dp(10)])

            def update_history_entry_bg(instance, _): 
                if hasattr(instance, 'bg_rect_instruction') and instance.bg_rect_instruction:
                    instance.bg_rect_instruction.pos = instance.pos
                    instance.bg_rect_instruction.size = instance.size
            venta_box.bind(pos=update_history_entry_bg, size=update_history_entry_bg)

            fecha_label = Label(text=f"Fecha: {venta['fecha']}", bold=True, size_hint_y=None, color=text_color_history, font_size=history_item_font_size, halign='left', valign='top')
            fecha_label.bind(width=lambda instance, val: setattr(instance, 'text_size', (val - dp(24), None)))
            fecha_label.bind(texture_size=lambda instance, val: setattr(instance, 'height', val[1] + dp(8)))
            venta_box.add_widget(fecha_label)

            for prod_num_key, datos_prod_vendido in venta['productos'].items():
                producto_item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=dp(8), height=img_size_hist + dp(4))

                imagen_path_historial = datos_prod_vendido.get('imagen_path', "placeholder.png")
                if not os.path.exists(imagen_path_historial): 
                    imagen_path_historial = "placeholder.png"

                img_widget_hist = Image(
                    source=imagen_path_historial, size_hint_x=None, width=img_size_hist,
                    size_hint_y=None, height=img_size_hist,
                    fit_mode="contain", 
                    pos_hint={'center_y': 0.5}
                )
                producto_item_layout.add_widget(img_widget_hist)

                nombre_prod = datos_prod_vendido['nombre']
                cantidad_vendida = datos_prod_vendido['cantidad']
                precio_unit_venta = datos_prod_vendido['precio_unitario_venta']
                precio_total_item_formateado = f"$ {int(precio_unit_venta * cantidad_vendida):,}".replace(",", "_").replace(".", ",").replace("_", ".")

                texto_producto = f"{nombre_prod} ({cantidad_vendida} u.)\nTotal Ítem: {precio_total_item_formateado}"
                prod_label_details = Label(text=texto_producto, size_hint_y=None, font_size='16sp',
                                          color=text_color_history, halign='left', valign='center')
                prod_label_details.bind(width=lambda instance, val: setattr(instance, 'text_size', (val - dp(10), None)))
                prod_label_details.bind(texture_size=lambda instance, val: setattr(instance, 'height', max(img_size_hist, val[1]))) 
                producto_item_layout.add_widget(prod_label_details)
                venta_box.add_widget(producto_item_layout)

            total_formateado = f"$ {int(venta['total']):,}".replace(",", "_").replace(".", ",").replace("_", ".")
            total_venta_label = Label(text=f"  Total Venta: {total_formateado}", size_hint_y=None, color=app.theme_config.get("History_total_text_color", (0.85,0.85,0.3,1)), bold=True, font_size=history_total_font_size, halign='left', valign='top')
            total_venta_label.bind(width=lambda instance, val: setattr(instance, 'text_size', (val - dp(24), None)))
            total_venta_label.bind(texture_size=lambda instance, val: setattr(instance, 'height', val[1] + dp(10)))
            venta_box.add_widget(total_venta_label)
            history_layout.add_widget(venta_box)

        hoy_str = datetime.datetime.now().strftime("%d/%m/%Y")
        total_ventas_hoy = 0.0

        for venta_hist in app.historial_ventas:
            fecha_venta_str = venta_hist['fecha'].split(' ')[0] 
            if fecha_venta_str == hoy_str:
                total_ventas_hoy += venta_hist['total']

        total_hoy_formateado = f"$ {int(total_ventas_hoy):,}".replace(",", "_").replace(".", ",").replace("_", ".")

        if hasattr(self.ids, 'total_dia_label'):
            self.ids.total_dia_label.text = f"Total Ventas del Día: {total_hoy_formateado}"

class SettingsScreen(SwipeRightToMenuScreen): 
    preview_theme_config = DictProperty({}) 
    PRESET_BUTTON_IDS = { 
        "btn_action_default": [0.25,0.45,0.65],
        "btn_action_green": [0.2,0.6,0.3],
        "btn_action_red": [0.7,0.2,0.2],
        "btn_action_orange": [0.9,0.5,0.1],
    }

    def on_enter(self, *args): 
        try:
            app = App.get_running_app()
            bg_color = app.theme_config.get("SettingsScreen_bg_rgba", [0.12, 0.13, 0.15, 0.85])
            color_instruction = self.ids.settings_root_layout.canvas.before.get_group('bg_color')[0]
            color_instruction.rgba = bg_color
        except (AttributeError, IndexError) as e:
            print(f"Advertencia: No se pudo actualizar el color de fondo de SettingsScreen: {e}")
            
        app = App.get_running_app()
        self.preview_theme_config = {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in app.theme_config.items()}
        self.update_ui_from_preview() 


    def update_ui_from_preview(self): 
        app = App.get_running_app()
        action_button_rgb_tuple = tuple(self.preview_theme_config.get("MyActionButton_rgb", app.default_theme_settings["MyActionButton_rgb"]))
        active_button_id = None
        for btn_id, preset_color_list in self.PRESET_BUTTON_IDS.items():
            if list(action_button_rgb_tuple) == preset_color_list:
                active_button_id = btn_id
                break
        for btn_id in self.PRESET_BUTTON_IDS.keys():
            if hasattr(self.ids, btn_id):
                button_widget = self.ids[btn_id]
                button_widget.state = 'down' if btn_id == active_button_id else 'normal'

        self.ids.button_opacity_slider.value = float(self.preview_theme_config.get("button_opacity", app.default_theme_settings["button_opacity"]))
        if hasattr(self.ids, 'button_opacity_label'):
             self.ids.button_opacity_label.text = f"{self.ids.button_opacity_slider.value:.2f}"

        self.ids.card_opacity_slider.value = float(self.preview_theme_config.get("card_background_opacity", app.default_theme_settings["card_background_opacity"]))
        if hasattr(self.ids, 'card_opacity_label'):
             self.ids.card_opacity_label.text = f"{self.ids.card_opacity_slider.value:.2f}"

        self.ids.product_list_opacity_slider.value = float(self.preview_theme_config.get("product_list_bg_opacity", app.default_theme_settings["product_list_bg_opacity"]))
        if hasattr(self.ids, 'product_list_opacity_label'):
            self.ids.product_list_opacity_label.text = f"{self.ids.product_list_opacity_slider.value:.2f}"

        self.ids.settings_bg_opacity_slider.value = float(self.preview_theme_config.get("settings_screen_bg_opacity", app.default_theme_settings["settings_screen_bg_opacity"]))
        if hasattr(self.ids, 'settings_bg_opacity_label'):
            self.ids.settings_bg_opacity_label.text = f"{self.ids.settings_bg_opacity_slider.value:.2f}"


    def update_preview_theme(self, key, value): 
        app_instance = App.get_running_app()
        try:
            default_val_type_sample = app_instance.default_theme_settings.get(key) 
            if isinstance(default_val_type_sample, float) or key in ["button_opacity", "product_list_bg_opacity", "settings_screen_bg_opacity", "card_background_opacity"]:
                try:
                    self.preview_theme_config[key] = float(value)
                except ValueError:
                    app_instance.show_popup("Error de Valor", f"El valor '{value}' para '{key}' debe ser numérico decimal.")
                    return
            elif isinstance(default_val_type_sample, int):
                try:
                    self.preview_theme_config[key] = int(float(value)) 
                except ValueError:
                    app_instance.show_popup("Error de Valor", f"El valor '{value}' para '{key}' debe ser numérico entero.")
                    return
            else: 
                self.preview_theme_config[key] = value

        except ValueError:
            app_instance.show_popup("Error de Valor", f"El valor '{value}' para '{key}' no es válido.")
        except Exception as e:
            app_instance.show_popup("Error", f"Error actualizando la vista previa del tema: {e}")

        slider_label_map = {
            "button_opacity": "button_opacity_label",
            "product_list_bg_opacity": "product_list_opacity_label",
            "settings_screen_bg_opacity": "settings_bg_opacity_label",
            "card_background_opacity": "card_opacity_label"
        }
        if key in slider_label_map:
            label_id = slider_label_map[key]
            if hasattr(self.ids, label_id):
                label_widget = self.ids[label_id]
                label_widget.text = f"{self.preview_theme_config.get(key, 0.0):.2f}" 


    def set_button_color_preset(self, button_key_rgb, color_rgb): 
        self.preview_theme_config[button_key_rgb] = list(color_rgb)
        
    def apply_and_save_theme_changes(self):
        loading_popup = AttractiveLoadingPopup()
        loading_popup.open()
        Clock.schedule_once(lambda dt: self._perform_apply_and_save(loading_popup), 0.2)

    def _perform_apply_and_save(self, loading_popup):
        app = App.get_running_app()
        try:
            final_theme_to_apply = app._prepare_theme_dict(self.preview_theme_config.copy())
            app.save_app_theme(app.theme_store_file, self.preview_theme_config)
            
            app.theme_config = final_theme_to_apply
            app.force_ui_refresh()

        except Exception as e:
            print(f"ERROR: Ocurrió un error al aplicar el tema: {e}")
            app.show_popup("Error", "No se pudieron aplicar los cambios.")
        finally:
            loading_popup.dismiss()

    def restore_default_preview(self): 
        app = App.get_running_app()
        self.preview_theme_config = {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in app.default_theme_settings.items()}
        self.update_ui_from_preview() 
        app.show_popup("Configuración", "Valores predeterminados cargados.\nPresiona 'Guardar Cambios' para aplicar.")


class MyApp(App): 
    productos = ListProperty([]) 
    historial_ventas = ListProperty([]) 
    numero_producto = NumericProperty(1) 
    sm = ObjectProperty(None) 
    theme_config = DictProperty({}) 
    background_image_widget = ObjectProperty(None, allownone=True) 

    # OPTIMIZACIÓN: Añadimos un diccionario para búsquedas rápidas
    product_map = DictProperty({})

    theme_store_file = StringProperty("current_theme.json") 
    product_store_file = StringProperty("productos_data.json") 
    sales_history_store_file = StringProperty("historial_ventas.json") 

    default_theme_settings = {
        "app_background_value_image": "fondo.png", 
        "MyActionButton_rgb": [0.25, 0.45, 0.65], 
        "MySmallActionButton_rgb": [0.3, 0.6, 0.4], 
        "button_opacity": 1.0, 
        "MyActionButton_rgba": [0.25, 0.45, 0.65, 1.0],
        "MySmallActionButton_rgba": [0.3, 0.6, 0.4, 1.0],
        "product_list_bg_base_color_rgb": [0.12, 0.13, 0.15], 
        "product_list_bg_opacity": 0.0, 
        "product_list_bg_rgba": [0.12, 0.13, 0.15, 0.0], 
        "card_background_opacity": 1.0, 
        "ProductCard_bg_normal_rgb": [0.22, 0.24, 0.27], 
        "ProductCard_bg_selected_rgb": [0.35, 0.55, 0.8], 
        "ProductCard_border_normal_rgba": [0.32, 0.34, 0.37, 1], 
        "ProductCard_border_selected_rgba": [0.5, 0.7, 0.95, 1], 
        "ProductCard_DeleteButton_rgba": [0.85,0.25,0.25,1], 
        "SelectableProductRow_normal_rgb": [0.22, 0.24, 0.27], 
        "SelectableProductRow_selected_rgb": [0.35, 0.55, 0.8],
        "SelectableProductRow_normal_rgba": [0.22, 0.24, 0.27, 1.0], 
        "SelectableProductRow_selected_rgba": [0.35, 0.55, 0.8, 1.0], 
        "SelectableProductRow_border_color_normal": [0.32, 0.34, 0.37, 1], 
        "SelectableProductRow_border_color_selected": [0.5, 0.7, 0.95, 1],  
        "settings_screen_bg_base_color_rgb": [0.12, 0.13, 0.15], 
        "settings_screen_bg_opacity": 0.9, 
        "SettingsScreen_bg_rgba": [0.12, 0.13, 0.15, 0.9], 
        "MyTitleLabel_color": [0.9, 0.9, 0.95, 1],
        "MyHeaderLabel_color": [0.85, 0.85, 0.9, 1],
        "MyInputLabel_color": [0.85,0.85,0.9,1],
        "ExitButton_rgba": [0.85, 0.25, 0.25, 1], 
        "Popup_Accept_Button_rgba": [0.2, 0.65, 0.3, 1.0], 
        "Popup_Cancel_Button_rgba": [0.85, 0.25, 0.25, 1.0], 
        "Popup_bg_rgba": [0.12,0.12,0.15,0.97], 
        "Popup_separator_color": [0.3,0.3,0.3,1], 
        "ViewProducts_text_color": [0.9,0.9,0.92,1], 
        "CartItems_text_color": [0.92,0.92,0.95,1], 
        "CartItemCard_bg_rgb": [0.20, 0.22, 0.25], 
        "CartItemCard_bg_rgba": [0.20, 0.22, 0.25, 1.0], 
        "History_text_color": [0.9,0.9,0.95,1], 
        "History_total_text_color": [0.85,0.85,0.3,1], 
        "History_entry_bg_rgba": [0.18,0.20,0.23,0.75], 
    }

    def build(self): 
        self.load_app_theme(self.theme_store_file, apply_defaults_on_fail=True) 
        self.load_products_from_store() 
        self.load_sales_history_from_store() 

        root_layout = FloatLayout() 
        self.background_image_widget = Image(
            source="fondo.png",
            fit_mode='fill', size_hint=(1,1),
            pos_hint={'center_x':0.5, 'center_y':0.5},
            opacity=0 
        )
        root_layout.add_widget(self.background_image_widget, index=1) 

        self.sm = ScreenManager() 
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(AddProductScreen(name='add_product'))
        self.sm.add_widget(ViewProductsScreen(name='view_products'))
        self.sm.add_widget(SaleScreen(name='sale'))
        self.sm.add_widget(HistoryScreen(name='history'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        root_layout.add_widget(self.sm) 

        self.bind(theme_config=self.apply_theme_to_app_elements) 
        self.apply_theme_to_app_elements() 
        return root_layout

    def force_ui_refresh(self):
        print("INFO: Forzando refresco de la UI para todas las pantallas.")
        for screen in self.sm.screens:
            if self.sm.current == screen.name and hasattr(screen, 'on_enter'):
                screen.on_enter()
            
            if screen.name == 'view_products' and hasattr(screen, 'update_products_list'):
                screen.update_products_list()
            elif screen.name == 'sale':
                if hasattr(screen, 'update_products_for_sale'):
                    screen.update_products_for_sale()
                if hasattr(screen, 'update_cart_display'):
                    screen.update_cart_display()
            elif screen.name == 'history' and hasattr(screen, 'update_history_list'):
                screen.update_history_list()
    
    def on_start(self): 
        if self.root and self.sm and self.sm.has_screen('settings'):
            settings_screen = self.sm.get_screen('settings')
            if isinstance(settings_screen, SettingsScreen):
                 settings_screen.preview_theme_config = {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in self.theme_config.items()}
                 settings_screen.update_ui_from_preview()

    def load_products_from_store(self): 
        store = JsonStore(self.product_store_file)
        if store.exists('productos_guardados'):
            try:
                loaded_data = store.get('productos_guardados')
                self.productos = loaded_data.get('lista_productos', [])
                self.numero_producto = loaded_data.get('proximo_numero', 1)
                
                # OPTIMIZACIÓN: Crear el diccionario de productos al cargar
                self.product_map = {p['numero']: p for p in self.productos}
                
                print(f"Productos cargados. Próximo Nº: {self.numero_producto}")
            except Exception as e:
                print(f"Error al cargar productos: {e}. Iniciando con datos vacíos.")
                self.productos = []
                self.numero_producto = 1
                self.product_map = {}
        else:
            print("Archivo de productos no encontrado. Iniciando con datos vacíos.")
            self.productos = []
            self.numero_producto = 1
            self.product_map = {}

    def save_products_to_store(self): 
        store = JsonStore(self.product_store_file)
        try:
            store.put('productos_guardados',
                      lista_productos=list(self.productos),
                      proximo_numero=self.numero_producto)
            print("Productos guardados.")
        except Exception as e:
            print(f"Error al guardar productos: {e}")
            self.show_popup("Error de Guardado", f"No se pudieron guardar los productos: {e}")

    def load_sales_history_from_store(self): 
        store = JsonStore(self.sales_history_store_file)
        if store.exists('historial_ventas_guardado'):
            try:
                self.historial_ventas = store.get('historial_ventas_guardado')['lista_historial']
                print("Historial de ventas cargado.")
            except Exception as e:
                print(f"Error al cargar historial de ventas: {e}. Iniciando con historial vacío.")
                self.historial_ventas = []
        else:
            print("Archivo de historial de ventas no encontrado. Iniciando con historial vacío.")
            self.historial_ventas = []

    def save_sales_history_to_store(self): 
        store = JsonStore(self.sales_history_store_file)
        try:
            store.put('historial_ventas_guardado', lista_historial=list(self.historial_ventas))
            print("Historial de ventas guardado.")
        except Exception as e:
            print(f"Error al guardar historial de ventas: {e}")
            self.show_popup("Error de Guardado", f"No se pudo guardar el historial de ventas: {e}")


    def _parse_color_string(self, color_str, default_color): 
        try:
            cleaned_str = str(color_str).replace('[','').replace(']','').replace(' ','')
            parts = [float(p.strip()) for p in cleaned_str.split(',') if p.strip()]
            if len(parts) == 3 or len(parts) == 4:
                if len(parts) == 3 and len(default_color) == 4: 
                    parts.append(1.0)
                return [max(0.0, min(1.0, x)) for x in parts][:len(default_color)] 
            return list(default_color) 
        except Exception:
            return list(default_color)

    def _prepare_theme_dict(self, source_dict_raw): 
        prepared = {k: (list(v) if isinstance(v, (list, tuple)) else v) for k, v in self.default_theme_settings.items()}

        for key, raw_value in source_dict_raw.items():
            if key not in prepared: continue 
            default_val_sample = self.default_theme_settings[key] 

            if isinstance(default_val_sample, list): 
                if isinstance(raw_value, str): 
                    parsed_color = self._parse_color_string(raw_value, default_val_sample)
                    if parsed_color and (len(parsed_color) == len(default_val_sample) or (len(parsed_color) == 3 and len(default_val_sample) == 4)):
                        prepared[key] = parsed_color
                elif isinstance(raw_value, list) and all(isinstance(x, (int, float)) for x in raw_value):
                    valid_raw_color = [max(0.0, min(1.0, float(x))) for x in raw_value] 
                    if len(valid_raw_color) == len(default_val_sample):
                        prepared[key] = valid_raw_color
                    elif len(valid_raw_color) == 3 and len(default_val_sample) == 4: 
                        prepared[key] = valid_raw_color + [1.0]
            elif isinstance(default_val_sample, float):
                try: prepared[key] = float(raw_value)
                except (ValueError, TypeError): pass 
            elif isinstance(default_val_sample, str):
                 prepared[key] = str(raw_value)
            elif isinstance(default_val_sample, int):
                try: prepared[key] = int(raw_value)
                except (ValueError, TypeError): pass
            else: 
                 prepared[key] = raw_value

        button_opacity = float(prepared.get("button_opacity", self.default_theme_settings["button_opacity"]))
        for btn_prefix in ["MyActionButton", "MySmallActionButton"]:
            rgb_key = f"{btn_prefix}_rgb"
            rgba_key = f"{btn_prefix}_rgba"
            base_rgb = list(prepared.get(rgb_key, self.default_theme_settings[rgb_key]))
            prepared[rgba_key] = base_rgb[:3] + [button_opacity]

        card_op = float(prepared.get("card_background_opacity", self.default_theme_settings["card_background_opacity"]))
        
        pc_norm_rgb = list(prepared.get("ProductCard_bg_normal_rgb", self.default_theme_settings["ProductCard_bg_normal_rgb"]))
        prepared["ProductCard_bg_normal_rgba"] = pc_norm_rgb[:3] + [card_op]
        pc_sel_rgb = list(prepared.get("ProductCard_bg_selected_rgb", self.default_theme_settings["ProductCard_bg_selected_rgb"]))
        prepared["ProductCard_bg_selected_rgba"] = pc_sel_rgb[:3] + [card_op]

        spr_norm_rgb = list(prepared.get("SelectableProductRow_normal_rgb", self.default_theme_settings["SelectableProductRow_normal_rgb"]))
        prepared["SelectableProductRow_normal_rgba"] = spr_norm_rgb[:3] + [card_op]
        spr_sel_rgb = list(prepared.get("SelectableProductRow_selected_rgb", self.default_theme_settings["SelectableProductRow_selected_rgb"]))
        prepared["SelectableProductRow_selected_rgba"] = spr_sel_rgb[:3] + [card_op]

        cic_rgb = list(prepared.get("CartItemCard_bg_rgb", self.default_theme_settings["CartItemCard_bg_rgb"]))
        prepared["CartItemCard_bg_rgba"] = cic_rgb[:3] + [card_op]
        
        prod_list_base_rgb = list(prepared.get("product_list_bg_base_color_rgb", self.default_theme_settings["product_list_bg_base_color_rgb"]))
        prod_list_opacity = float(prepared.get("product_list_bg_opacity", self.default_theme_settings["product_list_bg_opacity"]))
        prepared["product_list_bg_rgba"] = prod_list_base_rgb[:3] + [prod_list_opacity]

        settings_bg_base_rgb = list(prepared.get("settings_screen_bg_base_color_rgb", self.default_theme_settings["settings_screen_bg_base_color_rgb"]))
        settings_bg_opacity = float(prepared.get("settings_screen_bg_opacity", self.default_theme_settings["settings_screen_bg_opacity"]))
        prepared["SettingsScreen_bg_rgba"] = settings_bg_base_rgb[:3] + [settings_bg_opacity]
        
        direct_color_keys = [
            "ExitButton_rgba", "Popup_Accept_Button_rgba", "Popup_Cancel_Button_rgba",
            "Popup_bg_rgba", "MyTitleLabel_color", "MyHeaderLabel_color", "MyInputLabel_color",
            "ViewProducts_text_color", "CartItems_text_color", 
            "History_text_color", "History_total_text_color", "History_entry_bg_rgba", "Popup_separator_color",
            "ProductCard_border_normal_rgba", "ProductCard_border_selected_rgba",
            "SelectableProductRow_border_color_normal", "SelectableProductRow_border_color_selected",
            "ProductCard_DeleteButton_rgba"
        ]
        for key in direct_color_keys:
            val = prepared.get(key)
            default_val = list(self.default_theme_settings[key]) 
            if isinstance(val, str): 
                 parsed = self._parse_color_string(val, default_val)
                 prepared[key] = parsed if parsed else default_val
            elif not (isinstance(val, list) and all(isinstance(x, (int, float)) for x in val) and \
                      (len(val) == 3 or len(val) == 4)): 
                prepared[key] = default_val 
            elif len(val) == 3 and len(default_val) == 4: 
                prepared[key] = val + [1.0]
            elif len(val) == 4 and len(default_val) == 3: 
                 prepared[key] = val[:3]
            else: 
                 prepared[key] = list(val) 
        return prepared


    def apply_theme_to_app_elements(self, *args): 
        bg_image_path = self.theme_config.get("app_background_value_image", "fondo.png")

        if self.background_image_widget: 
            try:
                if not os.path.exists(bg_image_path): 
                    print(f"ERROR: Imagen de fondo '{bg_image_path}' no encontrada. Se usará un color sólido de respaldo.")
                    Window.clearcolor = (0.07, 0.07, 0.1, 1)
                    self.background_image_widget.source = '' 
                    self.background_image_widget.opacity = 0 
                else: 
                    if self.background_image_widget.source != bg_image_path: 
                        self.background_image_widget.source = bg_image_path
                    self.background_image_widget.reload() 
                    self.background_image_widget.opacity = 1 
                    Window.clearcolor = (0,0,0,0) 
            except Exception as e:
                print(f"Error al cargar imagen de fondo '{bg_image_path}': {e}. Se usará un color sólido de respaldo.")
                Window.clearcolor = (0.07, 0.07, 0.1, 1)
                self.background_image_widget.source = ''
                self.background_image_widget.opacity = 0
        else: 
             print("ADVERTENCIA: background_image_widget no existe.")
             Window.clearcolor = (0.07, 0.07, 0.1, 1)


    def load_app_theme(self, filename, apply_defaults_on_fail=True, return_raw=False): 
        store = JsonStore(filename)
        raw_loaded_theme_data = {}
        success = False
        if store.exists('theme_settings'):
            try:
                stored_data = store.get('theme_settings')
                if 'config' in stored_data and isinstance(stored_data['config'], dict) and stored_data['config']:
                    raw_loaded_theme_data = stored_data['config']
                    success = True
                    print(f"Tema '{filename}' cargado desde JSON.")
                else:
                    print(f"Archivo de tema '{filename}' contiene datos vacíos o con estructura incorrecta en 'config'.")
            except Exception as e:
                print(f"Error al leer datos del tema desde '{filename}': {e}")
        else:
            print(f"Archivo de tema '{filename}' no encontrado.")

        final_theme_source_for_processing = {}
        if success:
            final_theme_source_for_processing = self.default_theme_settings.copy()
            final_theme_source_for_processing.update(raw_loaded_theme_data) 
        elif apply_defaults_on_fail:
            print("Aplicando tema predeterminado.")
            final_theme_source_for_processing = self.default_theme_settings.copy()

        if return_raw: 
            return final_theme_source_for_processing if (success or apply_defaults_on_fail) else None

        if final_theme_source_for_processing:
            self.theme_config = self._prepare_theme_dict(final_theme_source_for_processing)
        elif not self.theme_config: 
            print("Fallback final: theme_config está vacío, usando configuración predeterminada procesada.")
            self.theme_config = self._prepare_theme_dict(self.default_theme_settings.copy()) 
        
        return success 


    def save_app_theme(self, filename, settings_dict_raw): 
        store = JsonStore(filename)
        try:
            store.put('theme_settings', config=dict(settings_dict_raw))
            print(f"Tema guardado en '{filename}'.")
        except Exception as e:
            print(f"Error al guardar tema en '{filename}': {e}")
            self.show_popup("Error", f"No se pudo guardar el tema: {e}")

    def show_popup(self, title, message): 
        popup_bg_rgba = self.theme_config.get("Popup_bg_rgba", self.default_theme_settings["Popup_bg_rgba"])
        button_bg_rgba_config = self.theme_config.get("MySmallActionButton_rgba", self.default_theme_settings["MySmallActionButton_rgba"])

        message_label = Label(text=message, halign='center', valign='middle', font_size='19sp', size_hint_y=None, color=(0.9,0.9,0.9,1))
        message_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1] + dp(10))) 

        close_button = Button(
            text='Cerrar', size_hint_y=None, height=dp(50), font_size='18sp',
            background_color=button_bg_rgba_config, 
            background_normal='', background_down='', color=(1,1,1,1)
        )
        with close_button.canvas.before:
            Color(rgba=button_bg_rgba_config) 
            close_button.bg_rect = RoundedRectangle(radius=[dp(10)])
        def update_button_bg(instance, _): 
            if hasattr(instance, 'bg_rect'):
                instance.bg_rect.pos = instance.pos
                instance.bg_rect.size = instance.size
        close_button.bind(pos=update_button_bg, size=update_button_bg)


        popup_layout_internal = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        popup_layout_internal.add_widget(message_label)
        popup_layout_internal.add_widget(close_button)

        popup_content_wrapper = BoxLayout(orientation='vertical')
        with popup_content_wrapper.canvas.before:
            Color(rgba=popup_bg_rgba) 
            popup_content_wrapper.bg_rect_instruction = RoundedRectangle(radius=[dp(12)]) 

        def _update_popup_wrapper_bg(instance, _): 
            if hasattr(instance, 'bg_rect_instruction') and instance.bg_rect_instruction:
                instance.bg_rect_instruction.pos = instance.pos
                instance.bg_rect_instruction.size = instance.size
        popup_content_wrapper.bind(pos=_update_popup_wrapper_bg, size=_update_popup_wrapper_bg)
        popup_content_wrapper.add_widget(popup_layout_internal)


        popup_content_width = Window.width * 0.8 
        label_text_width = popup_content_width - dp(20) * 2 
        message_label.text_size = (label_text_width, None) 
        message_label.texture_update() 

        title_and_separator_height = dp(50) if title else dp(10) 
        internal_content_height = message_label.height + close_button.height + popup_layout_internal.spacing + popup_layout_internal.padding[1] + popup_layout_internal.padding[3]
        final_popup_height = internal_content_height + title_and_separator_height
        min_popup_height = dp(220) 
        final_popup_height = max(final_popup_height, min_popup_height)


        popup = Popup(title=title, title_size='21sp', title_align='center',
                      content=popup_content_wrapper, 
                      size_hint=(0.8, None), height=final_popup_height,
                      auto_dismiss=False,
                      separator_color=self.theme_config.get("Popup_separator_color", self.default_theme_settings["Popup_separator_color"]),
                      background_color = (0,0,0,0), background = '') 

        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def show_gif_popup(self, gif_source, duration=2.5):
        """
        Muestra un popup sin bordes con un GIF animado que se cierra después de 'duration' segundos.
        Asegúrate de que el archivo GIF (ej. 'listo.gif') exista en el directorio del proyecto.
        """
        if not os.path.exists(gif_source):
            print(f"ERROR: No se encontró el archivo GIF '{gif_source}'. Mostrando popup de texto en su lugar.")
            self.show_popup("Éxito", "¡Venta completada!")
            return

        gif_image = Image(
            source=gif_source,
            anim_loop=0,
            allow_stretch=True,
            fit_mode='contain'
        )

        popup = Popup(
            content=gif_image,
            size_hint=(None, None),
            size=(dp(280), dp(280)),
            auto_dismiss=False,
            background='',
            background_color=(0,0,0,0),
            separator_height=0,
            title=''
        )
        popup.open()

        Clock.schedule_once(lambda dt: popup.dismiss(), duration)


    def on_stop(self): 
        print("Aplicación cerrada.")

if __name__ == "__main__":
    #Window.size = (480, 853) # Tamaño móvil típico para pruebas
    MyApp().run()
