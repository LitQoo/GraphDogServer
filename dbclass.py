
# -*- coding: utf-8 -*-
#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import rdbms
import time
import json
import logging
from google.appengine.api import memcache
import datetime
import webapp2

GD_CLOUDSQL_INSTANCE_DEFAULT = 'graphdogserver:graphdog'
#GD_CLOUDSQL_DBNAME = None
#GD_CLOUDSQL_CONNECT = None

def setSqlConnect(aid=None,dbname=None,instance=None):

	#global GD_CLOUDSQL_INSTANCE
	#global GD_CLOUDSQL_DBNAME
	#global GD_CLOUDSQL_CONNECT

	app = webapp2.get_app()

	if aid:
		app.request.registry['GD_CLOUDSQL_DBNAME'] = 'APP_'+aid
		#GD_CLOUDSQL_DBNAME = 'APP_'+aid

	if dbname:
		#GD_CLOUDSQL_DBNAME = dbname
		app.request.registry['GD_CLOUDSQL_DBNAME'] = dbname
	
	if instance:
		GD_CLOUDSQL_INSTANCE = instance
		app.request.registry['GD_CLOUDSQL_INSTANCE'] = instance

def sqlConnect():



	#logging.info('setsqlConnect')
	#setSqlConnect(aid,dbname,instance)
	#return rdbms.connect(instance=GD_CLOUDSQL_INSTANCE, database=GD_CLOUDSQL_DBNAME, charset='utf8')
	#logging.info('if not GD_CLOUDSQL_CONNECT')
	#logging.info(GD_CLOUDSQL_CONNECT)

	app = webapp2.get_app()
	try:
		GD_CLOUDSQL_CONNECT = app.request.registry['GD_CLOUDSQL_CONNECT']
	except:
		GD_CLOUDSQL_INSTANCE = app.request.registry['GD_CLOUDSQL_INSTANCE']
		GD_CLOUDSQL_DBNAME = app.request.registry['GD_CLOUDSQL_DBNAME']
		GD_CLOUDSQL_CONNECT = rdbms.connect(instance=GD_CLOUDSQL_INSTANCE, database=GD_CLOUDSQL_DBNAME, charset='utf8')
		app.request.registry['GD_CLOUDSQL_CONNECT'] = GD_CLOUDSQL_CONNECT

	return GD_CLOUDSQL_CONNECT

	'''if not GD_CLOUDSQL_CONNECT:
		GD_CLOUDSQL_CONNECT = rdbms.connect(instance=GD_CLOUDSQL_INSTANCE, database=GD_CLOUDSQL_DBNAME, charset='utf8')

	#logging.info('try GD_CLOUDSQL_CONNECT.CheckOpen()')
	#try:
	#	GD_CLOUDSQL_CONNECT.CheckOpen()
	#except:
	#	logging.info('reconnect')
	#	GD_CLOUDSQL_CONNECT = rdbms.connect(instance=GD_CLOUDSQL_INSTANCE, database=GD_CLOUDSQL_DBNAME, charset='utf8')

	#logging.info('return GD_CLOUDSQL_CONNECT')
	#logging.info(GD_CLOUDSQL_CONNECT)

	import weakref

	ref_gdcc = weakref.ref(GD_CLOUDSQL_CONNECT)
	return ref_gdcc()'''

def newSqlConnect(aid=None,dbname=None,instance=None):
	setSqlConnect(aid,dbname,instance)
	sqlConnect()

def sqlClose():
	#global GD_CLOUDSQL_INSTANCE
	#global GD_CLOUDSQL_DBNAME
	#global GD_CLOUDSQL_CONNECT
	app = webapp2.get_app()

	try:
		GD_CLOUDSQL_CONNECT = app.request.registry['GD_CLOUDSQL_CONNECT']
	except:
		GD_CLOUDSQL_CONNECT = None

	if GD_CLOUDSQL_CONNECT:
		try:
			GD_CLOUDSQL_CONNECT.close()
		except:
			logging.info('close sql error')

		GD_CLOUDSQL_CONNECT=None
		app.request.registry['GD_CLOUDSQL_CONNECT'] = None

def createDatabaseAndConnect(aid=None,dbname=None,instance=None):
		conn =newSqlConnect(dbname='graphdog')
		cursor = conn.cursor()

		if aid:
			dbname = 'APP_'+aid

		query = """create database %s charset utf8;"""%dbname
		cursor.execute(query)
		createQuery = conn.commit()
		#logging.info('commit sql')
		#conn.close()

		sqlClose()

		setSqlConnect(dbname=dbname,instance=instance)





#############################################################################
# database class
#############################################################################
class UniqueConstraintViolation(Exception):
	def __init__(self, scope, value):
		super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))

class DB_AppScores():
	asid=0
	auInfo=0
	nick=""
	flag=""
	sTime=0
	uTime=0 
	eTime=0 
	gType="default"
	score=0
	userdata = {}
	isOver=False
	playTime = 0

	@staticmethod
	def createTable():
		conn = sqlConnect()
		cursor = conn.cursor()
		query = """CREATE TABLE IF NOT EXISTS `AppScore` (
				  `no` int(7) NOT NULL auto_increment,
				  `auInfo` int(20) NOT NULL default '0',
				  `nick` varchar(40) NOT NULL default '',
				  `flag` varchar(20) NOT NULL default '',
				  `gType` varchar(40) NOT NULL default '',
				  `score` int(10) NOT NULL default '0',
				  `sTime` int(12) NOT NULL default '0',
				  `uTime` int(12) NOT NULL default '0',
				  `eTime` int(12) NOT NULL default '0',
				  `userdata` text NOT NULL,
				  PRIMARY KEY  (`no`),
				  KEY `gType` (`gType`),
				  KEY `score` (`score`),
				  KEY `sTime` (`sTime`),
				  KEY `auInfo` (`auInfo`)
				)
				ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

		cursor.execute(query)
		createQuery = conn.commit()

		#cursor.close()
		#conn.close()


	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppScore WHERE no=%s limit 1' % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()
		return DB_AppScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppScore WHERE no=%s limit 1' % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()
		if row:
			return DB_AppScores.set(row)
		else:
			_new = DB_AppScores()
			_new.asid = findID
			return _new

	@staticmethod
	def query(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no ,auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppScore'
		if where:
			query=query+' '+where

		cursor.execute(query)
		rows = cursor.fetchall()
		cursor.close()
		#conn.close()
		return rows

	@staticmethod
	def count(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT COUNT(no) FROM AppScore'
		if where:
			query=query+' '+where

		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()
		return row[0]
	
	@staticmethod
	def set(row):
		_new = DB_AppScores()
		_new.asid = row[0]
		_new.auInfo = row[1]
		_new.nick = row[2]
		_new.flag = row[3]
		_new.sTime = row[4]
		_new.uTime = row[5]
		_new.eTime = row[6]
		_new.gType = row[7]
		_new.score = row[8]
		_new.userdata = json.loads(row[9])
		_new.isOver = False

		if _new.eTime!=0:
			_new.isOver=True

		if _new.eTime!=0:
			_new.playTime = _new.eTime-_new.sTime
		else:
			_new.playTime = int(time.time())-_new.sTime

		return _new

	def put(self):
		#write
		if not self.asid:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.sTime = int(time.time())
			cursor.execute('INSERT INTO AppScore (auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata) '
			 				'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
							(self.auInfo,self.nick,self.flag,self.sTime,self.uTime,self.eTime,self.gType,self.score,json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False)
							))
			conn.commit()
			#cursor = conn.cursor()

			cursor.execute('SELECT LAST_INSERT_ID() FROM AppScore limit 1')
			row = cursor.fetchone()
			cursor.close()
			#conn.close()

			if row:
				self.asid=row[0]

		else:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.uTime = int(time.time())
			cursor.execute('UPDATE AppScore SET auInfo=%s, nick=%s, flag=%s, sTime=%s, uTime=%s, eTime=%s, gType=%s, score=%s, userdata=%s WHERE no=%s',
				(	self.auInfo,
					self.nick,
					self.flag,
					self.sTime,
					self.uTime,
					self.eTime,
					self.gType,
					self.score,
					json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False),
					self.asid
				))
			conn.commit()
			cursor.close()
			#conn.close()

	def to_dict(self):
		_new = {}
		_new['asid']=self.asid
		_new['auinfo']=self.auInfo
		_new['nick']=self.nick
		_new['flag']=self.flag
		_new['stime']=self.sTime
		_new['utime']=self.uTime
		_new['etime']=self.eTime
		_new['type']=self.gType
		_new['score']=self.score
		_new['userdata']=self.userdata
		_new['isover']=self.isOver
		_new['playtime']=self.playTime
		return _new

class DB_AppMaxScores():

	no=0
	amsid=""
	auInfo=0
	nick=""
	flag=""
	sTime=0
	uTime=0 
	eTime=0 
	gType="default"
	score=0
	userdata = {}
	isOver=False
	playTime = 0

	@staticmethod
	def createTable():
		conn = sqlConnect()
		cursor = conn.cursor()
		query = """
					CREATE TABLE IF NOT EXISTS `AppMaxScore` (
						`no` int(7) NOT NULL auto_increment,
						`amsid` varchar(30) NOT NULL default '0',
						`auInfo` int(20) NOT NULL default '0',
						`nick` varchar(40) NOT NULL default '',
						`flag` varchar(20) NOT NULL default '',
						`gType` varchar(40) NOT NULL default '',
						`score` int(10) NOT NULL default '0',
						`sTime` int(12) NOT NULL default '0',
						`uTime` int(12) NOT NULL default '0',
						`eTime` int(12) NOT NULL default '0',
						`userdata` text NOT NULL,
						PRIMARY KEY  (`no`),
						KEY `amsid` (`amsid`),
						KEY `gType` (`gType`),
						KEY `score` (`score`),
						KEY `auInfo` (`auInfo`)
					)
					ENGINE=InnoDB DEFAULT CHARSET=utf8;
				"""
		cursor.execute(query)
		createQuery = conn.commit()
		cursor.close()
		#conn.close()

	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,amsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppMaxScore WHERE amsid='%s' limit 1" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()
		return DB_AppMaxScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,amsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppMaxScore WHERE amsid='%s' limit 1" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()

		if row:
			return DB_AppMaxScores.set(row)
		else:
			_new = DB_AppMaxScores()
			_new.amsid = findID
			return _new

	@staticmethod
	def query(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no,amsid ,auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppMaxScore'
		if where:
			query=query+' '+where

		cursor.execute(query)
		rows = cursor.fetchall()
		cursor.close()
		#conn.close()

		return rows

	@staticmethod
	def count(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT COUNT(no) FROM AppMaxScore'

		if where:
			query=query+' '+where

		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()

		return row[0]
	
	@staticmethod
	def set(row):
		_new = DB_AppMaxScores()
		_new.no = row[0]
		_new.amsid = row[1]
		_new.auInfo = row[2]
		_new.nick = row[3]
		_new.flag = row[4]
		_new.sTime = row[5]
		_new.uTime = row[6]
		_new.eTime = row[7]
		_new.gType = row[8]
		_new.score = row[9]
		_new.userdata = json.loads(row[10])
		_new.isOver = False

		if _new.eTime!=0:
			_new.isOver=True

		if _new.eTime!=0:
			_new.playTime = _new.eTime-_new.sTime
		else:
			_new.playTime = int(time.time())-_new.sTime

		return _new

	def put(self):
		#write
		if not self.no:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.sTime = int(time.time())
			cursor.execute('INSERT INTO AppMaxScore (amsid,auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata) '
							'VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)',
							(self.amsid,self.auInfo,self.nick,self.flag,self.sTime,self.uTime,self.eTime,self.gType,self.score,json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False)
							))
			
			conn.commit()
			cursor.execute('SELECT LAST_INSERT_ID() FROM AppMaxScore limit 1')
			row = cursor.fetchone()
			cursor.close()
			#conn.close()
			if row:
				self.no=row[0]

		else:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.uTime = int(time.time())
			cursor.execute('UPDATE AppMaxScore SET auInfo=%s, nick=%s, flag=%s, sTime=%s, uTime=%s, eTime=%s, gType=%s, score=%s, userdata=%s WHERE no=%s',
				(	self.auInfo,
					self.nick,
					self.flag,
					self.sTime,
					self.uTime,
					self.eTime,
					self.gType,
					self.score,
					json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False),
					self.no
				))

			conn.commit()
			cursor.close()
			#conn.close()

	def to_dict(self):
		_new = {}
		_new['amsid']=self.amsid
		_new['auid']=self.auInfo
		_new['nick']=self.nick
		_new['flag']=self.flag
		_new['stime']=self.sTime
		_new['utime']=self.uTime
		_new['etime']=self.eTime
		_new['type']=self.gType
		_new['score']=self.score
		_new['userdata']=self.userdata
		_new['isover']=self.isOver
		_new['playtime']=self.playTime
		return _new


class DB_AppWeeklyScores():
	no = 0
	awsid=""
	auInfo=0
	nick=""
	flag=""
	sTime=0
	uTime=0 
	eTime=0 
	gType="default"
	score=0
	week=0
	userdata = {}
	isOver=False
	playTime = 0

	@staticmethod
	def createTable():
		conn = sqlConnect()
		cursor = conn.cursor()
		query = """
					CREATE TABLE IF NOT EXISTS `AppWeeklyScore` (
						`no` int(7) NOT NULL auto_increment,
						`awsid` varchar(30) NOT NULL default '0',
						`auInfo` int(20) NOT NULL default '0',
						`week` int(20) NOT NULL default '0',
						`nick` varchar(40) NOT NULL default '',
						`flag` varchar(20) NOT NULL default '',
						`gType` varchar(40) NOT NULL default '',
						`score` int(10) NOT NULL default '0',
						`sTime` int(12) NOT NULL default '0',
						`uTime` int(12) NOT NULL default '0',
						`eTime` int(12) NOT NULL default '0',
						`userdata` text NOT NULL,
						PRIMARY KEY  (`no`),
						KEY `awsid` (`awsid`),
						KEY `gType` (`gType`),
						KEY `score` (`score`),
						KEY `week` (`week`),
						KEY `auInfo` (`auInfo`)
					)
					ENGINE=InnoDB DEFAULT CHARSET=utf8;
				"""
		cursor.execute(query)
		createQuery = conn.commit()
		cursor.close()
		#conn.close()

	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,awsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week FROM AppWeeklyScore WHERE awsid='%s' limit 1" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		return DB_AppWeeklyScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,awsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week FROM AppWeeklyScore WHERE awsid='%s' limit 1" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()

		if row:
			return DB_AppWeeklyScores.set(row)
		else:
			_new = DB_AppWeeklyScores()
			_new.awsid = findID
			return _new

	@staticmethod
	def query(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no,awsid ,auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week FROM AppWeeklyScore'
		if where:
			query=query+' '+where

		cursor.execute(query)
		rows = cursor.fetchall()
		cursor.close()
		#conn.close()
		return rows

	@staticmethod
	def count(where=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT COUNT(no) FROM AppWeeklyScore'
		if where:
			query=query+' '+where

		cursor.execute(query)
		row = cursor.fetchone()
		cursor.close()
		#conn.close()
		return row[0]
	
	@staticmethod
	def set(row):
		_new = DB_AppWeeklyScores()
		_new.no = row[0]
		_new.awsid = row[1]
		_new.auInfo = row[2]
		_new.nick = row[3]
		_new.flag = row[4]
		_new.sTime = row[5]
		_new.uTime = row[6]
		_new.eTime = row[7]
		_new.gType = row[8]
		_new.score = row[9]
		_new.userdata = json.loads(row[10])
		_new.week = row[11]
		_new.isOver = False

		if _new.eTime!=0:
			_new.isOver=True

		if _new.eTime!=0:
			_new.playTime = _new.eTime-_new.sTime
		else:
			_new.playTime = int(time.time())-_new.sTime

		return _new

	def put(self):
		#write
		if not self.no:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.sTime = int(time.time())
			tp = (self.awsid,self.auInfo,self.nick,self.flag,self.sTime,self.uTime,self.eTime,self.gType,self.score,json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False),self.week)
			cursor.execute('INSERT INTO AppWeeklyScore (awsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week) '
							'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
							tp)
			conn.commit()

			cursor.execute('SELECT LAST_INSERT_ID() FROM AppWeeklyScore limit 1')
			row = cursor.fetchone()
			cursor.close()
			#conn.close()
			if row:
				self.no=row[0]

		else:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.uTime = int(time.time())
			cursor.execute("UPDATE AppWeeklyScore SET auInfo=%s, nick=%s, flag=%s, sTime=%s, uTime=%s, eTime=%s, gType=%s, score=%s, userdata=%s,week=%s WHERE no=%s",
				(	self.auInfo,
					self.nick,
					self.flag,
					self.sTime,
					self.uTime,
					self.eTime,
					self.gType,
					self.score,
					json.dumps(self.userdata,encoding="utf-8",ensure_ascii=False),
					self.week,
					self.no
				))
			conn.commit()
			cursor.close()
			#conn.close()

	def to_dict(self):
		_new = {}
		_new['awsid']=self.awsid
		_new['auid']=self.auInfo
		_new['nick']=self.nick
		_new['flag']=self.flag
		_new['stime']=self.sTime
		_new['utime']=self.uTime
		_new['etime']=self.eTime
		_new['type']=self.gType
		_new['score']=self.score
		_new['userdata']=self.userdata
		_new['week']=self.week
		_new['isover']=self.isOver
		_new['playtime']=self.playTime
		return _new


class DB_Developer(ndb.Model):
	email = ndb.StringProperty()
	name = ndb.StringProperty()
	group = ndb.StringProperty(default="")

class DB_DeveloperGroup(ndb.Model):
	name = ndb.StringProperty()

class DB_App(ndb.Model):
	aID = ndb.StringProperty()
	group = ndb.StringProperty(default="")
	title = ndb.StringProperty(default="")
	secretKey = ndb.StringProperty(default="ABCDEFGH")
	#scoresSortType = ndb.StringProperty()
	scoresSortValue = ndb.IntegerProperty(default=100)
	developer = ndb.KeyProperty()
	useCPI = ndb.BooleanProperty(default=False)
	bannerImg = ndb.StringProperty(default="")
	iconImg=ndb.StringProperty(default="")
	store = ndb.JsonProperty(default={"ios":"storeid","android":"storeid"})
	descript = ndb.JsonProperty(default={"default":"descript"})
	cpiReward = ndb.JsonProperty(default={"default":100})
	dbInstance= ndb.StringProperty(default=GD_CLOUDSQL_INSTANCE_DEFAULT)
	isPutOn = False

	def putOn(self):
		self.isPutOn = True

	def doPut(self):
		if self.isPutOn==True:
			self.put()

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
	version = ndb.IntegerProperty(default=0)
	loginCount = ndb.IntegerProperty(default=1)
	grade = ndb.StringProperty(default="")

	def calcActiveTime(self):
		if self.lastDate and self.joinDate:
			return int((datetime.datetime.now() - self.lastDate).total_seconds())
		else:
			return 0

	activeTime = ndb.ComputedProperty(calcActiveTime)
	isPutOn = False

	def putOn(self):
		self.isPutOn = True

	def doPut(self):
		if self.isPutOn==True:
			self.put()

	def toResult(self):
		_new = self.to_dict()
		if self.uInfo:
			_new['uid']=self.uInfo.id()
		_new['id']=self.key.id()
		_new['joindate']=time.mktime(self.joinDate.timetuple())
		_new['lastdate']=time.mktime(self.lastDate.timetuple())
		_new['logincount']=self.loginCount

		del _new['loginCount']
		del _new['uInfo']
		del _new['joinDate']
		del _new['lastDate']
		return _new


class DB_AppVersions(ndb.Model):
	version = ndb.IntegerProperty(default=0)
	apiVersion = ndb.IntegerProperty(default=0)
	platform = ndb.StringProperty(default="")
	createTime = ndb.DateTimeProperty(auto_now_add=True)
	comment = ndb.StringProperty(default="")
	def toResult(self):
		_new = self.to_dict()
		_new['id']=self.key.id()
		_new['createtime']=time.mktime(self.createTime.timetuple())
		del _new['createTime']
		return _new

class DB_AppStats(ndb.Model):
	year = ndb.IntegerProperty()
	month = ndb.IntegerProperty()
	day = ndb.IntegerProperty()
	ymd = ndb.IntegerProperty()
	statsData = ndb.JsonProperty(default={})
	
	def toResult(self):
		_new = self.to_dict()
		if self.key:
			_new['id']=self.key.id()
		return _new

	@staticmethod
	def getInMC():
		#today = "20110606"
		#todayh = "2013052201"
		today = datetime.date.today().strftime("%Y%m%d")
		todayh = time.strftime("%Y%m%d%H", time.localtime(time.time()))
		data = memcache.get("stats")		
		when = memcache.get("stats_when")
		whenh = memcache.get("stats_whenh")
		if not when:
			when = today
		if not whenh:
			whenh = todayh

		if not data:
			data = {}

		if todayh != whenh:
			#데이터저장 when꺼를들고오기~~
			stats = DB_AppStats.get_or_insert("stats_"+when)
			stats.year = int(when[0:4])
			stats.month = int(when[4:6])
			stats.day = int(when[6:8])
			stats.ymd = int(when)
			stats.statsData,data = DB_AppStats.savesafe(stats.statsData,data)

			stats.put()
			#새값생성
			if today != when:
				newdata={}
				DB_AppStats.setInMC(newdata)
				return newdata
			else:
				DB_AppStats.setInMC(data)

		return data

	@staticmethod
	def setInMC(data):
		today = datetime.date.today().strftime("%Y%m%d")
		todayh = time.strftime("%Y%m%d%H", time.localtime(time.time()))
		#today = "20110606"
		#todayh = "2011060603"
		memcache.set("stats",data)
		memcache.set("stats_when",today)
		memcache.set("stats_whenh",todayh)
		
	@staticmethod
	def countStatHour(category,count=1):
		stats = DB_AppStats.getInMC()
		hour = int(datetime.datetime.now().hour)
		if not stats.get(category):
			stats[category]=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		elif type(stats.get(category)) != list:
			return

		try:
			stats[category][hour]+=count
		except KeyError:
			stats[category][hour]=count
		DB_AppStats.setInMC(stats)
		
	@staticmethod
	def countStatKey(category,key,count=1):
		stats = DB_AppStats.getInMC()
		if not stats.get(category):
			stats[category]={}
		elif type(stats.get(category)) != dict:
			return

		try:
			stats[category][key]+=count
		except KeyError:
			stats[category][key]=count
		
		DB_AppStats.setInMC(stats)
		
	@staticmethod
	def savesafe(stats,ns):
		if not stats:
			stats={}

		for category in ns:
			if type(ns[category])==list:
				if not stats.get(category):
					stats[category] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

				for idx, val in enumerate(ns[category]):
					if stats[category][idx] < ns[category][idx]:
						stats[category][idx]=ns[category][idx]
					elif stats[category][idx] > ns[category][idx]:
						stats[category][idx]+=ns[category][idx]
						ns[category][idx]=0

			elif type(ns[category])==dict:
				if not stats.get(category):
					stats[category] = {} 
				for key in ns[category]:
					if not stats[category].get(key):
						stats[category][key] = 0

					stats[category][key]+=ns[category][key]
					ns[category][key]=0		

		return (stats,ns)

class DB_AppLog(ndb.Model):
	auInfo = ndb.KeyProperty(DB_AppUser)
	version = ndb.IntegerProperty(default = 0)
	category = ndb.StringProperty(default="")
	text = ndb.StringProperty(default="")
	time = ndb.DateTimeProperty(auto_now_add=True)

	def toResult(self):
		_new = self.to_dict()

		if self.auInfo:
			_new['auid']=self.auInfo.id()
		_new['id']=self.key.id()
		_new['time']=time.mktime(self.time.timetuple())
		del _new['auInfo']
		return _new




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


class DB_AppNotice(ndb.Model):
	title=ndb.StringProperty(default="")
	category = ndb.StringProperty(default="")
	content = ndb.JsonProperty(default={})
	userdata = ndb.JsonProperty(default={})
	platform = ndb.StringProperty(default="")
	createTime = ndb.IntegerProperty(default=0)
	count = ndb.IntegerProperty(default=0)
	
	def toResult(self):
		_new = self.to_dict()
		_new['createtime']=_new['createTime']
		_new['id']=self.key.id()
		del _new['createTime']
		return _new

class DB_AppGiftcode(ndb.Model):
	code = ndb.StringProperty(default="")
	category = ndb.StringProperty(default="")
	value = ndb.IntegerProperty(default=0)
	user = ndb.KeyProperty()
	createTime = ndb.IntegerProperty()
	useTime = ndb.IntegerProperty(default=0)
	userdata = ndb.JsonProperty(default={})
	def toResult(self):
		_new = self.to_dict()
		_new['createtime']=_new['createTime']
		_new['usetime']=_new['useTime']
		_new['id']=self.key.id()
		if self.user: _new['user']=self.user.id()
		del _new['createTime']
		del _new['useTime']
		return _new

class DB_AppImage(ndb.Model):
	imageName = ndb.StringProperty(default="")
	developer = ndb.UserProperty()
	imgurl=""
	
class DB_AppStage(ndb.Model):
	stage = ndb.StringProperty(default="")
	category = ndb.StringProperty(default="")
	userdata = ndb.JsonProperty(default={})
	createTime = ndb.DateTimeProperty(auto_now_add=True)
	
	def toResult(self):
		_new = self.to_dict()
		_new['id']=self.key.id()
		_new['createtime']=time.mktime(self.createTime.timetuple())
		del _new['createTime']
		return _new

class DB_AppFeedback(ndb.Model):
	sender = ndb.KeyProperty(DB_AppUser)
	category = ndb.StringProperty(default="")
	content = ndb.StringProperty(default="")
	state = ndb.StringProperty(default="")
	mode = ndb.StringProperty(default="receive")
	userdata = ndb.JsonProperty(default = {})
	createTime = ndb.DateTimeProperty(auto_now_add=True)

	def toResult(self):
		_new = self.to_dict()
		_new['id']=self.key.id()
		_new['sender']=self.sender.id()
		_new['createtime']=time.mktime(self.createTime.timetuple())
		del _new['createTime']
		return _new
