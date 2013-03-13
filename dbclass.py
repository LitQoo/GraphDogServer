
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
	title = ndb.StringProperty()
	secretKey = ndb.StringProperty()
	#scoresSortType = ndb.StringProperty()
	scoresSortValue = ndb.IntegerProperty()
	developer = ndb.KeyProperty()
	useCPI = ndb.BooleanProperty()

class DB_User(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	udid = ndb.StringProperty()
	installs = ndb.StringProperty(repeated=True)

class DB_AppUser(ndb.Model):
	nick = ndb.StringProperty()
	flag = ndb.StringProperty()
	uInfo  = ndb.KeyProperty(DB_User)
	createTime = ndb.StringProperty()
	udid = ndb.StringProperty()
	userData = ndb.JsonProperty()

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
	parent = ndb.KeyProperty()
	lang = ndb.StringProperty()
	title=ndb.StringProperty()
	text = ndb.TextProperty()
	userData = ndb.JsonProperty()



class DB_AppData(ndb.Model):
	pass

