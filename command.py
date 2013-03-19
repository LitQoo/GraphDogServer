# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import webapp2
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
#from google.appengine.api import rdbms
#from google.appengine.ext import db
from google.appengine.ext import ndb
from webapp2_extras import sessions
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from google.appengine.api import users
from google.appengine.api import namespace_manager
import json
import datetime
import time
import base64
import sys
import logging
import random
from dbclass import *
from SessionBaseHandler import *

class CommandHandler(SessionBaseHandler):
	def post(self):

		logging.info('########################### start command ###############################')

		logging.info(self.request.headers.get('accept_language'))

		path = self.request.path
		action = self.request.get('action')
		aID = self.request.get('aID')
		token = self.request.get('token')
		param = CommandHandler.decParam(self.request.get('param'))
		auInfo={}
		aInfo={}
		gdNamespace = namespace_manager.get_namespace()
		appNamespace = 'APP_'+aID
			
		if action == 'logout':
			self.session['auID']=''
			self.session['aID']=''
			self.printError('logout',100)
			return

		if not param:
			param={}

		#find app
		try:
			aInfo = DB_App.get_by_id(aID)
		except Exception, e:
			self.printError('dont find app' + aID,100)
			return

		#create dbclass
		#DB_AppUser =  _DB_AppUser.createClass(aID)
		#DB_AppScore = _DB_AppScore.createClass(aID)

		namespace_manager.set_namespace(appNamespace)

		if self.session.get('auID'):
			#key =  ndb.Key(urlsafe=self.session.get('auID'))
			#auInfo = key.get()
			auInfo = DB_AppUser.get_by_id(int(self.session.get('auID')))
			logging.info('nick : ' + str(self.session.get('auID')))


		#dec token
		tokens = CommandHandler.decToken(token,aInfo.secretKey)
		logging.info('tokens : ' + str(tokens))
		cTime = int(time.time())

		#/actionname/?param  && ?action=actionname&param 형식모두지원하기
		if not action:
		 	ga = path.split("/")
		 	if len(ga)>2:
		 		action = ga[2]

		#action 없으면 에러
		if not action:
			self.printError('dont find action',100)
			return
		
		#기본리턴값
		result = {'action':action , 'callback': param.get('callback'), 'createTime':str(cTime)}

		# timestamp action
		if action == 'timestamp': ##########################################################################
			result['timestamp'] = int(cTime)
			result['state']='ok'

		# getweek
		if action == 'getweek': ##########################################################################
			result['week']=int(datetime.date.today().strftime("%U"))
			result['lefttime']=int(2400)
			

		# start action
		if action == 'start':	#로그인하기 ##########################################################################
			#auID있으면 au정보 뽑아오기~
			if tokens.get('auID'):
				try:
					logging.info('finded by auID : '+tokens['auID'])
					auInfo = DB_AppUser.get_by_id(tokens['auID'])
					#key =  ndb.Key(urlsafe=tokens['auID'])
					#auInfo = key.get()
				except Exception, e:
					pass
			

			#auID존재여부확인 , ctime check && uuid check  and appuser.createTime == tokens.get('createTime')
			if auInfo:	#and auInfo.udid == tokens.get('udid')
				logging.info("user finded")
				# name , flag 확인해서 업데이트하기
				if tokens.get('nick') and tokens.get('flag') and auInfo.nick != tokens.get('nick') or auInfo.flag != tokens.get('flag'):
					#logging.info('chage the nick & flag key:'+str(auInfo.uInfo.key))
					
					namespace_manager.set_namespace(gdNamespace)
					uInfo=auInfo.uInfo.get()
					uInfo.nick = auInfo.nick = tokens.get('nick')
					uInfo.flag = auInfo.flag = tokens.get('flag')
					uInfo.put()

				#createTime update
					namespace_manager.set_namespace(appNamespace)
					auInfo.createTime=str(cTime)
					auInfo.put()

				#weekly점수 검사후 초기화!##############################
				

			else:	#join 하기
				#udid로 회원테이블뒤지기
				logging.info("user dont finded")
				uInfo = {}
				namespace_manager.set_namespace(gdNamespace)
				que = DB_User.query(DB_User.udid == tokens.get('udid'))
				find = que.fetch(limit=1)
				
				if len(find)>0: #회원정보찾음
					logging.info("find uid by udid")
					uInfo = find[0]
					if not tokens.get('nick'):
						tokens['nick']=uInfo.nick
						tokens['flag']=uInfo.flag

					#회원정보에서 앱설치한적있는가 찾아보자
					
					if aID in uInfo.installs:
						namespace_manager.set_namespace(appNamespace)
						q = DB_AppUser.query(DB_AppUser.uInfo == uInfo.key)
						for a in q.fetch(limit=1):
							logging.info("find auid in installs")
							auInfo = a


				else:	#못찾음
					logging.info("dont find uid by udid")
					#전체회원가입
					namespace_manager.set_namespace(gdNamespace)
					uInfo = DB_User();
					uInfo.nick = tokens.get('nick')
					uInfo.flag = tokens.get('flag')
					uInfo.udid = tokens.get('udid')
					uInfo.put()

				
				if not auInfo: #앱정보없으면 앱회원가입
					logging.info("join appuser")
					namespace_manager.set_namespace(appNamespace)
					auInfo = DB_AppUser()
					auInfo.nick = tokens.get('nick')
					auInfo.flag = tokens.get('flag')
					auInfo.udid = tokens.get('udid')
					auInfo.uInfo = uInfo.key
					auInfo.put()

					#인스톨즈 업데이트
					namespace_manager.set_namespace(gdNamespace)
					
					
					uInfo.installs.append(aID)
					uInfo.put()

					result['isFirst']=True
					

					#cpiEvents체크
					if len(uInfo.CPIEvents)>0:
						logging.info('check cpievent')
						i=0
						for cpi in uInfo.CPIEvents:
							if aID == cpi.get('eventAppID'):
								logging.info('find cpi Event')
								namespace_manager.set_namespace('APP_'+cpi.get('fromAppID'))
								newRequest = DB_AppRequest()
								newRequest.receiver = ndb.Key('DB_AppUser',int(cpi.get('fromAppUserID')))
								newRequest.sender = aInfo.key
								newRequest.category = 'cpiEvent'
								newRequest.content = 'complete cpiEvent'
								newRequest.put()

								del uInfo.CPIEvents[i]
								uInfo.put()

								result['cpiEvent']=True
							i=i+1


			#결과리턴~
			result['tokenUpdate']='ok';
			result['state']='ok';
			result['nick']=tokens.get('nick')
			result['flag']=tokens.get('flag')
			result['auid']=auInfo.key.id()
			self.session['aID']=aID
			self.session['auID']=auInfo.key.id()
			
			#nextaction
			if param.get('nextAction'):
				action = param.get('nextAction')
				param = param.get('nextParam')

		#login 검사
		if not self.session.get('aID') or not self.session.get('auID'):
			self.printError('error',100)

		#action startscores
		if action == 'getflagranks':#점수시작~ ##########################################################################
			namespace_manager.set_namespace(appNamespace)
			scoresSortValue = aInfo.scoresSortValue
			startTime = int(cTime)/scoresSortValue*scoresSortValue
			result['leftTime'] = int(cTime)-startTime
			logging.info('startscores')
			#DB_AppScore.sTime==startTime
			_list = DB_AppScore.query().fetch()
			alluser=0;
			flags={}
			for _as in _list:
				if not flags.get(_as.flag):
					flags[_as.flag]={'user':int(1),'score':int(_as.score),'flag':_as.flag}
				else:
					_cnt = int(flags.get(_as.flag).get('user'))+1
					_scr = int(flags.get(_as.flag).get('score'))+_as.score
					flags[_as.flag]={'score':_scr,'user':_cnt,'flag':_as.flag}

				alluser=alluser+1

			#flags=sorted(flags, key=flags.__getitem__,flags.__getitem__, reverse=True)

			items = [v for k, v in flags.items()]
			items=sorted(items, key=lambda x: x['score'],cmp=lambda x,y: y-x) 
			result['flags']=items
			result['alluser']=alluser
			

		#action startscores
		if action == 'startscores':#점수시작~ ##########################################################################
			logging.info('startscores')
		#param ->  type, score, userdata, 
			gType = param.get('type')
			if not gType:
				gType = 'defalut'

			r = random.randrange(0,5)
			flags = ['kr','cn','jp','us','ru','kp']
			auInfo.flag = flags[r]
			
			startTime = int(cTime)/aInfo.scoresSortValue*aInfo.scoresSortValue

			namespace_manager.set_namespace(appNamespace)


			asInfo = DB_AppScore()
			asInfo.sTime = startTime
			asInfo.gType = gType
			asInfo.score =  random.randrange(10,500) #int(param.get('score'))
			asInfo.auInfo = auInfo.key
			asInfo.flag = auInfo.flag
			asInfo.nick = auInfo.nick
			asInfo.isOver = False
			asInfo.put()


			self.session['asSortTime'] = startTime
			self.session['asSortPrevTime'] = startTime-aInfo.scoresSortValue
			self.session['asID']=asInfo.key.id()
			self.session['gType']=str(gType)

			result['state']='ok'


		if action == 'getscores': ##########################################################################
			
			namespace_manager.set_namespace(appNamespace)
			asInfo =  ndb.Key('DB_AppScore',id=int(self.session.get('asID'))).get()
			asSortTime = self.session.get('asSortTime')
			asSortTimeList = [self.session.get('asSortTime'),self.session.get('asSortPrevTime')]
			if not asInfo:
				self.printError('dont find asid',100)
				return

			if param.get('score'):
				asInfo.score = int(param.get('score'))
			
			asInfo.isOver = bool(param.get('isOver'))
			if asInfo.isOver:
				asInfo.eTime = cTime
				self.session['asSortID']=''
				self.session['asID']=''
				################ weekly, legned, 24h 등록

			asInfo.put()
			#순위뽑기 시작~


			#2. 전체유저수뽑기
			result['alluser'] = DB_AppScore.query(DB_AppScore.sTime.IN(asSortTimeList)).count()
			#1. 내등수뽑기
			result['myrank'] =  DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'),DB_AppScore.score>asInfo.score)).count()+1

			logging.info('info '+str(asInfo.score))
			if result['myrank']<=10:
				scorelist = DB_AppScore.query(DB_AppScore.sTime.IN(asSortTimeList)).order(-DB_AppScore.score).fetch(10)
				result['list']=[]
				rank=1
				for sinfo in scorelist:
					_new = sinfo.to_dict()
					_new['rank']=rank
					del _new['auInfo']
					result['list'].append(_new)
					rank=rank+1
			else:
				scorelist1 = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'))).order(-DB_AppScore.score).fetch(3)
				scorelist2 = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'))).order(-DB_AppScore.score).fetch(offset=result.get('myrank')-5,limit=7)
				result['list']=[]
				rank=1
				for sinfo in scorelist1:
					_new = sinfo.to_dict()
					_new['rank']=rank
					del _new['auInfo']
					result['list'].append(_new)
					rank=rank+1

				rank = result['myrank']-4
				for sinfo in scorelist2:
					_new = sinfo.to_dict()
					_new['rank']=rank
					del _new['auInfo']
					result['list'].append(_new)
					rank=rank+1

		if action == 'getnotices':
			namespace_manager.set_namespace(appNamespace)
			# param - lastNoticeID, 
			#          limit = true, false
			lastNoticeID = param.get('lastNoticeID')
			limit = param.get('limit')
			if not lastNoticeID :
				lastNoticeID=0
			#DB_AppNotice.key.id>lastNoticeID
			noticeList = DB_AppNotice.query().order(-DB_AppNotice.key).fetch(limit)
			result['noticeList']=[]
			for notice in noticeList:
				noticedict = {}
				noticedict['id']=notice.key.id()
				noticedict['title']=notice.title
				noticedict['content']=notice.content
				noticedict['userData']=notice.userData
				noticedict['platform']=notice.platform
				noticedict['createTime']=notice.createTime
				result['noticeList'].append(noticedict)

		if action == 'getcpilist':
			namespace_manager.set_namespace(gdNamespace)
			cpiList = DB_App.query(DB_App.useCPI == True).fetch(10)
			result['cpiList']=[]
			for cpi in cpiList:
				if cpi.key.id() == aID:
					continue

				cpidict = {}
				cpidict['title']=cpi.title
				cpidict['bannerImg']=cpi.bannerImg
				cpidict['iconImg']=cpi.iconImg
				cpidict['store']=cpi.store
				result['cpiList'].append(cpidict)

			result['state']='ok'
			
		if action == 'addcpievent':
			namespace_manager.set_namespace(gdNamespace)
			cpiappid = param.get('aID')
			user = auInfo.uInfo.get()
			logging.info(user.CPIEvents)
			newCpiEvent={'eventAppID':cpiappid,'fromAppID':aID,'fromAppUserID':auInfo.key.id()}
			user.CPIEvents.append(newCpiEvent)
			user.put()
			result['state']='ok'

		#결과리턴
		self.response.write(json.dumps(result))
		
		logging.info('########################### end command ###############################')
		
	def get(self):
		self.post()

	@classmethod
	def decParam(cls,param):
		re={}
		try:
			re = base64.decodestring(param)
			re = json.loads(re) #json.dumps
		except Exception, e:
			return re
		return re
	
	@classmethod
	def encParam(cls,paramstr):
		re = base64.encodestring(paramstr)
		return re

	@classmethod
	def decToken(cls,token,skey):
		re={}
		try:
			logging.info('skey2:'+skey+'  len:'+str(len(skey)))
			token=token.replace(" ","+")
			to = base64.decodestring(token)
			
			if len(token)%8>0:
				token = token + ' '*(8-len(token)%8)			

			if len(skey)%8>0:
				skey = skey + ' '*(8-len(skey)%8)

			obj = DES.new(skey,DES.MODE_ECB)
			to=obj.decrypt(to)
			logging.info(to)
			re['auID']=to[0]
			re['udid']=to[1]
			re['flag']=to[2]
			re['nick']=to[3]
			re['email']=to[4]
			re['platform']=to[5]
			re['createTime']=to[6]
		except Exception, e:
		 	return re
		return re
	
	@classmethod
	def encToken(cls,auID,udid,flag,nick,email,platform,createTime,skey):
		token = str(auID)+'||'+str(udid)+'||'+str(flag)+'||'+str(nick)+'||'+str(email)+'||'+str(platform)+'||'+str(createTime)+'||'
		
		if len(token)%8>0:
			token = token + ' '*(8-len(token)%8)			

		if len(skey)%8>0:
			skey = skey + ' '*(8-len(skey)%8)
		
		obj = DES.new(skey,DES.MODE_ECB)
		token = obj.encrypt(token)
		token = base64.encodestring(token)
		return token

	def printError(self,msg,code):
		re = {'state':'error', 'msg':msg, 'errorcode':code}
		self.response.write(json.dumps(re))

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'hsgraphdogsessionsk',
}

app = webapp2.WSGIApplication([
	('/command', CommandHandler),
	('/command/.*', CommandHandler)
],
config=config,
debug=True)


