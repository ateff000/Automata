def get_bits_num(n):
	'''Нахоит количество битов в числе'''
	div = n
	cnt = 0
	while (div > 0):
		div = int(div/2)
		cnt += 1
	return cnt
	
def get_max_value(n):
	'''Возвращает  число из n бит'''
	return pow(2, n) - 1
	

def split_int_to_bits(x, l, reverse = False):
	'''Возвращает число x в двоичном виде в качестве списка длинной l'''
	out = []
	for i in range(l):
		tmp = x >> i & 1
		out.append(tmp)
	if reverse == True:
		out.reverse()
	return out

def combine_bits_to_int(bits, reverse = False):
	out = 0
	if reverse:
		bits.reverse()
	for i, bit in enumerate(bits):
		tmp = bit << i
		out |= tmp
	if reverse:
		bits.reverse()
	return out
	
def bitlist_to_string(bitlist):
	# return str(bitlist)
	out = ''
	for bit in bitlist:
		out += str(bit)
	return out
	
if __name__ == '__main__':
	# while 1:
		# n = int(input('>>>	'))
		# print(get_bits_num(n))
		
	# a = [0, 1, 1, 0, 1]
	for i in range(8):
		a = split_int_to_bits(i, 3, True)
		# print(a)
		b = combine_bits_to_int(a, True)
		# print(b)
		print(a, b)
	# print(bitlist_to_string(a))
	# print(combine_bits_to_int(a))
	
def comb_truthtable_ones(name, ones, n, value, tab_n):
	'''	Функция берет словарь со списками единиц и наполняет эти списки номерами строк таблицы истинности, если разложенное значение в конкретном выходе таблицы равно единице
		name -- название выходов таблицы истинности,
		ones -- словарь с единицами для таблици истинности,
		n -- количество выходов таблицы истинности,
		value -- совокупное целочисленное значение выходов таблицы истинности (т.е. если value = 5, а n = 3, то выходы будут равны [1, 0, 1], )
		tab_n -- номер строки таблицы истинности
		'''
	if ones == {}:
		for i in range(n):
			tmp = f'{name}[{n - i - 1}]'
			ones[tmp] = []
	bits = split_int_to_bits(value, n, reverse = True)
	for i in range(n):
		tmp = f'{name}[{n - i - 1}]'
		if bits[i] == 1:
			ones[tmp].append(tab_n)

def comb_truthtable_ones_state(name, ones, state, tab_n):
	'''	Функция берет словарь со списками единиц и наполняет эти списки номерами строк таблицы истинности, если разложенное значение в конкретном выходе таблицы равно единице
		name -- название выходов таблицы истинности,
		ones -- словарь с единицами для таблици истинности,
		state -- список со значениями выходов таблицы истинности в текущей строке
		tab_n -- номер строки таблицы истинности
		'''
	n = len(state)
	if ones == {}:
		for i in range(n):
			tmp = f'{name}[{n - i - 1}]'
			ones[tmp] = []
	for i in range(n):
		tmp = f'{name}[{n - i - 1}]'
		if state[i] == 1:
			ones[tmp].append(tab_n)
			
def comb_truthtable_ones_state_set(name, ones, state, tab_n):
	'''Тоже, что и функция выше, только работает с множествами вместо списков	'''
	n = len(state)
	if ones == {}:
		for i in range(n):
			tmp = f'{name}[{n - i - 1}]'
			ones[tmp] = set()
	for i in range(n):
		tmp = f'{name}[{n - i - 1}]'
		if state[i] == 1:
			ones[tmp].add(tab_n)