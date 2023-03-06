txt_instruction = '''
Данное приложение позволит вам с помощью теста Руфье \n провести первичную диагностику вашего здоровья.\n
Проба Руфье представляет собой нагрузочный комплекс, \n предназначенный для оценки работоспособности сердца при физической нагрузке.\n
У испытуемого определяют частоту пульса за 15 секунд.\n
Затем в течение 45 секунд испытуемый выполняет 30 приседаний.\n
После окончания нагрузки пульс подсчитывается вновь: \nчисло пульсаций за первые 15 секунд, 30 секунд отдыха,\n число пульсаций за последние 15 секунд.\n'''

txt_test1 = '''Замерьте пульс за 15 секунд.\n
Результат запишите в соответствующее поле.'''

txt_test2 = '''Выполните 30 приседаний за 45 секунд.\n 
Нажмите кнопку "Начать", чтобы запустить счетчик приседаний.\n
Делайте приседания со скоростью счетчика.'''

txt_test3 = '''В течение минуты замерьте пульс два раза:\n 
за первые 15 секунд минуты, затем за последние 15 секунд.\n
Результаты запишите в соответствующие поля.''' 

txt_sits = 'Выполните 30 приседаний за 45 секунд.'
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import NumericProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import Clock

name = ''
age = 0
pulse1 = 0
pulse2 = 0
pulse3 = 0
Window.clearcolor = (0.25, 0.53,0.99 , 1)
button_color = (0, 1, 0, 1)
label_color = (0,0,0,1)
''' Модуль для расчета результатов пробы Руфье.

Сумма измерений пульса в трех попытках (до нагрузки, сразу после и после короткого отдыха)
в идеале должна быть не более 200 ударов в минуту. 
Мы предлагаем детям измерять свой пульс на протяжении 15 секунд, 
и приводим результат к ударам в минуту умножением на 4:
    S = 4 * (P1 + P2 + P3)
Чем дальше этот результат от идеальных 200 ударов, тем хуже.
Традиционно таблицы даются для величины, делённой на 10. 

Индекс Руфье   
    IR = (S - 200) / 10
оценивается по таблице в соответствии с возрастом:
        7-8             9-10                11-12               13-14               15+ (только для подростков!)
отл.     < 6.5           < 5                 < 3.5               < 2                 < 0.5  
хор.    >= 6.5 и < 12   >= 5 и < 10.5       >= 3.5 и < 9        >= 2 и < 7.5        >= 0.5 и < 6
удовл.  >= 12 и < 17    >= 10.5 и < 15.5    >= 9 и < 14         >= 7.5 и < 12.5     >= 6 и < 11
слабый  >= 17 и < 21    >= 15.5 и < 19.5    >= 14 и < 18        >= 12.5 и < 16.5    >= 11 и < 15
неуд.   >= 21           >= 19.5             >= 18               >= 16.5             >= 15

для всех возрастов результат "неуд" отстоит от "слабого" на 4, 
тот от "удовлетворительного" на 5, а "хороший" от "уд" - на 5.5

поэтому напишем функцию ruffier_result(r_index, level), которая будет получать
рассчитанный индекс Руфье и уровень "неуд" для возраста тестируемого, и отдавать результат

'''
# здесь задаются строки, с помощью которых изложен результат:
txt_index = "Ваш индекс Руфье: "
txt_workheart = "Работоспособность сердца: "
txt_nodata = '''
нет данных для такого возраста'''
txt_res = [] 
txt_res.append('''низкая. 
Срочно обратитесь к врачу!''')
txt_res.append('''удовлетворительная. 
Обратитесь к врачу!''')
txt_res.append('''средняя''')
txt_res.append('''
выше среднего''')
txt_res.append('''
высокая''')

def ruffier_index(P1, P2, P3):
    ''' возвращает значение индекса по трем показателям пульса для сверки с таблицей'''
    r_index = (4*(P1 + P2 + P3)-200)/10
    return r_index

def neud_level(age):
    ''' варианты с возрастом меньше 7 и взрослым надо обрабатывать отдельно, 
    здесь подбираем уровень "неуд" только внутри таблицы:
    в возрасте 7 лет "неуд" - это индекс 21, дальше каждые 2 года он понижается на 1.5 до значения 15 в 15-16 лет '''
    n = (min(15,int(age)- 7))//2
    x = 21 - 1.5*n
    return x 
    
def ruffier_result(r_index, level):
    ''' функция получает индекс Руфье и интерпретирует его, 
    возвращает уровень готовности: число от 0 до 4
    (чем выше уровень готовности, тем лучше).  '''
    if r_index >= level:
        return 0
    if r_index >= level-4:
        return 1
    if r_index >= level-9:
        return 2
    if r_index >= level-14.5:
        return 3
    return 4

def test(P1,P2,P3,age):
    ''' эту функцию можно использовать снаружи модуля для подсчетов индекса Руфье.
    Возвращает готовые тексты, которые остается нарисовать в нужном месте
    Использует для текстов константы, заданные в начале этого модуля. '''
    if int(age) < 7:
        return f'{txt_index}0, {txt_nodata}'
    else: 
        ruf_index = ruffier_index(P1,P2,P3)
        result = txt_res[ruffier_result(ruf_index, neud_level(age))]
        res = f'{txt_index}{str(ruf_index)}\n{txt_workheart}{result}'
        return res

def check(str_num):
    try:
        return int(str_num)
    except:
        return False

class Instruction_scr(Screen): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.start = Button(text = 'Начать',size_hint = (0.4,0.3),pos_hint = {'center_x':0.5})
        self.start.background_color = button_color
        self.start.on_press = self.save_name
        name = Label(text = 'Введите имя')
        self.age = Label(text = 'Введите возраст')
        insruction = Label(text = txt_instruction)
        self.age2 = TextInput(multiline = False)
        self.name2 = TextInput(multiline = False)
        layout1 = GridLayout(size_hint=(0.5, 0.2), height='30sp',cols = 1,rows = 4,pos_hint = {'center_x':0.5})
        layout2 = GridLayout(size_hint=(0.5, 0.2), height='30sp',cols = 1,rows = 4,pos_hint = {'center_x':0.5})
        layout3 = BoxLayout(padding=8, spacing=8,orientation = 'vertical',)
        layout4 = BoxLayout(size_hint=(0.4, 0.3), height='50sp',pos_hint = {'center_x' : 0.5,},orientation = 'vertical')
        #layout4.add_widget(self.start)
        layout1.add_widget(self.age)
        layout1.add_widget(self.age2)
        layout2.add_widget(name)
        layout2.add_widget(self.name2)
        layout3.add_widget(insruction) 
        layout3.add_widget(layout1)
        layout3.add_widget(layout2)
        layout3.add_widget(self.start)
        #layout3.add_widget(layout4)
        self.add_widget(layout3)
    def save_name(self): 
        global name,age
        name = self.name2.text
        age = check(self.age2.text)
        if age == False or age < 7 or age > 15:
            age = 0
            self.age2.text = str(age)
            self.age.text = 'Введите нормальное значение'
        else:
            self.manager.current = 'second'

class Seconds(Label):
    done = BooleanProperty(False)
    def __init__(self, total, **kwargs):
        self.total = total
        self.current = 0
        self.done = False
        my_text = 'Прошло секунд ' + str(self.current)
        super().__init__(text = my_text)
    def restart(self, total, **kwargs):
        self.total = total
        self.current = 0
        self.done = False
        self.text  = 'Прошло секунд' + str(self.current)
        self.start()
    def start(self):
        Clock.schedule_interval(self.change,1)
    def change(self, dt):
        self.current += 1
        self.text  = 'Прошло секунд ' + str(self.current)
        if self.current >= self.total:
            self.done = True
            return False
class Pulse_scr(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.label_sec = Seconds(15)
        self.label_sec.bind(done = self.sec_finished)
        test = Label(text = txt_test1)
        self.result2 = Label(text = 'Введите результат')
        self.result = TextInput(multiline = False)
        self.result.set_disabled(True)
        self.next_ = Button(text = 'Начать')
        self.next_.background_color = button_color
        self.next_.on_press = self.save_pulse
        layout1 = BoxLayout(padding=8, spacing=8,orientation = 'vertical')
        layout2 = BoxLayout(size_hint=(0.8, 0.4), height='50sp',pos_hint = {'center_x' : 0.5,},orientation = 'vertical')
        layout3 = BoxLayout(size_hint=(0.4, 0.3), height='50sp',pos_hint = {'center_x' : 0.5,},orientation = 'vertical')
        layout1.add_widget(test)
        layout1.add_widget(self.label_sec)
        layout2.add_widget(self.result2)
        layout2.add_widget(self.result)
        layout3.add_widget(self.next_)
        layout1.add_widget(layout2)
        layout1.add_widget(layout3)
        self.add_widget(layout1)
    def sec_finished(self,*args):
        self.result.set_disabled(False)
        self.next_screen = True
        self.next_.set_disabled(False)
        self.next_.text = 'Продолжить'
    def save_pulse(self):
        if not self.next_screen:
            self.next_.set_disabled(True)
            self.label_sec.start()
        else:
            global pulse1
            pulse1 = check(self.result.text)
            if pulse1 == False or pulse1 <= 0:
                pulse1 = 0
                self.result.text = str(pulse1)
                self.result2.text = 'Введите нормальное значение'
            else:
                self.manager.current = 'third'
class Sits(Label):
    
    def __init__(self, total, **kwargs):
        self.total = total
        self.current = 0
        txt = 'Осталось приседаний: ' + str(self.total)
        super().__init__(text = txt,**kwargs)
    def next(self, *args):
        self.current += 1
        remain = max(0, self.total - self.current)
        self.text = 'Осталось приседаний: ' + str(remain)       

class Runner(BoxLayout):

    value = NumericProperty(0)
    finished = BooleanProperty(False)
    def __init__(self,total = 10,steptime = 1, autorepeat = True, **kwargs):
        super().__init__(**kwargs)  
        self.total = total
        self.animation = (Animation(pos_hint = {'top': 0.1}, duration = steptime/2) + Animation(pos_hint = {'top': 1.0},duration = steptime/2)) 
        self.btn = Button(size_hint = (1,0.1),pos_hint = {'top' : 1.0},text = 'Приседайте')
        self.btn.background_color = button_color
        self.add_widget(self.btn)
        self.animation.on_progress = self.next
    def start(self):
        self.value = 0
        self.finished = False
        self.animation.repeat = True
        self.animation.start(self.btn)

    def next(self, widget, step):
        if step == 1.0:
            self.value += 1
            if self.value >= self.total:
                self.animation.repeat = False
                self.finished = True
class Sits_scr(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.next_screen = False
        self.lbl_sits = Sits(30)
        self.run = Runner(total = 30, steptime = 2,size_hint = (0.4,1))
        self.run.bind(value = self.sits_finished)
        text = Label(text = txt_sits)
        self.button = Button(text = 'Начать',size_hint=(0.4, 0.3), height='50sp',pos_hint = {'center_x' : 0.5,})
        self.button.background_color = button_color
        self.button.on_press = self.next
        layout = BoxLayout(padding=8, spacing=8,orientation = 'vertical')
        animation_layout = BoxLayout(orientation = 'vertical',size_hint = (0.3,1))
        layout.add_widget(text)
        layout.add_widget(animation_layout)
        layout.add_widget(self.button) 
        layout.add_widget(self.run)
        animation_layout.add_widget(self.lbl_sits)
        self.add_widget(layout)
    def sits_finished(self,instance,value):
        self.button.set_disabled(False)
        self.next_screen = True
        self.button.text = 'Продолжить'

    def next(self):
        if not self.next_screen:
            self.button.set_disabled(True)
            self.run.start()
            self.run.bind(value = self.lbl_sits.next)
        else:
            self.manager.current = 'fourth'
class Pulse2_scr(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.stage = 0
        self.label_sec = Seconds(15)
        self.label_sec.bind(done = self.second_finished)
        self.next_scr = False
        text_ = Label(text = txt_test3)
        self.txt = Label(text = 'Введите результат',halign = 'left', pos_hint = {'center_x' : 0.3})
        layout2 = BoxLayout(size_hint=(0.7, None), height='30sp',pos_hint = {'center_x':0.5})
        self.result = TextInput(multiline = False)
        self.result.set_disabled(True)
        self.txt2 = Label(text = 'Введите результат после отдыха',halign = 'left', pos_hint = {'center_x' : 0.3})
        layout3 = BoxLayout(size_hint=(0.7, None), height='30sp',pos_hint = {'center_x':0.5})
        self.result2 = TextInput(multiline = False)
        self.result2.set_disabled(True)
        self.button = Button(text = 'Начать')
        self.button.background_color = button_color
        self.button.on_press = self.save_pulse
        layout4 = BoxLayout(size_hint=(0.4, 0.3),pos_hint = {'center_x' : 0.5},orientation = 'vertical')
        layout = BoxLayout(padding=8, spacing=8,orientation = 'vertical')
        layout.add_widget(text_)
        layout.add_widget(self.label_sec)
        layout2.add_widget(self.result)
        layout2.add_widget(self.txt)
        layout3.add_widget(self.result2)
        layout3.add_widget(self.txt2)
        layout4.add_widget(self.button)
        layout.add_widget(layout2) 
        layout.add_widget(layout3)
        layout.add_widget(layout4)
        self.add_widget(layout)
    def second_finished(self,*args):
        self.button.set_disabled(True)
        if self.label_sec.done:
            if self.stage == 0:
                self.stage = 1
                self.label_sec.restart(30)
                self.result.set_disabled(False)
                self.button.set_disabled(True)
            elif self.stage == 1:
                self.stage = 2 
                self.label_sec.restart(15)
                self.button.set_disabled(True)
            elif self.stage == 2:
                self.next_scr = True
                self.result2.set_disabled(False)
                self.button.set_disabled(False)
                self.button.text = 'Завершить'
    def save_pulse(self):
        if not self.next_scr:
            self.button.set_disabled(True)
            self.label_sec.start()
        else:
            global pulse2,pulse3
            pulse2 = check(self.result.text)
            pulse3 = check(self.result2.text)
            if pulse2 == False or pulse2 <=0:
                pulse2 = 0
                self.result.text = str(pulse2)
                self.txt.text = 'Введите нормальное значение'
            else:
                self.manager.current = 'fiveth'
            if pulse3 == False or pulse3 <=0:
                pulse3 = 0
                self.result2.text = str(pulse3)
                self.txt2.text = 'Введите нормальное значение'
            else:
                self.manager.current = 'fiveth'
class Result_scr(Screen):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.instruction = Label(text = '')
        self.layout = BoxLayout(padding=8, spacing=8,orientation = 'vertical', pos_hint = {'center_y':0.5,'center_x': 0.5},size_hint = (0.2,0.2))
        self.layout.add_widget(self.instruction)
        self.add_widget(self.layout)
        self.on_enter = self.print_result
    def print_result(self):
        global name
        self.instruction.text = f'{name}\n{test(pulse1,pulse2,pulse3,age)}'
class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Instruction_scr(name = 'first'))
        sm.add_widget(Pulse_scr(name = 'second'))
        sm.add_widget(Sits_scr(name = 'third'))
        sm.add_widget(Pulse2_scr(name = 'fourth'))
        sm.add_widget(Result_scr(name = 'fiveth'))
        return sm

app = MyApp()
if __name__ == '__main__':
    app.run()
''' Модуль для расчета результатов пробы Руфье.

Сумма измерений пульса в трех попытках (до нагрузки, сразу после и после короткого отдыха)
в идеале должна быть не более 200 ударов в минуту. 
Мы предлагаем детям измерять свой пульс на протяжении 15 секунд, 
и приводим результат к ударам в минуту умножением на 4:
    S = 4 * (P1 + P2 + P3)
Чем дальше этот результат от идеальных 200 ударов, тем хуже.
Традиционно таблицы даются для величины, делённой на 10. 

Индекс Руфье   
    IR = (S - 200) / 10
оценивается по таблице в соответствии с возрастом:
        7-8             9-10                11-12               13-14               15+ (только для подростков!)
отл.     < 6.5           < 5                 < 3.5               < 2                 < 0.5  
хор.    >= 6.5 и < 12   >= 5 и < 10.5       >= 3.5 и < 9        >= 2 и < 7.5        >= 0.5 и < 6
удовл.  >= 12 и < 17    >= 10.5 и < 15.5    >= 9 и < 14         >= 7.5 и < 12.5     >= 6 и < 11
слабый  >= 17 и < 21    >= 15.5 и < 19.5    >= 14 и < 18        >= 12.5 и < 16.5    >= 11 и < 15
неуд.   >= 21           >= 19.5             >= 18               >= 16.5             >= 15

для всех возрастов результат "неуд" отстоит от "слабого" на 4, 
тот от "удовлетворительного" на 5, а "хороший" от "уд" - на 5.5

поэтому напишем функцию ruffier_result(r_index, level), которая будет получать
рассчитанный индекс Руфье и уровень "неуд" для возраста тестируемого, и отдавать результат

'''
# здесь задаются строки, с помощью которых изложен результат:
txt_index = "Ваш индекс Руфье: "
txt_workheart = "Работоспособность сердца: "
txt_nodata = '''
нет данных для такого возраста'''
txt_res = [] 
txt_res.append('''низкая. 
Срочно обратитесь к врачу!''')
txt_res.append('''удовлетворительная. 
Обратитесь к врачу!''')
txt_res.append('''средняя''')
txt_res.append('''
выше среднего''')
txt_res.append('''
высокая''')

def ruffier_index(P1, P2, P3):
    ''' возвращает значение индекса по трем показателям пульса для сверки с таблицей'''
    r_index = (4*(P1 + P2 + P3)-200)/10
    return r_index

def neud_level(age):
    ''' варианты с возрастом меньше 7 и взрослым надо обрабатывать отдельно, 
    здесь подбираем уровень "неуд" только внутри таблицы:
    в возрасте 7 лет "неуд" - это индекс 21, дальше каждые 2 года он понижается на 1.5 до значения 15 в 15-16 лет '''
    n = (min(15,int(age)- 7))//2
    x = 21 - 1.5*n
    return x 
    
def ruffier_result(r_index, level):
    ''' функция получает индекс Руфье и интерпретирует его, 
    возвращает уровень готовности: число от 0 до 4
    (чем выше уровень готовности, тем лучше).  '''
    if r_index >= level:
        return 0
    if r_index >= level-4:
        return 1
    if r_index >= level-9:
        return 2
    if r_index >= level-14.5:
        return 3
    return 4

def test(P1,P2,P3,age):
    ''' эту функцию можно использовать снаружи модуля для подсчетов индекса Руфье.
    Возвращает готовые тексты, которые остается нарисовать в нужном месте
    Использует для текстов константы, заданные в начале этого модуля. '''
    if int(age) < 7:
        return f'{txt_index}0, {txt_nodata}'
    else: 
        ruf_index = ruffier_index(P1,P2,P3)
        result = txt_res[ruffier_result(ruf_index, neud_level(age))]
        res = f'{txt_index}{str(ruf_index)}\n{txt_workheart}{result}'
        return res

def check(str_num):
    try:
        return int(str_num)
    except:
        return False
button_color = (0.9,0.9,0.9,1)
class Runner(BoxLayout):

    value = NumericProperty(0)
    finished = BooleanProperty(False)
    def __init__(self,total = 10,steptime = 1, autorepeat = True, **kwargs):
        super().__init__(**kwargs)  
        self.total = total
        self.animation = (Animation(pos_hint = {'top': 0.1}, duration = steptime/2) + Animation(pos_hint = {'top': 1.0},duration = steptime/2)) 
        self.btn = Button(size_hint = (1,0.1),pos_hint = {'top' : 1.0},text = 'Приседайте')
        self.btn.background_color = label_color
        self.add_widget(self.btn)
        self.animation.on_progress = self.next
    def start(self):
        self.value = 0
        self.finished = False
        self.animation.repeat = True
        self.animation.start(self.btn)

    def next(self, widget, step):
        if step == 1.0:
            self.value += 1
            if self.value >= self.total:
                self.animation.repeat = False
                self.finished = True