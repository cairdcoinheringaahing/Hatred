import random
import sys

code_page = '''¡¢£¤¥¦©¬®µ½¿€ÆÇÐÑ×ØŒÞßæçðıȷñ÷øœþ !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~¶°¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ƁƇƊƑƓƘⱮƝƤƬƲȤɓƈɗƒɠɦƙɱɲƥʠɼʂƭʋȥẠḄḌẸḤỊḲḶṂṆỌṚṢṬỤṾẈỴẒȦḂĊḊĖḞĠḢİĿṀṄȮṖṘṠṪẆẊẎŻạḅḍẹḥịḳḷṃṇọṛṣṭ§Äẉỵẓȧḃċḋėḟġḣŀṁṅȯṗṙṡṫẇẋẏż«»‘’“”'''

class attrdict(dict):
	def __init__(self, *args, **kwargs):
		dict.__init__(self, *args, **kwargs)
		self.__dict__ = self

	def __repr__(self):
		return 'attrdict(arity = {})'.format(self.arity)

	def __call__(self, *args):
		if hasattr(self, 'call'):
			func = self.call
			return func(*args)

		the_types = [type(arg) for arg in args]
		if self.arity == 0:
			func = self.call

		if self.arity == 1:
			if the_types[0] == str: func = self.strcall
			if the_types[0] in (int, float, complex): func = self.intcall
			if the_types[0] == list: func = self.arrcall
		
		if self.arity == 2:
			if the_types[0] == str:
				if the_types[1] == str: func = self.sscall
				if the_types[1] in (int, float, complex): func = self.sicall
				if the_types[1] == list: func = self.sacall

			if the_types[0] in (int, float, complex):
				if the_types[1] == str: func = self.iscall
				if the_types[1] in (int, float, complex): func = self.iicall
				if the_types[1] == list: func = self.iacall

			if the_types[0] == list:
				if the_types[1] == str: func = self.ascall
				if the_types[1] in (int, float, complex): func = self.aicall
				if the_types[1] == list: func = self.aacall

		return func(*args)

def arities(chain):
	return [link.arity for link in chain]

def dyadic_chain(chain, l, r):
	while chain:
		swap = False

		if 0 in arities(chain[:2]):
			chunk = chain[:2]
			chain = chain[2:]
			if len(chunk) == 2: a, b = chunk
			if len(chunk) == 1: a, = chunk

			if arities(chunk) == [0, 0]:
				l, r = a(), b()
			if arities(chunk) == [0, 1]:
				l, r = a(), b(r)
			if arities(chunk) == [0, 2]:
				l, r = a(), b(l, r)
			if arities(chunk) == [1, 0]:
				l, r = a(l), b()
			if arities(chunk) == [2, 0]:
				l, r = a(l, r), b()

			if arities(chunk) == [0]:
				l, r = a(), r

		else:
			chunk = chain[:3]
			chain = chain[3:]
			if len(chunk) == 3: a, b, c = chunk
			if len(chunk) == 2: a, b = chunk
			if len(chunk) == 1: a, = chunk

			if -1 in arities(chunk):
				chunk, broken = chunk[: arities(chunk).index(-1)], chunk[arities(chunk).index(-1)+1 :]
				chain = broken + chain
				swap = True

			if arities(chunk) == [1, 1, 1]:
				l, r = a(b(c(l))), l
			elif arities(chunk) == [1, 1, 2]:
				l, r = c(a(l), r), b(r)
			elif arities(chunk) == [1, 2, 1]:
				l, r = a(l), b(a(r), c(r))
			elif arities(chunk) == [1, 2, 2]:
				l, r = a(c(b(l, r), r)), c(l, r)

			elif arities(chunk) == [2, 1, 1]:
				l, r = a(l, r), c(b(r))
			elif arities(chunk) == [2, 1, 2]:
				l, r = a(l, b(r)), c(l, r)
			elif arities(chunk) == [2, 2, 1]:
				l, r = b(a(l, r), c(r)), l
			elif arities(chunk) == [2, 2, 2]:
				l, r = a(b(l, r), c(l, r)), c(b(l, r), a(l, r))

			elif arities(chunk) == [1, 1]:
				l, r = a(l), b(r)
			elif arities(chunk) == [1, 2]:
				l, r = a(l), b(l, r)
			elif arities(chunk) == [2, 1]:
				l, r = a(l, r), b(r)
			elif arities(chunk) == [2, 2]:
				l, r = a(l, r), b(l, r)

			elif arities(chunk) == [1]:
				l, r = a(l), r
			elif arities(chunk) == [2]:
				l, r = a(l, r), r

			elif arities(chunk) == []:
				l, r = l, r

			else:
				l_atom = random.choice(list(ATOMS.keys()))
				while ATOMS[l_atom].arity != 2: l_atom = random.choice(list(ATOMS.keys()))

				r_atom = random.choice(list(ATOMS.keys()))
				while ATOMS[r_atom].arity != 2: r_atom = random.choice(list(ATOMS.keys()))

				print('Random atoms chosen :', l_atom, 'and', r_atom, file = sys.stderr)

				l, r = ATOMS[l_atom](l, r), ATOMS[r_atom](l, r)

			if swap:
				l, r = r, l

	return l


def hatred_eval(code, arguments):
	return variadic_chain(parse_prog(code)[-1] if code else '', arguments)

def monadic_chain(chain, x):
	while chain:
		chunk = chain[:3]
		chain = chain[3:]
		if len(chunk) == 3: a, b, c = chunk
		if len(chunk) == 2: a, b = chunk
		if len(chunk) == 1: a, = chunk
		p = ATOMS['+']

		if arities(chunk) == [0, 0, 0]:
			x = p(x, p(a(), p(b(), c())))
		elif arities(chunk) == [0, 0, 1]:
			x = p(c(x), p(a(), b()))
		elif arities(chunk) == [0, 0, 2]:
			x = p(c(b(), x), a())
		elif arities(chunk) == [0, 1, 0]:
			x = p(x, b(p(a, c)))
		elif arities(chunk) == [0, 1, 1]:
			x = p(c(b(x)), a())
		elif arities(chunk) == [0, 1, 2]:
			x = c(x, b(a()))
		elif arities(chunk) == [0, 2, 0]:
			x = p(b(x, a()), c())
		elif arities(chunk) == [0, 2, 1]:
			x = c(b(a(), x))
		elif arities(chunk) == [0, 2, 2]:
			x = b(x, c(a(), x))

		elif arities(chunk) == [1, 0, 0]:
			x = a(p(x, p(b(), c())))
		elif arities(chunk) == [1, 0, 1]:
			x = c(p(a(x), b()))
		elif arities(chunk) == [1, 0, 2]:
			x = c(a(b()), x)
		elif arities(chunk) == [1, 1, 0]:
			x = a(p(b(x), c()))
		elif arities(chunk) == [1, 1, 1]:
			x = c(b(a(x)))
		elif arities(chunk) == [1, 1, 2]:
			x = c(a(x), b(x))
		elif arities(chunk) == [1, 2, 0]:
			x = a(b(x, c()))
		elif arities(chunk) == [1, 2, 1]:
			x = a(b(x, c(x)))
		elif arities(chunk) == [1, 2, 2]:
			x = b(a(x), c(x, a(x)))

		elif arities(chunk) == [2, 0, 0]:
			x = p(a(x, c()), b())
		elif arities(chunk) == [2, 0, 1]:
			x = a(c(x), b())
		elif arities(chunk) == [2, 0, 2]:
			x = c(a(x, b()), b())
		elif arities(chunk) == [2, 1, 0]:
			x = a(b(x), p(x, c()))
		elif arities(chunk) == [2, 1, 1]:
			x = a(c(b(x)), x)
		elif arities(chunk) == [2, 2, 0]:
			x = a(b(x, c()), x)
		elif arities(chunk) == [2, 2, 1]:
			x = a(c(x), b(x, x))
		elif arities(chunk) == [2, 2, 2]:
			x = a(x, b(x, c(x, x)))

		elif arities(chunk) == [0, 0]:
			x = p(x, p(a(), b()))
		elif arities(chunk) == [0, 1]:
			x = p(x, a(b()))
		elif arities(chunk) == [0, 2]:
			x = b(x, a())
		elif arities(chunk) == [1, 0]:
			x = a(p(x, b()))
		elif arities(chunk) == [1, 1]:
			x = b(a(x))
		elif arities(chunk) == [1, 2]:
			x = b(x, a(x))
		elif arities(chunk) == [2, 0]:
			x = a(x, b())
		elif arities(chunk) == [2, 1]:
			x = a(b(x), x)
		elif arities(chunk) == [2, 2]:
			x = a(x, b(x, x))

		elif arities(chunk) == [0]:
			x = p(x, a())
		elif arities(chunk) == [1]:
			x = a(x)
		elif arities(chunk) == [2]:
			x = a(x, x)

		elif arities(chunk) == []:
			x = x

		else:
			atom = random.choice(list(ATOMS.keys()))
			while ATOMS[atom].arity != 1:
				atom = random.choice(list(ATOMS.keys()))

			print('Random atom chosen :', atom, file = sys.stderr)

			x = ATOMS[atom](x)

	return x

def parse_code(prog_links):
	links = []
	for p_link in prog_links:
		chain = []
		for char in p_link:
			if char in ATOMS.keys():
				chain.append(ATOMS[char])
			elif char in QUICKS.keys():
				popped = []
				take = QUICKS[char].take
				for _ in range(take):
					popped.append(chain.pop())
				chain.append(QUICKS[char].call(popped))
		links.append(chain)
	return links

def parse_prog(program):
	return parse_code(program.split('¶'))

def take_links(take, arity):
	return attrdict(
		take = take,
		call = lambda links: attrdict(
			arity = arity,
			call = [
				lambda: niladic_chain(links),
				lambda x: monadic_chain(links, x),
				lambda x, y: dyadic_chain(links, x, y)
			][arity],
		),
	)

def to_s(val):
	return str(val)

def to_i(val):
	return int(val)

def variadic_chain(chain, args):
	if len(args) == 0:
		pass

	if len(args) == 1:
		return monadic_chain(chain, *args)

	if len(args) == 2:
		return dyadic_chain(chain, *args)

ATOMS = {

	'0': attrdict(
		arity = 0,
		call = lambda: 0,
	),

	'1': attrdict(
		arity = 1,
		call = lambda x: '1',
	),

	'H': attrdict(
		arity = 1,
		intcall = lambda x: x / 2,
		strcall = lambda x: x,
		arrcall = lambda x: [x[:len(x) // 2], x[len(x) // 2:]],
	),

	'I': attrdict(
		arity = 1,
		call = lambda x: x
	),

	'+': attrdict(
		arity = 2,
		iicall = lambda x, y: to_s(x) + to_s(y),
		iscall = lambda x, y: to_s(x) + y,
		iacall = lambda x, y: [x] + y,

		sicall = lambda x, y: to_i(x) + y,
		sscall = lambda x, y: to_i(x) + to_i(y),
		sacall = lambda x, y: to_i(x) + to_i(y),

		aicall = lambda x, y: [to_i(l) + to_i(y) for l in x],
		ascall = lambda x, y: to_s(x) + y,
		aacall = lambda x, y: [to_s(l) + to_s(r) for l, r in zip(x, y)],
	),

	',': attrdict(
		arity = 2,
		call = lambda x, y: [x, y],
	),

	'"': attrdict(
		arity = -1,
	),

}

QUICKS = {

	'®': take_links(2, 0),
	'©': take_links(4, 0),

	'2': take_links(2, 1),
	'3': take_links(3, 1),
	'4': take_links(4, 1),
	'5': take_links(5, 1),
	'6': take_links(6, 1),
	'7': take_links(7, 1),
	'8': take_links(8, 1),
	'9': take_links(9, 1),

	'²': take_links(2, 2),
	'³': take_links(3, 2),
	'⁴': take_links(4, 2),
	'⁵': take_links(5, 2),
	'⁶': take_links(6, 2),
	'⁷': take_links(7, 2),
	'⁸': take_links(8, 2),
	'⁹': take_links(9, 2),

	'@': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 2,
			call = lambda x, y: dyadic_chain(links, y, x),
		),
	),

	'(': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 1,
			call = lambda x: dyadic_chain(links, x, x),
		),
	),

	')': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 2,
			call = lambda x, y: dyadic_chain(links, y, y),
		),
	),

	'{': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 2,
			call = lambda x, y: monadic_chain(links, x),
		),
	),

	'}': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 2,
			call = lambda x, y: monadic_chain(links, y),
		),
	),

	'/': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 1,
			call = reduce,
		),
	),

	'\\': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = 1,
			call = cum_reduce,
		),
	),

	'€': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = max([1] + arities(links)),
			call = map_over,
		),
	),

	'Ɱ': attrdict(
		take = 1,
		call = lambda links: attrdict(
			arity = max([1] + arities(links)),
			call = map_over_right,
		),
	),
	

}

print(hatred_eval('HH',    (2,))) # 0.5
print(hatred_eval('H,HH2', (2,))) # [[2], [0.5]]
print(hatred_eval('HHH2,', (2,))) # [1.0, 0.5]

print(hatred_eval('HH',    (1, 2))) # 0.5
print(hatred_eval('H,HH2', (1, 2))) # 0.5
print(hatred_eval('HHH2,', (1, 2))) # [0.5, 2]

print(hatred_eval('HH"',    (1, 2))) # 1
print(hatred_eval('H,HH2"', (1, 2))) # [1.0, 0.5]
print(hatred_eval('HHH2,"', (1, 2))) # 0.5
