from fileinput import filename
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.uix.widget import Widget
import os
import random
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label 
from questions_self import QUESTIONS_SELF
from questions_relationship import QUESTIONS_RELATIONSHIP
from questions_friendship import QUESTIONS_FRIENDSHIP
from kivy.uix.screenmanager import Screen
import math
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput



LOVE_LANGUAGES = [
    "Words of Affirmation",
    "Acts of Service",
    "Receiving Gifts",
    "Quality Time",
    "Physical Touch"
]


class BaseScreen(Screen): 
    background = StringProperty("base.png")

class SplashScreen(BaseScreen):
    def on_enter(self):
        Clock.schedule_once(self.goto_welcome, 20.0)

    def goto_welcome(self, dt):
        self.manager.current = "welcome"

class WelcomeScreen(BaseScreen):
   def go_to_purpose(self):
     self.manager.current = "nameinput"

class NameInputScreen(BaseScreen):
    def save_name(self, name):
        if name.strip() == "":
            return
        app = App.get_running_app()
        app.user_name = name.strip()
        self.manager.current = "purpose"

class PurposeScreen(BaseScreen):
    def choose_purpose(self, purpose):
        app = App.get_running_app()
        qscreen = app.root.get_screen("question")

        if purpose == "self":
            qscreen.set_question_list(QUESTIONS_SELF, "self")
        elif purpose == "relationship":
            qscreen.set_question_list(QUESTIONS_RELATIONSHIP, "relationship")
        elif purpose == "friendship":
            qscreen.set_question_list(QUESTIONS_FRIENDSHIP, "friendship")

        app.root.current = "question"

class QuestionScreen(BaseScreen):
    q_index = NumericProperty(0)
    question_text = StringProperty("")
    scores = ListProperty([0, 0, 0, 0, 0]) 
    total_questions = NumericProperty(0)


    current_questions = ListProperty([])
    purpose = StringProperty("")
    show_back = BooleanProperty(False)

    def set_question_list(self, questions, purpose):
        import random
        if len(questions) > 20:
            self.current_questions = random.sample(questions, 20)
        else:
            self.current_questions = questions[:]  
        self.total_questions = len(self.current_questions)
        self.purpose = purpose

        self.q_index = 0
        self.scores = [0, 0, 0, 0, 0]
        self.answers = {}
        self.show_back = (self.q_index > 0)

    def on_enter(self):
        self.q_index = 0
        self.total_questions = len(self.current_questions)
        self.answers = {}
        
        self.load_question()

    def load_question(self):
        import random 

        self.show_back = (self.q_index > 0)

        if self.q_index < self.total_questions:
            q, options = self.current_questions[self.q_index]
            self.question_text = f"{self.q_index + 1}. {q}"
            option_pairs = [(text, idx) for idx, text in enumerate(options)]
            random.shuffle(option_pairs)
            for i, (text, lang_index) in enumerate(option_pairs):
                btn = self.ids.get(f"opt{i}")
                if btn:
                    btn.text = text
                    btn.lang_index = lang_index
        else:
            self.manager.current = "result"
        
        self.reset_buttons()

        if self.q_index in self.answers:
            selected_lang = self.answers[self.q_index]
            for i in range(5):
                btn = self.ids.get(f"opt{i}")
                if btn and btn.lang_index == selected_lang:
                    btn.background_color = (0.85, 0.25, 0.45, 1) 

        
    def choose(self, lang_index):
        if self.q_index not in self.answers:  
            self.answers[self.q_index] = lang_index
            if 0 <= lang_index < len(self.scores):
                self.scores[lang_index] += 1

        self.reset_buttons()
        for i in range(5):
            btn = self.ids.get(f"opt{i}")
            if btn and btn.lang_index == lang_index:
                btn.background_color = (0.85, 0.25, 0.45, 1)

        self.q_index += 1
        self.load_question()

    def prev_question(self):
        if self.q_index > 0:
            self.q_index -= 1
        if self.q_index in self.answers:
            prev_lang = self.answers[self.q_index]
            self.scores[prev_lang] = max(0, self.scores[prev_lang] - 1)
            del self.answers[self.q_index]

        self.load_question()

        
    def next_question(self):
        if self.q_index not in self.answers:
            print("User belum memilih jawaban!")
            return

        if self.q_index < self.total_questions - 1:
            self.q_index += 1
            self.load_question()
        else:
            self.manager.current = "result"

    def reset_quiz(self):
        if self.purpose == "self":
            self.set_question_list(QUESTIONS_SELF, "self")
        elif self.purpose == "relationship":
            self.set_question_list(QUESTIONS_RELATIONSHIP, "relationship")
        elif self.purpose == "friendship":
            self.set_question_list(QUESTIONS_FRIENDSHIP, "friendship")

        self.answers = {}
        self.q_index = 0
        self.load_question()

    def reset_buttons(self):
        default_colors = [
            (242/255, 183/255, 195/255, 1),
            (232/255, 163/255, 173/255, 1),
            (218/255, 121/255, 138/255, 1),
            (203/255, 106/255, 123/255, 1),
            (197/255, 95/255, 112/255, 1),
        ]
        for i in range(5):
            btn = self.ids.get(f"opt{i}")
            if btn:
                btn.background_color = default_colors[i]

class BarChart(Widget):
    labels = ListProperty(LOVE_LANGUAGES)
    values = ListProperty([0,0,0,0,0])

    def on_size(self, *args):
        self.draw_chart()

    def on_values(self, *args):
        self.draw_chart()

    def draw_chart(self):
        self.canvas.clear()
        with self.canvas:
            Color(rgba=(1, 1, 1, 0)) 
            w = self.width
            h = self.height
            bar_height = h / (len(self.values) * 1.4)
            gap = bar_height * 0.4
            max_bar_width = w * 0.7
            x_label_x = w * 0.02
            x_bar_x = w * 0.30
            y = h - bar_height - gap/2
            for i, v in enumerate(self.values):
                percent = v if v is not None else 0
                bar_w = max_bar_width * (percent / 100.0) if max_bar_width > 0 else 0
                Color(1.0, 0.6 - i*0.04, 0.8 - i*0.05, 1)
                Rectangle(pos=(x_bar_x, y), size=(bar_w, bar_height))
                Color(0.95, 0.85, 0.9, 1)
                Rectangle(pos=(x_bar_x + bar_w, y), size=(max_bar_width - bar_w, bar_height))
                y -= (bar_height + gap)


class ResultScreen(BaseScreen):
    user_title = StringProperty("")
    dominant_text = StringProperty("")
    detail_text = StringProperty("")
    percentages = ListProperty([0,0,0,0,0])

    def on_enter(self):
        app = App.get_running_app()
        name = app.user_name if app.user_name else "You"

        qscreen = self.manager.get_screen("question")
        scores = qscreen.scores[:]
        total = sum(scores) if sum(scores) > 0 else 1
        perc = [round((s / total) * 100, 1) for s in scores]
        self.percentages = perc
        max_index = scores.index(max(scores)) if scores else 0
        self.user_title =  f"{name}, your primary love language is"
        self.dominant_text = LOVE_LANGUAGES[max_index]
        details = {
            "Words of Affirmation": "Kamu merasa paling dihargai ketika mendengar kata-kata yang tulus, pujian yang lembut, dan ungkapan kasih sayang secara verbal. Ucapan yang meneguhkan membuatmu merasa diperhatikan, dipahami, dan dicintai dengan sepenuh hati.",
            "Acts of Service": "Kamu merasa dicintai ketika seseorang membantu meringankan bebanmu, bahkan tanpa diminta. Perhatian yang diwujudkan lewat perbuatan kecil maupun besar menunjukkan bahwa kamu berarti bagi mereka. Bagimu, tindakan nyata adalah bahasa cinta yang paling kuat.",
            "Receiving Gifts": "Hadiah yang diberikan dengan penuh perhatian—meski sederhana—membuatmu merasa diingat dan dihargai. Kamu melihat cinta melalui ketulusan di balik pemberian itu, bukan dari nilai atau ukurannya. Setiap hadiah terasa seperti simbol kepedulian yang hangat.",
            "Quality Time": "Kamu merasa paling dekat dengan seseorang ketika mereka memberikan waktunya secara utuh untukmu. Percakapan mendalam, momen berdua yang tenang, dan kebersamaan tanpa gangguan membuatmu merasa benar-benar terhubung. Waktu berkualitas adalah bentuk perhatian yang paling berarti bagimu.",
            "Physical Touch": "Sentuhan hangat, genggaman tangan, atau pelukan lembut membuatmu merasa aman dan disayangi. Bagi kamu, kedekatan fisik adalah cara paling natural untuk merasakan kenyamanan dan cinta yang tulus dari orang lain."
        }
        self.detail_text = details.get(self.dominant_text, "")
        bar = self.ids.get("bar_chart")
        if bar:
            bar.values = self.percentages


class ThankYouScreen(BaseScreen):

    def download_result(self):
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        self.file_name_input = TextInput(
            text="love_language_result",
            hint_text="Masukkan nama file",
            size_hint_y=None,
            height=40
        )

        self.filechooser = FileChooserListView(
            path=os.path.expanduser("~"),
            filters=["!*.py", "!*.kv"],
            size_hint_y= 2.9
        )

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)

        save_btn = Button(text="Save")
        cancel_btn = Button(text="Cancel")

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)

        content.add_widget(Label(text="Nama File:"))
        content.add_widget(self.file_name_input)
        content.add_widget(Label(text="Pilih Folder:"))
        content.add_widget(self.filechooser)
        content.add_widget(btn_layout)

        self.popup = Popup(
            title="Download Result",
            content=content,
            size_hint=(0.9, 0.9)
        )

        save_btn.bind(on_release=self.save_image)
        cancel_btn.bind(on_release=self.popup.dismiss)

        self.popup.open()
    def save_image(self, instance):
        app = App.get_running_app()
        sm = app.root
        result_screen = sm.get_screen("result")
        root_widget = result_screen.ids.get("capture_area")

        if not root_widget:
            print("capture_area tidak ditemukan")
            return

        folder = self.filechooser.path
        filename = self.file_name_input.text.strip()

        if not filename:
            filename = "love_language_result"
        
        full_path = os.path.join(folder, f"{filename}.png")

        root_widget.canvas.ask_update()
        Clock.schedule_once(
            lambda dt: root_widget.export_to_png(full_path),
            0.3
        )

        self.popup.dismiss()
        print(f"File disimpan di: {full_path}")


class CupidChoiceApp(App):
    user_name = StringProperty("")
    
    def build(self):
        root = Builder.load_file("cupidchoice.kv")
        root.transition = NoTransition()
        return root

if __name__ == "__main__":
    app = CupidChoiceApp()
    app.run()