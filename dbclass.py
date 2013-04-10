
# -*- coding: utf-8 -*-
#!/usr/bin/env python
from google.appengine.ext import ndb
#############################################################################
# database class
#############################################################################
class UniqueConstraintViolation(Exception):
    def __init__(self, scope, value):
        super(UniqueConstraintViolation, self).__init__("Value '%s' is not unique within scope '%s'." % (value, scope, ))

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
	descript = ndb.JsonProperty(default={"defalut":"descript"})
	cpiReward = ndb.JsonProperty(default={"defalut":100})

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
	lastNID = ndb.KeyProperty()
	requests = ndb.JsonProperty(default = [])

class DB_AppLog(ndb.Model):
	auInfo = ndb.KeyProperty(DB_AppUser)
	text = ndb.StringProperty()
	time = ndb.DateTimeProperty(auto_now_add=True)

class DB_AppScore(ndb.Model):
	auInfo=ndb.KeyProperty(DB_AppUser)
	nick=ndb.StringProperty()
	flag=ndb.StringProperty()
	sTime=ndb.IntegerProperty()
	uTime=ndb.IntegerProperty() 
	eTime=ndb.IntegerProperty() 
	gType=ndb.StringProperty()
	score=ndb.IntegerProperty()
	isOver=ndb.BooleanProperty()
	userdata = ndb.JsonProperty()

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
	userdata = ndb.JsonProperty()
	
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
	userdata = ndb.JsonProperty()

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
	userdata = ndb.JsonProperty()

class DB_AppGiftcode(ndb.Model):
	code = ndb.StringProperty()
	category = ndb.StringProperty()
	value = ndb.IntegerProperty()
	user = ndb.KeyProperty()
	createTime = ndb.IntegerProperty()
	useTime = ndb.IntegerProperty()

class DB_AppImage(ndb.Model):
	imageName = ndb.StringProperty()
	developer = ndb.UserProperty()
	imgurl=""
	
class DB_AppData(ndb.Model):
	pass

