# -*- coding: utf-8 -*-
#!/usr/bin/env python
import webapp2
from webapp2_extras import sessions
from google.appengine.ext import ndb

#############################################################################
# session
#############################################################################
class SessionBaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the datastore.
        return self.session_store.get_session(name='sessiondb',backend='datastore')

class Address(ndb.Model):
	int1 = ndb.IntegerProperty()
	int2 = ndb.IntegerProperty()

class testModel(ndb.Model):
	str1 = ndb.StringProperty()
	str2 = ndb.StringProperty()
	int1 = ndb.IntegerProperty()
	geo1 = ndb.GeoPtProperty()
	stu1 = ndb.StructuredProperty(Address, repeated=True)

class TestHandler(SessionBaseHandler):
	def get(self):
		logging.info('test')
		abc =  DB_App(namespace='my_apps_table')
		abc.aID = 'aID'
		abc.title='title'
		abc.secretKey='kkkk'
		abc.put()
		# i=0
		# while True:
		# 	new = testModel()
		# 	new.str1 = 'newStr'+str(i)
		# 	new.str2 = 'newStr2' + str(i)
		# 	new.int1 = random.randrange(1,100)
		# 	new.int2 = random.randrange(1,100)
		# 	new.json1 = json.dumps({'int1':new.int1,'int2':new.int2})
		# 	new.pic1 = {'int1':new.int1,'int2':new.int2}
		# 	new.geo1 = ndb.GeoPt(random.randrange(1,90),random.randrange(1,90))
		# 	new.stu1 = [Address(int1=random.randrange(1,90),int2=random.randrange(1,90))]
		# 	new.put()
		# 	if i>10:
		# 		break;
		# 	i=i+1
		
		# query = testModel.query(testModel.int1>30).order(-testModel.int1).order(-testModel.int2)
		# for new in query:
		# 	logging.info(new.to_dict())
