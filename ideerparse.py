import urllib3
from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_creator import Secret, Base, cls

cls()

engine = create_engine("sqlite:///data.db")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

Session = DBSession()

def add_Secret(genre, text='-', number = 0, commit=False):
    Session.add(Secret(text=text, genre=genre, number=number))
    if commit:
        Session.commit()

def parse(s):
	while s.find('tag" href="/secrets/')>0:
		number = s[s.find('"date" href="/')+14:s.find('/"> 2')]
		s = s[s.find('tag" href="/secrets/'):]
		s = s[s.find('>')+2:]
		genre = s[:s.find('<')-1]
		text = s[s.find('">')+2:s.find('</d')]
		print(genre, '\n', text)
		if not Session.query(Secret).filter(Secret.number == number).all():
			add_Secret(genre, text, number)
	Session.commit()

def download(n):
	ok = False
	while not ok:
		ok = True
		try:
			s = urllib3.PoolManager().request('GET', "http://ideer.ru", retries = 10).data.decode('utf8')
		except IOError:
			print('IOError')
			ok = False
			sleep(0.5)
	s = s[s.find('class="date" h')+2:]
	i = int(s[s.find('/')+1:s.find('>')-1]) - 3685 - len(Session.query(Secret).filter().all())
	while n > 0:
		ok = False
		while not ok: 
			ok = True
			try:
				s = urllib3.PoolManager().request('GET', "http://ideer.ru/?page=" + str(i), retries = 10).data.decode('utf8')
				if s[1] == 'h':
					cls()
					print('STUError')
					ok = False
					sleep(0.5)
			except IOError:
				cls()
				print('IOError')
				ok = False
				sleep(0.5)
		parse(s)
		n -= 15
		i -= 15
		cls()
		print(i)
		sleep(0.5)

from random import sample

def show(genre, n):
	m = Session.query(Secret).filter(Secret.genre == genre.decode('utf8')).all()
	if n > len(m): n = len(m)
	a = sample(range(len(m)), n)
	for i in a: m[i].repr()

download(50000)
