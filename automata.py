import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import numpy as np
import BitsFunctions as bf
import logging
import os
import pickle
from datetime import datetime
import qm

### Значит, сохранение/загрузка работают. Нужно сделать формирование сводной таблицы. Хотя нет, это не обязательно. Можно обойтись прямой записью единиц и неопределенных состояний. 

# def create_equations(dic):
	# equations = []
	# for name, ones in dic.items():
		# equation = name
		# raw_foo = qm.qm(ones = ones)
		# print(raw_foo)

# def create_logic_function()

def numerate_variables(name, n, reverse = True, little = True):
	out = []
	if little == True:
		name = name.lower()
	for i in range(n):
		if reverse == True:
			tmp = f'{name}[{n-i-1}]'
		else:
			tmp = f'{name}[{i}]'
		out.append(tmp)
	return out
	
def create_function_from_raw(raw_foo, inputs):
	terms = []
	print('TAK')
	for part in raw_foo:
		term = []
		for i, sym in enumerate(part):
			if sym == '0':
				term.append(f'!{inputs[i]}')
			elif sym == '1':
				term.append(f'{inputs[i]}')
			else:
				continue
		terms.append(term)
	out = ''
	for i, term in enumerate(terms):
		str_term = ''
		for j, x in enumerate(term):
			str_term += x
			if j != len(term) - 1:
				str_term += ' & '
		out += str_term
		if i != len(terms) - 1:
			out += ' | '
	print(out)
	return(out)

class win(tk.Frame):
	def __init__(self, root):
		super().__init__(root)
		root.frames_names = {
			'input':(0, 0),
			'result':(0, 1),
			'jumpsoutstable':(1, 0),
			'codings':(1, 1)}
		root.frames = {}
		for name, gridpos in root.frames_names.items():
			if name == 'input':
				fr = InputFrame(root)
			elif name == 'jumpsoutstable':
				fr = JumpsOutsTable(root, 4, 3, 2)
			elif name == 'codings':
				fr = CodingsFrame(root)
			elif name == 'result':
				fr = ResultsFrame(root)
			else:
				continue
			fr.grid(row = gridpos[0], column = gridpos[1], sticky = 'nswe')
			root.frames[name] = fr
		
		self.add_menu(root)
		
	def add_menu(self, root):
		self.menu = tk.Menu(root)
		root.config(menu = self.menu)
		self.menu_file = tk.Menu(self.menu, tearoff = 0)
		self.menu_file.add_command(label = 'Новый', command = lambda : self.clear_data())
		self.menu_file.add_command(label = 'Открыть', command = lambda : self.open_data())
		self.menu_file.add_command(label = 'Сохранить', command = lambda : self.save_data(False))
		self.menu_file.add_command(label = 'Выход', command = root.destroy)
		self.menu.add_cascade(label = 'Файл', menu = self.menu_file)
		# self.menu.add_command(label = 'Справка', command = lambda : self.show_help())
		
	def clear_data(self):
		pass
		
	def open_data(self, load_last = False):
		filename = 'last.fsatb'
		if load_last == False:
			filename = fd.askopenfilename(filetypes = [('Данные для рассчёта','*.fsatb'), ('Все','*.*')])
		file = open(filename, 'rb')
		load_data = pickle.load(file)
		for name, frame in root.frames.items():
			try:
				frame_data = load_data[name]
				print(f'frame "{name}": {frame_data}')
				frame.load(frame_data)
			except KeyError:
				print(f'frame "{name}" has no load data')
		# pass
		
	def save_data(self, is_current = True):
		filename = 'last'
		save_data = {}
		for name, frame in root.frames.items():
			frame_data = frame.save()	
			print(f'Frame "{name}" gave:\n {frame_data}\n')
			if frame_data == None:
				logging.error(f'Сохранение не удалось, так как от фрейма "{name}" получено:\n {frame_data}\n')
				mb.showinfo(title = 'ОШИБКА!', message = f'Сохранение не удалось, так как от фрейма "{name}" получено:\n {frame_data}\n')
				return False
			save_data[name] = frame_data
		if is_current == False:
			filename = fd.asksaveasfilename(filetypes = [('Данные для рассчёта','*.fsatb'), ('Все','*.*')])
		else:
			filename += '.fsatb'
		savefile = open(filename, 'wb')
		pickle.dump(save_data, savefile)
		savefile.close
		if is_current == False:
			mb.showinfo(title = ':3', message = f'Сохранено!')
	
	def get_table_values(self):
		values = self.fr_jumpsoutstable.get()
		# print(values)
		logging.debug(f'таблица переходов/выходов {values}')

class InputFrame(tk.LabelFrame):
	'''Окно ввода'''
	def __init__(self, root):
		super().__init__(root, text = 'Количество состояний:')
		self.names = {'nX':'входов (X)', 'nY':'автомата (Y)', 'nZ':'выходов (Z)'}
		self.lbs = {}
		self.ens = {}
		self.inputs = {} # Значения полей ввода
		i = 0
		for name, txt in self.names.items():
			self.lbs[name] = tk.Label(self, text = txt)
			self.lbs[name].grid(row = 0, column = i, sticky = 'nswe')
			self.ens[name] = tk.Entry(self, width = 5, bg = 'white', justify = 'right')
			self.ens[name].grid(row = 1, column = i, sticky = 'nswe')
			i += 1
		self.bt_createtable = tk.Button(self, text = 'Создать таблицу переходов/выходов', command = self.create_and_update_tabels)
		self.bt_createtable.grid(row = 2, column = 0, columnspan = len(self.names))
		
		self.bt_test00 = tk.Button(self, text = 'SET', command = self.test00)
		self.bt_test00.grid(row = 3, column = 0, columnspan = len(self.names))
		
	def create_and_update_tabels(self):
		self.create_jumpsouts()
		self.create_codings()
	
	def create_jumpsouts(self):
		try: 
			root.frames['jumpsoutstable'].destroy()
		except AttributeError:
			pass
		vals = []
		try:
			for name, en in self.ens.items():
				value = int(en.get())
				vals.append(value)
			root.frames['jumpsoutstable'] = JumpsOutsTable(root, vals[0], vals[1], vals[2])
			root.frames['jumpsoutstable'].grid(row = 1, column = 0, sticky = 'nswe')
		except ValueError:
			pass
	
	def create_codings(self):
		try: 
			root.frames['codings'].destroy()
		except AttributeError:
			pass
		self.get()
		root.frames['codings'] = CodingsFrame(root, self.inputs)
		root.frames['codings'].grid(row = 1, column = 1, sticky = 'nswe')
	
	def get(self):
		try:
			for name, entry in self.ens.items():
				n = int(entry.get())
				a = name.replace('n', '')
				self.inputs[a] = n
			return self.inputs
		except ValueError:
			return None
			# pass

	def set(self, inputs):
		for name, entry in self.ens.items():
			a = name.replace('n', '')
			entry.delete(0, tk.END)
			entry.insert(0, inputs[a])
	
	def save(self):
		return self.get()
	
	def load(self, load_data):
		self.set(load_data)
	
	def test00(self):
		inputs = {'X':[5], 'Y':[3], 'Z':[2]}
		self.set(inputs)
	
class TriStateButton(tk.Button):
	def __init__(self, root, num = 0):
		self.states = ('0', '1', 'X')
		self.bgs = ('#0bf', '#bf0', '#b0f')
		self.cnt = 0
		self.cntlim = len(self.states)
		self.state = tk.StringVar()
		self.state.set(self.states[self.cnt])
		self.bg = self.bgs[self.cnt]
		super().__init__(root,
			command = self.change_state,
			textvariable = self.state,
			bg = self.bg)
		
	def change_state(self):
		if self.cnt < self.cntlim - 1:
			self.cnt += 1
		else:
			self.cnt = 0
		# print(self.cnt)
		self.state.set(self.states[self.cnt])
		self.bg = self.bgs[self.cnt]
		super().configure(bg = self.bg)
		
class CntButton(tk.Button):
	def __init__(self, root, lim, bg = '#ddd'):
		self.lim = lim - 1
		self.state = 0
		self.value = tk.StringVar()
		self.value.set(str(self.state))
		super().__init__(root,
			command = self.change_state,
			textvariable = self.value,
			bg = bg)
	
	def change_state(self):
		if self.state < self.lim:
			self.state += 1
		else:
			self.state = 0
		self.value.set(str(self.state))
	
	def set(self, value):
		if value <= self.lim:
			self.state = value
			self.value.set(str(self.state))
		
class ActiveButton(tk.Button):
	'''Кнопка с состояниями "активно/неактивно". Если одна такая кнопка переходит в состояние "активно", то все другие такие же кнопки перейдут в неактивное состояние'''
	def __init__(self, root, name = 'ActiveButton', active_bg = '#f55'):
		self.name = name
		self.root = root
		self.bg = '#ddd'
		self.active_bg = active_bg
		self.active = False
		super().__init__(root, command = self.change_state, text = name, bg = self.bg, activebackground = self.bg)
	
	def change_state(self):
		if self.active == True:
			self.deactivate()
		else:
			self.activate()
	
	def activate(self):
		self.active = True
		super().configure(bg = self.active_bg, activebackground = self.active_bg)
		self.deactivate_other()
	
	def deactivate(self):
		self.active = False
		super().configure(bg = self.bg, activebackground = self.bg)
		
	def deactivate_other(self):
		rootwidgets = self.root.winfo_children()
		# print(self.grid_info())
		for widget in rootwidgets:
			if isinstance(widget, ActiveButton):
				if widget == self:
					continue
				widget.deactivate()
				

class JumpsOutsTable(tk.LabelFrame):
	def __init__(self, root, nX, nY, nZ):
		super().__init__(root, text = 'Таблица переходов/выходов')
		# количества
		self.nX = nX	# Входов
		self.nY = nY	# Состояний автомата
		self.nZ = nZ	# Выходов
		# Количество входов определяет количество строк таблицы
		# Количество состояний автомата определяет количество столбцов таблицы
		self.labels = []
		self.frames_jumpout = []
		self.create_table()
		
		self.bt_test00 = tk.Button(self, text = 'GET', command = self.test)
		self.bt_test00.grid(row = self.nX + 2, column = 0)
		self.bt_test01 = tk.Button(self, text = 'SET', command = self.test00)
		self.bt_test01.grid(row = self.nX + 2, column = 1)
		# self.get()
		
	def test(self):
		aaa = self.get()
		print(aaa)
		
	def test00(self):
		jumps = np.zeros((4, 2), dtype = int)
		outs = np.zeros((4, 2), dtype = int)
		jumps[3, 0] = 1
		jumps[0, 1] = 1
		jumps[1, 1] = 1
		outs[2, 0] = 1
		outs[3, 0] = 1
		outs[1, 1] = 1
		# print(jumps)
		# print(outs)
		self.set(jumps, outs)
		
	def create_table(self):		
		self.clear_all()
		for i in range(self.nX + 1):
			for j in range(self.nY + 1):
				if i == 0:
					if j == 0:
						continue
					self.frames_jumpout.append([])
					# Шапка
					text = f'Y[{j-1}]'
					lb = tk.Label(self, text = text, borderwidth = 1, relief = "ridge")
					lb.grid(row = i, column = j, sticky = 'nsew')
					self.labels.append(lb)
				else:
					if j == 0:
						text = f'X[{i-1}]'
						lb = tk.Label(self, text = text, borderwidth = 1, relief = "ridge")
						lb.grid(row = i, column = j, sticky = 'nsew')
						self.labels.append(lb)
					else:
						fr_jumpout = JumpOutFrame(self, self.nY, self.nZ)
						fr_jumpout.grid(row = i, column = j)
						self.frames_jumpout[j-1].append(fr_jumpout)
	
	def clear(self, objects):
		# print(objects)
		try:
			for obj in objects:
				obj.destroy()
		except TypeError:
			pass
		except AttributeError:
			pass
		
	def clear_all(self):
		# print('CLEAR')
		# print(len(self.labels))
		# print(len(self.frames_jumpout))
		# self.clear(self.labels)
		# self.clear(self.frames_jumpout)
		widgets = self.winfo_children()
		for widget in widgets:
			widget.destroy()
		# widgets = self.winfo_children()
		# for widget in widgets:
			# print(widget)
		# print(widgets)
		# for widget in widgets():
		
	def get(self):
		jumps = np.zeros((self.nX, self.nY), dtype = int)
		outs = np.zeros((self.nX, self.nY), dtype = int)
		logging.debug(f'Таблица переходов:\n{jumps}')
		for i, col in enumerate(self.frames_jumpout):
			for j, jumpuot in enumerate(col):
				YZ = jumpuot.get()
				jumps[j, i] = YZ[0]
				outs[j, i] = YZ[1]
		return(jumps, outs)
	
	def set(self, jumpsouts):
		jumps = jumpsouts[0]
		outs = jumpsouts[1]
		self.nX = jumps.shape[0]
		self.nY = jumps.shape[1]
		self.nZ = np.amax(outs) + 1
		self.frames_jumpout = []
		self.create_table()
		# print(len(self.frames_jumpout))
		for i, col in enumerate(self.frames_jumpout):
			for j, jumpout in enumerate(col):
				Y = jumps[j, i]
				Z = outs[j, i]
				# print(f'[{j}, {i}] Y = {Y}, Z = {Z}')
				jumpout.set(Y, Z)
				
	def save(self):
		jumpsouts = self.get()
		nZ = self.nZ
		save_data = jumpsouts, nZ
		return save_data
	
	def load(self, load_data):
		jumpsouts = load_data[0]
		nZ = load_data[0]
		self.set(jumpsouts)
		self.nZ = nZ
						
class JumpOutFrame(tk.Frame):
	def __init__(self, root, nY, nZ):
		super().__init__(root)
		self.bt_jump = CntButton(self, nY, '#bf0')
		self.bt_jump.pack(side = tk.LEFT)
		self.bt_out = CntButton(self, nZ, '#b0f')
		self.bt_out.pack(side = tk.RIGHT)
	
	def get(self):
		jump = self.bt_jump.state
		out = self.bt_out.state
		return (jump, out)
		
	def set(self, jump, out):
		self.bt_jump.set(jump)
		self.bt_out.set(out)
	

class CodingFrame(tk.LabelFrame):
	def __init__(self, root, n, label = 'Входы', name = 'X'):
		super().__init__(root, text = label)
		self.n = n # количество состояний, которое требуется закодировать
		self.name = name.upper() # Обозначение, чьи это состояния
		self.get_table_parameters()
		self.create_table()
		self.buttons()
		# self.get()	# убрать отсюдова
		
	def buttons(self):
		self.bt_up = tk.Button(self, text = 'UP', command = lambda : self.move_abt('up'))
		self.bt_up.grid(row = 1, column = self.n_cols + 1, sticky = 'nsew')
		self.bt_dw = tk.Button(self, text = 'DW', command = lambda : self.move_abt('dw'))
		self.bt_dw.grid(row = 2, column = self.n_cols + 1, sticky = 'nsew')
		
		# эти кнопки в конце убрать
		self.bt_test00 = tk.Button(self, text = 'GET', command = self.get)
		self.bt_test00.grid(row = 3, column = self.n_cols + 1, sticky = 'nsew')
		
		self.bt_test01 = tk.Button(self, text = 'SET', command = self.test)
		self.bt_test01.grid(row = 4, column = self.n_cols + 1, sticky = 'nsew')
	
	def test(self):
		coding = {'X[0]': [0, 0], 'X[1]': [1, 0], 'X[2]': [1, 1]}
		self.set(coding)
		# self.clear_all()
		# print('ok')
	
	def create_table(self):
		# print(f'name: {self.name}, bits = {self.n_bits}, rows = {self.n_rows}, columns = {self.n_cols}')
		# print(f'rows = {self.n_rows}')
		# print(f'columns = {self.n_cols}')
		self.clear_all()
		self.bits = {} # Зачем здесь этот словарь?
		self.abts_val = []
		# Проход по строкам
		for i in range(self.n_rows):
			# получаем биты числа i-1, это нужно для ??
			bits_n = bf.split_int_to_bits(i-1, self.n_bits, True)
			if i > 0:
				self.bits[i] = bits_n # i:[x, x, x]
			# Проход по столбцам
			for j in range(self.n_cols):
				if j == 0:
					# В первой колонке создаём активные кнопки
					# ячейка сетки [0, 0], пропускаем её
					if (i == 0) | (i > self.n):
						continue
					# текст актив. кнопки, например Х[2]
					text = f'{self.name}[{str(i-1)}]'
					# создаём актив. кнопку и добавляем её в список кнопок
					abt = ActiveButton(self, text)
					abt.grid(row = i, column = 0, sticky = 'nsew')
					self.abts_val.append(abt)
					continue
				if i == 0:
					# Во всех остальных колонках прописываем значения 0/1,
					# но в первой строке заполняем шапку
					# Биты идут от старшего к младшему слева направо
					text = f'{self.name.lower()}[{str(self.n_cols - j - 1)}]'
					lb = tk.Label(self, text = text, borderwidth = 1, relief = "ridge")
					lb.grid(row = 0, column = j, sticky = 'nsew')
					continue
				lb = tk.Label(self, text = bits_n[j-1], borderwidth = 1, relief = "ridge")
				lb.grid(row = i, column = j, sticky = 'nsew')
		# print(self.bits)
	
	def move_abt(self, direction):
		abts = {} # ??
		active = None
		for widget in self.winfo_children():
			if isinstance(widget, ActiveButton):
				if widget.active == True:
					active = widget
				tmp = widget.grid_info()
				row = tmp['row']
				abts[widget] = row
		if active:
			active_row = abts[active]
			if direction == 'up':
				if active_row > 1:
					active_row -= 1
					for abt, row in abts.items():
						if row == active_row:
							abt.grid(row = active_row + 1)
					active.grid(row = active_row)
			if direction == 'dw':
				if active_row < self.n_rows - 1:
					active_row += 1
					for abt, row in abts.items():
						if row == active_row:
							abt.grid(row = active_row - 1)
					active.grid(row = active_row)
	
	def get(self):
		out = {}
		for abt in self.abts_val:
			tmp = abt.grid_info()
			row = tmp['row']
			cod = self.bits[row]
			out[abt.name] = cod
		# print(out)	
		return out
		
	def get_table_parameters(self):
		'''Метод находит количество строк и столбцов таблицы, а так же количество бит для кодировки'''
		self.n_bits = bf.get_bits_num(self.n - 1) # кол-во бит для кодировки
		self.n_cols = self.n_bits + 1	# колонки таблицы
		self.n_rows = pow(2, self.n_bits) + 1	# строки таблицы

	def set(self, coding):
		self.n = len(coding)
		self.get_table_parameters()
		self.create_table()
		self.buttons()
		# print(self.abts_val)
		for abt in self.abts_val:
			name = abt.name
			# print(name)
			cod = coding[name]
			row = bf.combine_bits_to_int(cod, True) + 1
			abt.grid(row = row)
			
	def clear_all(self):
		widgets = self.winfo_children()
		for widget in widgets:
			widget.destroy()
			
class CodingsFrame(tk.LabelFrame):
	'''Окно с таблицами кодировок состояний входов, автомата и выходов'''
	def __init__(self, root, inputs = {'X': 4, 'Y': 2, 'Z': 2}):
		super().__init__(root, text = 'Кодировки')
		self.inputs = inputs
		# Словарь с названиями таблиц кодировок
		self.names = {
			'X':'Входы автомата',
			'Y':'Состояния автомата',
			'Z':'Выходы автомата'}
		self.frs_coding = {} # словарь с таблицами кодировок
		# Создаём таблицу
		self.create_table()
		
		self.bt_test00 = tk.Button(self, text = 'GET', command = self.get)
		self.bt_test00.grid(row = 2, column = 0, sticky = 'nsew')
		self.bt_test01 = tk.Button(self, text = 'SET', command = self.test00)
		self.bt_test01.grid(row = 2, column = 1, sticky = 'nsew')
	
	def create_table(self):
		i = 0
		for name, label in self.names.items():
			n = self.inputs[name]
			fr = CodingFrame(self, n, label = label, name = name)
			fr.grid(row = 0, column = i, sticky = 'nswe')
			self.frs_coding[name] = fr
			i += 1
		
	def get(self):
		out = {}
		for name, fr in self.frs_coding.items():
			tmp = fr.get()
			out[name] = tmp
			# print(name, tmp)
		return out
		
	def set(self, codings):
		for name, coding in codings.items():
			self.frs_coding[name].set(coding)
			
	def save(self):
		save_data = self.get()
		return save_data
		
	def load(self, load_data):
		self.set(load_data)
	
	def test00(self):
		codings = {
			'X' : {'X[0]': [0, 0, 0], 'X[1]': [0, 0, 1], 'X[2]': [0, 1, 0], 'X[3]': [1, 0, 0], 'X[4]': [1, 1, 0]},
			'Y' : {'Y[0]': [0, 1], 'Y[1]': [1, 0], 'Y[2]': [1, 1]},
			'Z' : {'Z[0]': [0], 'Z[1]': [1]}}
		self.set(codings)
			
class ResultsFrame(tk.LabelFrame):
	def __init__(self, root, label = 'Результат'):
		super().__init__(root, text = label)
		self.bt_test00 = tk.Button(self, text = 'TEST', command = self.test01)
		self.bt_test00.grid(row = 0, column = 0)
		self.ens = []
		
	def test00(self):
		jumpsouts = (
			np.array([
				[3, 2, 2, 3, 0],
				[3, 1, 4, 0, 1],
				[0, 2, 2, 0, 3]]),
			np.array([
				[0, 1, 1, 1, 0],
				[0, 1, 1, 1, 0],
				[0, 1, 1, 0, 0]]))
		codings = {
			'X': {
				'X[0]': [0, 0],
				'X[1]': [0, 1],
				'X[2]': [1, 0]},
			'Y': {
				'Y[0]': [0, 0, 0],
				'Y[1]': [0, 0, 1],
				'Y[2]': [0, 1, 1],
				'Y[3]': [0, 1, 0],
				'Y[4]': [1, 0, 0]},
			'Z': {'Z[0]': [0], 'Z[1]': [1]}}
		self.derive_functions(jumpsouts, codings)
	
	def test01(self):
		'''Метод обращается к корневому окну, ищет среди виджетов таблицу переходов-выходов и таблици кодировок, получает от них данные и вызывает метод выведения логических функций'''
		rootwidgets = root.winfo_children()
		for widget in rootwidgets:
			if isinstance(widget, JumpsOutsTable):
				jumpsouts = widget.get()
				print('\n', widget)
				print(jumpsouts, '\n')
				
			elif isinstance(widget, CodingsFrame):
				codings = widget.get()
				print('\n', widget)
				print(codings, '\n')
			else:
				pass
		self.derive_functions(jumpsouts, codings)

		
	def derive_functions(self, jumpsouts, codings):
		'''Метод вывода функций'''
		self.jumpsouts = jumpsouts	# Кортеж с таблицами переходов и выходов
		self.codings = codings		#	Словарь с кодировками состояний
		# Определяем размер таблицы переходов/выходов
		shape = self.jumpsouts[0].shape
		rows = shape[0]
		columns = shape[1]
		ones_D = {}	# Словарь со списками единиц для D-триггеров
		ones_Z = {} # Словарь со списками единиц для выходов
		nD = len(codings['Y']['Y[0]'])
		nZ = len(codings['Z']['Z[0]'])
		print(f'Количество\n\tD-триггеров: {nD}\n\tВыходов: {nZ}\n')
		# print(shape)
		# print(f'№	Код	Переход	Выход')
		for i in range(columns):
			key_Y = f'Y[{i}]' # Ключ для извлечения текущей кодировки Y
			for j in range(rows):
				key_X = f'X[{j}]' # Ключ для извлечения текущей кодировки X
				# Создаём список с битами таблицы истинности. Это нужно для получения номера строки таблицы истинности
				bit_tab_n = []
				bit_tab_n.extend(codings['Y'][key_Y])
				bit_tab_n.extend(codings['X'][key_X])
				# Получаем номер строки таблицы истинности
				tab_n = bf.combine_bits_to_int(bit_tab_n, True)
				jump = self.jumpsouts[0][j, i]
				out = self.jumpsouts[1][j, i]
				key_state_Y = f'Y[{jump}]'
				key_state_Z = f'Z[{out}]'
				bit_state_Y = self.codings['Y'][key_state_Y]
				bit_state_Z = self.codings['Z'][key_state_Z]
				bf.comb_truthtable_ones_state_set('D', ones_D, bit_state_Y, tab_n)
				bf.comb_truthtable_ones_state_set('Z', ones_Z, bit_state_Z, tab_n)
				# print(f'{tab_n}	{bit_tab_n}	{jump}	{bit_state_Y}	{out}	{bit_state_Z}')
		print(ones_Z)
		print(ones_D)
		qX = len(codings['X']['X[0]'])
		qY = len(codings['Y']['Y[0]'])
		tmp0 = numerate_variables('x', qX)
		tmp1 = numerate_variables('y', qY)
		tmp1.extend(tmp0)
		xy = tmp1 # Список переменных функции
		# print(xy)
		q = qX + qY # Количество переменных в функции
		end_tt_row = bf.get_max_value(q) + 1
		# print(q, end_tt_row)
		# Давай сперва сделаем вручную, потом может поймём, как сделать более изящно
		# Сперва выходы
		self.equations = []
		for name, ones in ones_Z.items():
			equation = name
			# Создаём множество нулей, иначе функция будет неверной
			zeros = set()
			for i in range(end_tt_row):
				if i in ones:
					continue
				zeros.add(i)
			raw_foo = qm.qm(ones = ones, zeros = zeros)
			create_function_from_raw(raw_foo, xy)
				
			# print(raw_foo)
	
				
				
class CodingTableFrame(tk.LabelFrame):
	def __init__(self, root, label = 'Закодированная таблица'):
		super().__init__(root, text = label)
				
class CodingWindow(tk.Canvas):
	'''Пока не знаю, как сделать норм'''
	def __init__(self, root, n, name = 'X'):
		super().__init__(root, bg = 'white')
		self.name = name
		self.ch = 20	# cell h
		self.cw = 40	# cell w
		self.n_bits = bf.get_bits_num(n)
		self.n_cols = self.n_bits + 1
		self.n_rows = pow(2, self.n_bits) + 1
		self.width = self.cw * self.n_cols
		self.height = self.ch * self.n_rows
		print(self.width, self.height)
		super().configure(width = self.width, height = self.height)
		self.draw_grid()
		self.fill_table()
	
	def draw_grid(self):
		y = self.ch
		for i in range(self.n_rows - 1):
			self.create_line(0, y, self.width, y)
			y += self.ch
		x = self.cw
		for i in range(self.n_cols - 1):
			self.create_line(x, 0, x, self.height)
			x += self.cw
		
	def fill_table(self):
		y = 0
		for i in range(self.n_rows):
			if i == 0:
				y += self.ch
				continue
			text = f'{self.name}{i-1}' 
			self.create_text(0, y, text = text, anchor = 'n', fill = '#a00', activefill = '#0a0')
			y += self.ch
			

if __name__ == '__main__':
	logs_dir = 'logs'
	date = datetime.strftime(datetime.now(), "%Y.%m.%d %H.%M.%S")
	# log = logs_dir + '/' + str(date) + '.log'
	log = logs_dir + '/' + 'test.log'
	if os.path.exists(logs_dir):
		logging.basicConfig(level = logging.DEBUG, filename = log, filemode = 'w')
	else:
		os.mkdir(logs_dir)
		logging.basicConfig(level = logging.DEBUG, filename = log, filemode = 'w')	
	root = tk.Tk()
	w = win(root)
	root.mainloop()