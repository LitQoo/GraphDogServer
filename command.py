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
def convert(input):
	if isinstance(input, dict):
	    return {convert(key): convert(value) for key, value in input.iteritems()}
	elif isinstance(input, list):
	    return [convert(element) for element in input]
	elif isinstance(input, unicode):
	    return input.encode('utf-8')
	else:
	    return input

class CommandHandler(SessionBaseHandler):
	def post(self):
		logging.info('########################### start command ###############################')

		logging.info(self.request.headers.get('accept_language'))

		path = self.request.path
		action = self.request.get('action').lower()
		aID = self.request.get('aID')
		logging.info('self.request')
		logging.info(self.request)
		logging.info('self.request.POST')
		logging.info(self.request.POST)
		token = self.request.get('token')
		version = self.request.get('version')
		param = CommandHandler.decParam(self.request.get('param'))
		auInfo={}
		aInfo={}
		gdNamespace = namespace_manager.get_namespace()
		appNamespace = 'APP_'+aID
		logging.info('param')
		logging.info(param)

		namespace_manager.set_namespace(appNamespace)
		if action == 'logout':
			self.session['auID']=''
			self.session['aID']=''
			self.printError('logout',100)

			logging.info('session auid:'+self.session.get('auID'))
			logging.info('session aid:'+self.session.get('aID'))
			return

		if not param:
			param={}


		namespace_manager.set_namespace(gdNamespace)
		#find app
		try:
			aInfo = DB_App.get_by_id(aID)
		except Exception, e:
			self.printError("dont find app1",100)
			return

		if not aInfo:
			self.printError('dont find app2' + aID,100)
			return
		
		#dec token
		tokens = CommandHandler.decToken(token,aInfo.secretKey)
		logging.info('tokens')
		logging.info(tokens)

		cTime = int(time.time())
				#기본리턴값
		result = {'action':action , 'callback': param.get('callback'), 'timestamp':int(cTime),'createTime':str(cTime), 'version':version}

		namespace_manager.set_namespace(appNamespace)
		#create dbclass
		#DB_AppUser =  _DB_AppUser.createClass(aID)
		#DB_AppScore = _DB_AppScore.createClass(aID)

		


		if self.session.get('auID'):
			#key =  ndb.Key(urlsafe=self.session.get('auID'))
			#auInfo = key.get()
			auInfo = DB_AppUser.get_by_id(int(self.session.get('auID')))
			logging.info('nick : ' + str(self.session.get('auID')))




		#/actionname/?param  && ?action=actionname&param 
		if not action:
		 	ga = path.split("/")
		 	if len(ga)>2:
		 		action = ga[2]

		#action 없으면 에러
		if not action:
			self.printError('dont find action',100)
			return
		

		# timestamp action
		if action == 'timestamp': ##########################################################################
			result['state']='ok'

		# getweek
		if action == 'getweek': ##########################################################################
			result['week']=int(datetime.date.today().strftime("%U"))
			localtime = time.localtime(time.time())
			weekday = int(datetime.date.today().strftime("%u"))
			if weekday==7:
				weekday = 0
			result['lefttime']=(7-weekday)*24*60*60 - localtime.tm_hour*60*60 -localtime.tm_min*60 - localtime.tm_sec
			result['state']='ok'

		# getweek
		if action == 'sessiontest': ##########################################################################
			number = 0
			if self.session.get('stest'):
				number = self.session.get('stest')

			number+=1

			self.session['stest']=number
			result['stest']=number
			
		#logging.info('aID in session : '+self.session.get('aID'))
		# start action

		
		if not self.session.get('aID') or self.session.get('aID')!=aID:	#login ##########################################################################
			logging.info('start authorise' + str(tokens.get('auID')))

			#auID있으면 au정보 뽑아오기~
			if tokens.get('auID'):
				try:
					logging.info('finded by auID : '+str(tokens['auID']))
					auInfo = DB_AppUser.get_by_id(tokens['auID'])
					#key =  ndb.Key(urlsafe=tokens['auID'])
					#auInfo = key.get()
				except Exception, e:
					pass
			

			#auID존재여부확인 , ctime check && uuid check  and appuser.createTime == tokens.get('createTime')
			if auInfo and auInfo.createTime == tokens.get('createTime') and auInfo.udid == tokens.get('udid'):	#and auInfo.udid == tokens.get('udid')
				logging.info("user finded")
				# name , flag update after check
				if tokens.get('nick') and tokens.get('flag') and auInfo.nick != tokens.get('nick') or auInfo.flag != tokens.get('flag'):
					#logging.info('chage the nick & flag key:'+str(auInfo.uInfo.key))
					
					namespace_manager.set_namespace(gdNamespace)
					uInfo=auInfo.uInfo.get()
					uInfo.nick = auInfo.nick = tokens.get('nick')
					uInfo.flag = auInfo.flag = tokens.get('flag')
					uInfo.put()
					namespace_manager.set_namespace(appNamespace)
				#createTime update
				
				auInfo.createTime=str(cTime)
				auInfo.put()

				#weekly pint update after check!##############################
				

			elif tokens.get('createTime')=='9999':	#join
				#find at user table by udid
				logging.info("user dont finded")
				uInfo = {}
				namespace_manager.set_namespace(gdNamespace)
				que = DB_User.query(DB_User.udid == tokens.get('udid'))
				find = que.fetch(limit=1)
				namespace_manager.set_namespace(appNamespace)
				if len(find)>0: #회원정보찾음
					logging.info("find uid by udid")
					uInfo = find[0]
					if not tokens.get('nick'):
						tokens['nick']=uInfo.nick
						tokens['flag']=uInfo.flag

					#check app installed in user info
					
					if aID in uInfo.installs:
						namespace_manager.set_namespace(appNamespace)
						q = DB_AppUser.query(DB_AppUser.uInfo == uInfo.key)
						for a in q.fetch(limit=1):
							logging.info("find auid in installs")
							auInfo = a


				else:	#don't find
					logging.info("dont find uid by udid")
					#join
					namespace_manager.set_namespace(gdNamespace)
					uInfo = DB_User();
					uInfo.nick = tokens.get('nick')
					uInfo.flag = tokens.get('flag')
					uInfo.udid = tokens.get('udid')
					uInfo.put()
					namespace_manager.set_namespace(appNamespace)
				
				if not auInfo: # if not app user , app join 
					logging.info("join appuser")
					auInfo = DB_AppUser()
					auInfo.nick = tokens.get('nick')
					auInfo.flag = tokens.get('flag')
					auInfo.udid = tokens.get('udid')
					auInfo.uInfo = uInfo.key
					auInfo.put()

					#update installs
					namespace_manager.set_namespace(gdNamespace)
					uInfo.installs.append(aID)
					uInfo.put()
					namespace_manager.set_namespace(appNamespace)
					result['isFirst']=True
					

					#cpiEvents check get
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
								namespace_manager.set_namespace(gdNamespace)
								del uInfo.CPIEvents[i]
								uInfo.put()
								namespace_manager.set_namespace(appNamespace)

								result['cpiEvent']=True
							i=i+1
			else :
				self.printError('authorise error',9999)
				logging.info(tokens.get('createTime'))
				return


			#return result
			result['tokenUpdate']='ok';
			result['state']='ok';
			result['auID']=str(auInfo.key.id())
			
			self.session['aID']=aID
			self.session['auID']=auInfo.key.id()
			logging.info('session update!! :'+aID+":"+str(auInfo.key.id()))
			logging.info('session auid:'+str(self.session.get('auID')))
			logging.info('session aid:'+str(self.session.get('aID')))
			logging.info('session cTime:'+str(cTime))
			auInfo.createTime=str(cTime)
			tokens['createTime']=str(cTime)
			auInfo.put()

			self.response.write(json.dumps(result))
			return

		#login check
		if not self.session.get('aID') or not self.session.get('auID'):
			self.printError('error',100)
			return

		#token check
		if tokens.get('createTime')!=auInfo.createTime:
			self.printError('token Error',9999)
			return

		#action startscores
		if action == 'getflagranks':#~ ##########################################################################
			scoresSortValue = aInfo.scoresSortValue
			startTime = int(cTime)/scoresSortValue*scoresSortValue
			gType = param.get('type')
			if not gType:
				gType = 'default'

			logging.info('startscores')
			#DB_AppScore.sTime==startTime
			_list = [];
			if gType=='all':
				_list = DB_AppScore.query().fetch(5)
			else:
				_list = DB_AppScore.query(DB_AppScore.gType==self.session.get('gType')).fetch(5)
			
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

			result['list']=items[:5]
			result['alluser']=alluser
			result['state']='ok'

		#action startscores
		if action == 'startscores':#~ ##########################################################################
			logging.info('startscores')
			sortValue=aInfo.scoresSortValue
		#param ->  type, score, userdata, 
			gType = param.get('type')
			if not gType:
				gType = 'default'

			
			startTime = int(cTime)/sortValue*sortValue


			asInfo = DB_AppScore()
			asInfo.sTime = startTime
			asInfo.uTime = int(cTime)
			asInfo.gType = gType
			asInfo.score =  random.randrange(10,500) #int(param.get('score'))
			asInfo.auInfo = auInfo.key
			asInfo.flag = tokens.get('flag')
			asInfo.nick = tokens.get('nick')
			asInfo.isOver = False
			asInfo.put()

			self.session['asSortTime'] = startTime
			self.session['asSortPrevTime'] = startTime-sortValue
			self.session['asID']=asInfo.key.id()
			self.session['gType']=str(gType)

			logging.info(namespace_manager.get_namespace())
			logging.info(str(self.session.get('asID')))
			logging.info(str(self.session.get('asSortTime')))
			logging.info(str(self.session.get('auID')))
			logging.info(str(self.session.get('aID')))
			logging.info(str(self.session.get('gType')))

			result['state']='ok'


		if action == 'getscores': ##########################################################################
			logging.info('test')
			logging.info(namespace_manager.get_namespace())
			logging.info(str(self.session.get('asID')))
			logging.info(str(self.session.get('asSortTime')))
			logging.info(str(self.session.get('auID')))
			logging.info(str(self.session.get('aID')))
			logging.info(str(self.session.get('gType')))

			asInfo =  ndb.Key('DB_AppScore',int(self.session.get('asID'))).get()
			asSortTime = self.session.get('asSortTime')
			asSortTimeList = [self.session.get('asSortTime'),self.session.get('asSortPrevTime')]
			gType = self.session.get('gType')
			if not asInfo:
				self.printError('dont find asid',100)
				return

			if param.get('score'):
				asInfo.score = int(param.get('score'))
			else:
				asInfo.score = 0
				
			asInfo.isOver = bool(param.get('isover'))

			if asInfo.isOver:
				asInfo.eTime = cTime
				logging.info(self.session.get('asID'))
				self.session['asSortID']=''
				self.session['asID']=''

				if param.get('userdata'):
					asInfo.userdata = param.get('userdata')

				findweeklydata = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.auInfo==auInfo.key,DB_AppWeeklyScore.gType==asInfo.gType)).fetch(1)
				weeklydata = {}
				nowweek = int(datetime.date.today().strftime("%U"))
				if findweeklydata:
					weeklydata = findweeklydata[0]
				else:
					weeklydata = DB_AppWeeklyScore(score=0, week=0, gType=asInfo.gType, auInfo=auInfo.key)

				if weeklydata.score<asInfo.score or weeklydata.week != nowweek:
					weeklydata.score = asInfo.score
					weeklydata.nick = asInfo.nick
					weeklydata.flag = asInfo.flag
					weeklydata.sTime = asInfo.uTime
					weeklydata.eTime = asInfo.eTime
					weeklydata.week = nowweek
					weeklydata.put()
					result['newweeklyscore']=True
					findmaxdata = DB_AppMaxScore.query(ndb.AND(DB_AppMaxScore.auInfo==auInfo.key,DB_AppMaxScore.gType==asInfo.gType)).fetch(1)
					maxdata = {}
					if findmaxdata:
						maxdata = findmaxdata[0]
					else:
						maxdata = DB_AppMaxScore(score=0,gType=asInfo.gType,auInfo=auInfo.key)

					if maxdata.score<asInfo.score:
						maxdata.score = asInfo.score
						maxdata.nick = asInfo.nick
						maxdata.flag = asInfo.flag
						maxdata.sTime = asInfo.uTime
						maxdata.eTime = asInfo.eTime
						maxdata.put()
						result['newmaxscore']=True

			asInfo.put()
			#future = asInfo.put_async()
			#tt = future.get_result()
			#logging.info('test value')
			#logging.info(tt)
			#start rank

			#testlist = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList)),DB_AppScore.gType==self.session.get('gType')).order(-DB_AppScore.score).fetch()
			#for aaa in testlist:
			#	logging.info("id:"+str(aaa.auInfo.id())+", score:"+str(aaa.score))


			#2. alluser
			result['alluser'] = DB_AppScore.query(DB_AppScore.sTime.IN(asSortTimeList)).count()
			#1. myrank
			result['myrank'] =  DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'),DB_AppScore.score>asInfo.score)).count()+1

			logging.info('myrank is')
			logging.info(result['myrank'])

			logging.info('myscore is')
			logging.info('info '+str(asInfo.score))

			#asInfo = future.get_result()
			checkme = False
			if result['myrank']<=10:
				scorelist = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList)),DB_AppScore.gType==self.session.get('gType')).order(-DB_AppScore.score).fetch(10)
				result['list']=[]
				rank=1
				for sinfo in scorelist:
					_new = sinfo.toResult()
					_new['rank']=rank

					if _new['asid']==asInfo.key.id():
						_new['isme']=True
						checkme=True

					result['list'].append(_new)
					rank=rank+1
			else:
				scorelist = DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'))).order(-DB_AppScore.score).fetch(3)
				scorelist += DB_AppScore.query(ndb.AND(DB_AppScore.sTime.IN(asSortTimeList),DB_AppScore.gType==self.session.get('gType'))).order(-DB_AppScore.score).fetch(offset=result.get('myrank')-5,limit=7)

				result['list']=[]
				rank=1

				for sinfo in scorelist:
					_new = sinfo.toResult()
					ofs=0
					if rank>3:
						ofs =result['myrank']-8

					_new['rank']=rank+ofs

					if _new['asid']==asInfo.key.id():
						_new['isme']=True
						checkme=True

					result['list'].append(_new)
					rank=rank+1

				
				


			if not checkme:
				logging.info('write!! new!!!')
				_new = asInfo.toResult()
				_new['rank']=result['myrank']
				_new['isme']=True

				if result.get('myrank')<=10:
					result['list'].insert(result.get('myrank')-1,_new)
					logging.info('insert to myrank'+str(result.get('myrank')-1))
				else:
					result['list'].insert(7,_new)
					logging.info('insert to 7')
				
				result['list'] = result['list'][:10]

			result['state']='ok'

		if action == 'getweeklyscores': ################################################################################
			gType = param.get('type')
			if not gType:
				gType = 'default'

			# find my info
			findweeklydata = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.auInfo==auInfo.key,DB_AppWeeklyScore.gType==gType)).fetch(1)
			weeklydata = {}
			nowweek = int(datetime.date.today().strftime("%U"))
			if findweeklydata:
				weeklydata = findweeklydata[0]
			else:
				weeklydata = DB_AppWeeklyScore(score=0, week=0, gType=asInfo.gType, auInfo=auInfo.key)

			#2. alluser
			result['alluser'] = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).count()
			#1. myrank
			result['myrank'] =  DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.score>weeklydata.score,DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).count()+1


			#asInfo = future.get_result()
			checkme = False
			if result['myrank']<=10:
				scorelist = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(10)
				result['list']=[]
				rank=1
				for sinfo in scorelist:
					_new = sinfo.toResult()
					_new['rank']=rank

					if _new['auid']==auInfo.key.id():
						_new['isme']=True
						checkme=True

					result['list'].append(_new)
					rank=rank+1
			else:
				scorelist = DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(3)
				scorelist += DB_AppWeeklyScore.query(ndb.AND(DB_AppWeeklyScore.gType==gType,DB_AppWeeklyScore.week == nowweek)).order(-DB_AppWeeklyScore.score).fetch(offset=result.get('myrank')-5,limit=7)

				result['list']=[]
				rank=1

				for sinfo in scorelist:
					_new = sinfo.toResult()
					ofs=0
					if rank>3:
						ofs =result['myrank']-8

					_new['rank']=rank+ofs

					if _new['auid']==auInfo.key.id():
						_new['isme']=True
						checkme=True

					result['list'].append(_new)
					rank=rank+1


		if action == 'getnotices': #######################################################################################
			# param - lastNoticeID, 
			#          limit = true, false
			lastNoticeID = param.get('lastNoticeID')
			limit = param.get('limit')
			if not limit:
				limit = 10
			if not lastNoticeID :
				lastNoticeID=0
			#DB_AppNotice.key.id>lastNoticeID
			noticeList = DB_AppNotice.query().order(-DB_AppNotice.key).fetch(limit)
			result['list']=[]
			for notice in noticeList:
				noticedict = {}
				noticedict['id']=notice.key.id()
				noticedict['title']=notice.title
				noticedict['content']=notice.content
				noticedict['userdata']=notice.userdata
				noticedict['platform']=notice.platform
				noticedict['createtime']=notice.createTime
				result['list'].append(noticedict)
			result['state']='ok'
		
		if action == 'getrequests': #######################################################################################
			limit = param.get('limit')
			if not limit:
				limit = 10
			rlist = DB_AppRequest.query(DB_AppRequest.receiver==auInfo.key).fetch(limit)
			result['list']=[]
			for request in rlist:
				requestDict = {}
				requestDict['id']=request.key.id()
				requestDict['category']=request.category
				requestDict['content']=request.content
				requestDict['userdata']=json.loads(request.userdata)
				result['list'].append(requestDict)
			result['state']='ok'

		if action == 'removerequest': #######################################################################################
			request = DB_AppRequest.get_by_id(int(self.session.get('id')))
			if request:
				request.delete()
			result['state']='ok'

		if action == 'getcpilist': #######################################################################################
			namespace_manager.set_namespace(gdNamespace)
			limit = self.request.get('limit')
			if not limit:
				limit = 10
			cpiList = DB_App.query(ndb.AND(DB_App.useCPI== True,DB_App.group==aInfo.group)).fetch(limit)
			result['list']=[]
			for cpi in cpiList:
				if cpi.key.id() == aID:
					continue
				cpidict = {}
				cpidict['id']=cpi.key.id()
				cpidict['title']=cpi.title
				cpidict['bannerimg']=cpi.bannerImg
				cpidict['iconimg']=cpi.iconImg

				store = json.loads(cpi.store)
				cpidict['store']=store.get(tokens.get('platform'))
				
				descripts = json.loads(cpi.descript)
				descript = descripts.get(tokens.get('lang'))
				if not descript:
					descript = descripts.get('default')

				cpidict['descript']=descript

				result['list'].append(cpidict)

			result['state']='ok'
			namespace_manager.set_namespace(appNamespace)
		
		if action == 'addcpievent': #######################################################################################
			namespace_manager.set_namespace(gdNamespace)
			cpiappid = param.get('aid')
			user = auInfo.uInfo.get()
			logging.info(user.CPIEvents)
			newCpiEvent={'eventAppID':cpiappid,'fromAppID':aID,'fromAppUserID':auInfo.key.id()}
			user.CPIEvents.append(newCpiEvent)
			user.put()
			result['state']='ok'
			namespace_manager.set_namespace(appNamespace)

		if action == 'usegiftcode':#######################################################################################
			
			if param.get('giftcode'):
				giftcode = DB_AppGiftcode.get_by_id(param.get('giftcode').upper())
				result['resultcode']=100
				
				if not giftcode:
					result['resultcode']=880
					result['resultmsg']="don't find giftcode"

				elif giftcode.user:
					result['resultcode']=890
					result['resultmsg']="this giftcode was used"

				elif self.session.get('giftcodeTime'):
					gifttime = cTime-int(self.session.get('giftcodeTime'));


			else:
				result['resultcode']=880
				result['resultmsg']="don't find giftcode"
				
				#if gifttime < 3600:
				#	result['resultcode']=870
				#	result['resultmsg']="you don't use giftcode for 1H"

			result['state']='ok'
			if result.get('resultcode')==100:
				result['category']=giftcode.category
				result['value']=giftcode.value
				giftcode.useTime = int(time.time())
				giftcode.user = auInfo.key
				giftcode.put()
				self.session['giftcodeTime']=int(time.time())

		if action == 'addmail':#######################################################################################
			namespace_manager.set_namespace(gdNamespace)
			uInfo =  auInfo.uInfo.get()
			uInfo.mail = param.get('mail')
			uInfo.put()
			namespace_manager.set_namespace(appNamespace)

			result['state']='ok'
			auInfo.mail = param.get('mail')
			auInfo.put()

		namespace_manager.set_namespace(appNamespace)
		#결과리턴
		#for key,value in result.iteritems():
		#	logging.info(str(type(value)))
		#	if(type(value) == unicode):
		#		logging.info('test')
		#		result[key] = value.encode('utf-8')
			 
		#result = convert(result)
		logging.info(result)
		resultStr = json.dumps(result,encoding="utf-8",ensure_ascii=False)
		#logging.info(resultStr)
		#resultStr = resultStr.encode('utf-8')
		self.response.write(resultStr)
		logging.info(resultStr)
		logging.info('########################### end command ###############################')
	


	def get(self):
		self.post()		

	@classmethod
	def decParam(cls,param):
		re={}
		try:
			re = base64.decodestring(param)
			#re = re.decode('utf-8')
			#logging.info('decParam type')
			#logging.info(str(type(to)))
			re = json.loads(re) #json.dumps
		except Exception, e:
			return re
		return re
	
	@classmethod
	def encParam(cls,paramstr):
		re = base64.encodestring(paramstr)
		re = re.decode('utf-8')
		return re

	@classmethod
	def decToken(cls,token,skey):
		re={}
		try:
			token=token.replace(" ","+")
			to = base64.decodestring(token)
			#to = to.decode('uft-8')
			#logging.info('decToken type')
			#logging.info(str(type(to)))
			if len(token)%8>0:
				token = token + ' '*(8-len(token)%8)			

			if len(skey)%8>0:
				skey = skey + ' '*(8-len(skey)%8)

			obj = DES.new(skey,DES.MODE_ECB)
			to=obj.decrypt(to)
			#to=to.decode('utf-8')
			to=to.split("||")
			
			if to[0]:
				re['auID']=int(to[0])
			else:
				re['auID']=0

			re['udid']=to[1]
			re['flag']=to[2]
			re['lang']=to[3]
			re['nick']=to[4]
			re['email']=to[5]
			re['platform']=to[6]
			re['createTime']=to[7]
		except Exception, e:
		 	return re
		return re
	
	@classmethod
	def encToken(cls,auID,udid,flag,lang,nick,email,platform,createTime,skey):
		token = str(auID)+'||'+str(udid)+'||'+str(flag)+'||'+str(lang)+'||'+str(nick)+'||'+str(email)+'||'+str(platform)+'||'+str(createTime)+'||'
		
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