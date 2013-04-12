
# -*- coding: utf-8 -*-
#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import rdbms
import time

CLOUDSQL_INSTANCE = 'graphdog'
CLOUDSQL_DATABASE = 'APP_sportsworldcup'
CLOUDSQL_CONNECTION = None
def sqlConnect():
	if not CLOUDSQL_CONNECTION:
		CLOUDSQL_CONNECTION=rdbms.connect(instance=CLOUDSQL_INSTANCE, database=CLOUDSQL_DATABASE, charset='utf8')

	return CLOUDSQL_CONNECTION

def sqlClose():
	if CLOUDSQL_CONNECTION:
		CLOUDSQL_CONNECTION.close()
		CLOUDSQL_CONNECTION=None


#############################################################################
# database class
#############################################################################
class UniqueConstraintViolation(Exception):
	def __init__(self, scope, value):
		super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))

class DB_AppScores():
	asid=None
	auInfo=None
	nick=""
	flag=""
	sTime=0
	uTime=0 
	eTime=0 
	gType="default"
	score=0
	isOver=False
	userdata = {}
	playTime = 0

	@classmethod
	def get(asid):
		conn = sqlConnect()
		cursor = conn.cursor()
		cursor.execute('SELECT (auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata) FROM AppScore WHERE no='+str(asid))
		rows = cursor.fetchall()
		sqlClose()

	@classmethod
	def query(where):
		conn = sqlConnect()
		cursor = conn.cursor()
		cursor.execute('SELECT (auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata) FROM AppScore '+where)
		rows = cursor.fetchall()
		return rows
		sqlClose()

	def set(row):
		pass

	def put(self):
		#update
		if not asid:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.sTime = int(time.time())
			cursor.execute('INSERT INTO AppScore (auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata) '
			 				'VALUES (%d, %s, %s, %d, %d, %d, %s, %d, %s)',
							(self.auInfo,self.nick,self.flag,self.sTime,self.uTime,self.eTime,self.gType,self.score,self.userdata
							))
			conn.commit()

			cursor.execute('SELECT LAST_INSERT_ID()')
			row = cursor.fetchall()[0]
			if row:
				self.asid=self.row[0]

			sqlClose()


	def toResult(self):
		_new = self.to_dict()
		_new['auid']=self.auInfo.id()
		_new['isover']=_new['isOver']
		_new['etime']=_new['eTime']
		_new['stime']=_new['uTime']
		_new['type']=_new['gType']
		_new['asid']=self.key.id()
		del _new['isOver']
		del _new['auInfo']
		del _new['eTime']
		del _new['sTime']
		del _new['uTime']
		del _new['gType']
		return _new

class DB_Developer(ndb.Model):
	email = ndb.StringProperty()
	name = ndb.StringProperty()
	group = ndb.StringProperty()
	test=ndb.JsonProperty()

class DB_DeveloperGroup(ndb.Model):
	name = ndb.StringProperty()

class DB_App(ndb.Model):
	aID = ndb.StringProperty()
	group = ndb.StringProperty()
	title = ndb.StringProperty()
	secretKey = ndb.StringProperty()
	#scoresSortType = ndb.StringProperty()
	scoresSortValue = ndb.IntegerProperty()
	developer = ndb.KeyProperty()
	useCPI = ndb.BooleanProperty()
	bannerImg = ndb.StringProperty()
	iconImg=ndb.StringProperty()
	store = ndb.JsonProperty(default={"ios":"storeid","android":"storeid"})
	descript = ndb.JsonProperty(default={"default":"descript"})
	cpiReward = ndb.JsonProperty(default={"default":100})

class DB_User(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	udid = ndb.StringProperty()
	installs = ndb.StringProperty(repeated=True)
	mail = ndb.StringProperty()
	CPIEvents = ndb.JsonProperty(default = [])
	joinDate = ndb.DateTimeProperty(auto_now_add=True)

class DB_AppUser(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	mail = ndb.StringProperty()
	uInfo  = ndb.KeyProperty(DB_User)
	createTime = ndb.StringProperty()
	udid = ndb.StringProperty()
	userdata = ndb.JsonProperty()
	joinDate = ndb.DateTimeProperty(auto_now_add=True)
	lastDate = ndb.DateTimeProperty(auto_now=True)
	lastNID = ndb.IntegerProperty(default = 0)
	requests = ndb.JsonProperty(default = [])

class DB_AppLog(ndb.Model):
	auInfo = ndb.KeyProperty(DB_AppUser)
	text = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class DB_AppScore(ndb.Model):

	def computePlayTime(self):
		if self.eTime and self.uTime:
			return self.eTime-self.uTime
		else:
			return 0
	auInfo=ndb.KeyProperty(DB_AppUser)
	nick=ndb.StringProperty()
	flag=ndb.StringProperty()
	sTime=ndb.IntegerProperty(default=0)
	uTime=ndb.IntegerProperty(default=0) 
	eTime=ndb.IntegerProperty(default=0) 
	gType=ndb.StringProperty(default='default')
	score=ndb.IntegerProperty(default=0)
	isOver=ndb.BooleanProperty(default=False)
	userdata = ndb.JsonProperty(default={})
	playTime = ndb.ComputedProperty(computePlayTime)



class DB_AppFlagScore(ndb.Model):
	date = ndb.StringProperty()
	flag = ndb.StringProperty()
	score = ndb.IntegerProperty()
	user = ndb.IntegerProperty()
	gType = ndb.StringProperty()
	
	def toResult(self):
		_new = self.to_dict()
		_new['type']=_new['gType']
		del _new['gType']
		return _new

class DB_AppMaxScore(ndb.Model):
	auInfo=ndb.KeyProperty(DB_AppUser)
	nick=ndb.StringProperty()
	flag=ndb.StringProperty()
	gType=ndb.StringProperty()
	score=ndb.IntegerProperty()
	sTime=ndb.IntegerProperty()
	eTime=ndb.IntegerProperty()
	userdata = ndb.JsonProperty(default={})
	
	def toResult(self):
		_new = self.to_dict()
		_new['auid']=self.auInfo.id()
		_new['etime']=_new['eTime']
		_new['stime']=_new['sTime']
		_new['type']=_new['gType']
		_new['awsid']=self.key.id()
		del _new['auInfo']
		del _new['eTime']
		del _new['sTime']
		del _new['gType']
		return _new

class DB_AppWeeklyScore(ndb.Model):
	auInfo=ndb.KeyProperty(DB_AppUser)
	nick=ndb.StringProperty()
	flag=ndb.StringProperty()
	week=ndb.IntegerProperty()
	gType=ndb.StringProperty()
	score=ndb.IntegerProperty()
	sTime=ndb.IntegerProperty()
	eTime=ndb.IntegerProperty()
	userdata = ndb.JsonProperty(default={})

	def toResult(self):
		_new = self.to_dict()
		_new['auid']=self.auInfo.id()
		_new['etime']=_new['eTime']
		_new['stime']=_new['sTime']
		_new['type']=_new['gType']
		_new['awsid']=self.key.id()
		del _new['auInfo']
		del _new['eTime']
		del _new['sTime']
		del _new['gType']
		return _new

class DB_AppNotice(ndb.Model):
	title=ndb.StringProperty()
	category = ndb.StringProperty()
	content = ndb.TextProperty()
	userdata = ndb.JsonProperty()
	platform = ndb.StringProperty()
	createTime = ndb.IntegerProperty()
	count = ndb.IntegerProperty()

class DB_AppRequest(ndb.Model):
	receiver = ndb.KeyProperty()
	sender = ndb.KeyProperty()
	category = ndb.StringProperty()
	content = ndb.StringProperty()
	userdata = ndb.JsonProperty(default={})

class DB_AppGiftcode(ndb.Model):
	code = ndb.StringProperty()
	category = ndb.StringProperty()
	value = ndb.IntegerProperty()
	user = ndb.KeyProperty()
	createTime = ndb.IntegerProperty()
	useTime = ndb.IntegerProperty()
	userdata = ndb.JsonProperty(default={})

class DB_AppImage(ndb.Model):
	imageName = ndb.StringProperty()
	developer = ndb.UserProperty()
	imgurl=""
	
class DB_AppData(ndb.Model):
	pass

