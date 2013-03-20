
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
	store = ndb.JsonProperty()


class DB_User(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	udid = ndb.StringProperty()
	installs = ndb.StringProperty(repeated=True)
	mail = ndb.StringProperty()
	CPIEvents = ndb.PickleProperty(default = [])

class DB_AppUser(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	mail = ndb.StringProperty()
	uInfo  = ndb.KeyProperty(DB_User)
	createTime = ndb.StringProperty()
	udid = ndb.StringProperty()
	userData = ndb.JsonProperty()
	joinDate = ndb.DateProperty(auto_now=True)

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
	userData = ndb.JsonProperty()

class DB_AppNotice(ndb.Model):
	title=ndb.StringProperty()
	content = ndb.TextProperty()
	userData = ndb.JsonProperty()
	platform = ndb.StringProperty()
	createTime = ndb.IntegerProperty()

class DB_AppRequest(ndb.Model):
	receiver = ndb.KeyProperty()
	sender = ndb.KeyProperty()
	category = ndb.StringProperty()
	content = ndb.StringProperty()
	userData = ndb.JsonProperty()

class DB_AppGiftcode(ndb.Model):
	code = ndb.StringProperty()
	category = ndb.StringProperty()
	value = ndb.IntegerProperty()
	user = ndb.KeyProperty()
	createTime = ndb.IntegerProperty()
	useTime = ndb.IntegerProperty()


class DB_AppData(ndb.Model):
	pass

