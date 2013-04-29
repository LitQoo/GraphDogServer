
# -*- coding: utf-8 -*-
#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import rdbms
import time
import json
import logging
from google.appengine.api import memcache
import datetime

CLOUDSQL_INSTANCE = 'graphdogserver:graphdog'
CLOUDSQL_CONNECTION = None

def sqlConnect(aid=None,dbname=None,instance=None):
	global CLOUDSQL_CONNECTION
	global CLOUDSQL_INSTANCE
	logging.info('connect sql')

	if aid:
		dbname = 'APP_'+aid
	if not instance:
		instance = CLOUDSQL_INSTANCE

	if not CLOUDSQL_CONNECTION:
		CLOUDSQL_CONNECTION=rdbms.connect(instance=instance, database=dbname, charset='utf8')
		if CLOUDSQL_CONNECTION:
			logging.info('connect sql ok')
		else:
			logging.info('connect sql failed')

	return CLOUDSQL_CONNECTION

def sqlClose():
	global CLOUDSQL_CONNECTION
	logging.info('close sql')
	if CLOUDSQL_CONNECTION:
		CLOUDSQL_CONNECTION.close()
		CLOUDSQL_CONNECTION=None
		logging.info('close ok')

def createDatabaseAndConnect(aid=None,dbname=None):
		conn =sqlConnect(dbname='graphdog')
		cursor = conn.cursor()

		if aid:
			dbname = 'APP_'+aid

		query = """create database %s charset utf8;"""%dbname
		cursor.execute(query)
		createQuery = conn.commit()
		logging.info(createQuery)
		
		sqlClose()

		return sqlConnect(dbname=dbname)





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
		logging.info(createQuery)

	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppScore WHERE no=%s' % findID
		cursor.execute(query)
		row = cursor.fetchone()
		return DB_AppScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = 'SELECT no, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppScore WHERE no=%s' % findID
		cursor.execute(query)
		row = cursor.fetchone()
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

			cursor.execute('SELECT LAST_INSERT_ID() FROM AppScore')
			row = cursor.fetchone()
			logging.info(row)
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
		logging.info(createQuery)

	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,amsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppMaxScore WHERE amsid='%s'" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		return DB_AppMaxScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,amsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata FROM AppMaxScore WHERE amsid='%s'" % findID
		cursor.execute(query)
		row = cursor.fetchone()
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

			cursor.execute('SELECT LAST_INSERT_ID() FROM AppMaxScore')
			row = cursor.fetchone()
			logging.info(row)
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
		logging.info(createQuery)

	@staticmethod
	def get(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,awsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week FROM AppWeeklyScore WHERE awsid='%s'" % findID
		cursor.execute(query)
		row = cursor.fetchone()
		return DB_AppWeeklyScores.set(row)

	@staticmethod
	def get_or_insert(findID=None):
		conn = sqlConnect()
		cursor = conn.cursor()
		query = "SELECT no,awsid, auInfo, nick, flag, sTime, uTime, eTime, gType, score, userdata, week FROM AppWeeklyScore WHERE awsid='%s'" % findID
		cursor.execute(query)
		row = cursor.fetchone()
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

			cursor.execute('SELECT LAST_INSERT_ID() FROM AppWeeklyScore')
			row = cursor.fetchone()
			logging.info(row)
			if row:
				self.no=row[0]

		else:
			conn = sqlConnect()
			cursor = conn.cursor()
			self.uTime = int(time.time())
			logging.info(self.to_dict())
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
	dbInstance= ndb.StringProperty(default=CLOUDSQL_INSTANCE)
	isPutOn = False

	def putOn(self):
		logging.info('putOn')
		self.isPutOn = True

	def doPut(self):
		logging.info('doPut')
		if self.isPutOn==True:
			logging.info('doPut complete')
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
	isPutOn = False

	def putOn(self):
		logging.info('putOn')
		self.isPutOn = True

	def doPut(self):
		logging.info('doPut')
		if self.isPutOn==True:
			logging.info('doPut complete')
			self.put()



class DB_AppVersions(ndb.Model):
	version = ndb.IntegerProperty(default=0)
	platform = ndb.StringProperty(default="")
	createTime = ndb.DateTimeProperty(auto_now_add=True)
	comment = ndb.StringProperty(default="")

class DB_AppStats(ndb.Model):
	category = ndb.StringProperty(default="")
	year = ndb.IntegerProperty()
	month = ndb.IntegerProperty()
	day = ndb.IntegerProperty()
	statsData = ndb.JsonProperty(default={})

	@staticmethod
	def getInMC():
		today = datetime.date.today().strftime("%Y%m%d")
		data = memcache.get("stats")		
		when = memcache.get("stats_when")
		if not when:
			when = today

		if not data:
			data = {'hit':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'install':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'update':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'country':{'en':0,'kr':0},'platform':{'ios':0,'android':0}}

		if today != when:
			#데이터저장 when꺼를들고오기~~
			stats = DB_AppStats.get_or_insert("stats_"+when)
			stats.year = int(when[0:3])
			stats.month = int(when[4:5])
			stats.day = int(when[6:7])
			stats.statsData = data
			stats.put()
			#새값생성
			newdata={'hit':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'install':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'update':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],'country':{'en':0,'kr':0},'platform':{'ios':0,'android':0}}
			DB_AppStats.setInMC(newdata)
			return newdata

		return data

	@staticmethod
	def setInMC(data):
		today = datetime.date.today().strftime("%Y%m%d")
		memcache.set("stats",data,60*60*24*2)
		memcache.set("stats_when",today,60*60*24*2)

class DB_AppLog(ndb.Model):
	auInfo = ndb.KeyProperty(DB_AppUser)
	category = ndb.StringProperty()
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
	title=ndb.StringProperty(default="")
	category = ndb.StringProperty(default="")
	content = ndb.JsonProperty(default={})
	userdata = ndb.JsonProperty(default={})
	platform = ndb.StringProperty(default="")
	createTime = ndb.IntegerProperty(default=0)
	count = ndb.IntegerProperty(default=0)

class DB_AppRequest(ndb.Model):
	receiver = ndb.KeyProperty()
	sender = ndb.KeyProperty()
	category = ndb.StringProperty(default="")
	content = ndb.StringProperty(default="")
	userdata = ndb.JsonProperty(default={})

class DB_AppGiftcode(ndb.Model):
	code = ndb.StringProperty(default="")
	category = ndb.StringProperty(default="")
	value = ndb.IntegerProperty(default=0)
	user = ndb.KeyProperty()
	createTime = ndb.IntegerProperty()
	useTime = ndb.IntegerProperty(default=0)
	userdata = ndb.JsonProperty(default={})

class DB_AppImage(ndb.Model):
	imageName = ndb.StringProperty(default="")
	developer = ndb.UserProperty()
	imgurl=""
	
class DB_AppData(ndb.Model):
	pass

