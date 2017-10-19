import numpy as np
import requests
import bs4
from collections import OrderedDict
from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from df2gspread import df2gspread as d2g
from df2gspread import gspread2df as g2d
from PIL import Image
from firebase import firebase
import pyrebase
import glob
import datetime
# ==============return event heading=================#


def heading(soup):
	heading = soup.find(class_="_5gmx")
	print(("Event data fectched: " + heading.string))
	head1 = str(heading.string)
	return str(head1)


# ==========return event start date =================#

def date(soup):
	date = soup.find('span', class_="_5a4z")
	date1 = date.string
	return str(date1)


# ==========return event image url =================#

def ur_l(soup):
	tags = soup.findAll('img', class_="scaledImageFitWidth img")
	Url_1 = "\n".join(set(tag['src'] for tag in tags))
	tags = soup.findAll('img', class_="scaledImageFitHeight img")
	Url_2 = "\n".join(set(tag['src'] for tag in tags))
	if Url_1:
		return str(Url_1)
	else:
		return str(Url_2)


# ======================return event details=====================#

def Event_Details(data):
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		Event_Details = more_soup.findAll('div', {'class': '_2qgs'})
		if Event_Details:
			Event = Event_Details[0].text
	return Event


# =======================return event location===============#

def Location(data):
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		Location = more_soup.findAll('a', {'class': '_5xhk'})
		if Location:
			Locate = str(Location[0].text)
	return Locate


# ============= return event More Info || Timming || Ticket Link ============= #

def Tick_Time_Info(data):
	mainData = []
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		wanted_text = more_soup.findAll('div', {'class': '_5xhp fsm fwn fcg'})
		if wanted_text:

			mainData.append(str(wanted_text[1].text))
			mainData.append(wanted_text[0].text)
			try:
				mainData.append(wanted_text[2].text)

			except IndexError:
				mainData.append('nan')
	return mainData


# ======================return start date endate======================#
def Date(data):
	dat = []
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		Timming = more_soup.findAll("span", {'itemprop': "startDate"})
		if Timming:
			try:
				dat.append(str(Timming[1].text))
			except IndexError:
				dat.append(str(Timming[0].text))
			try:
				dat.append(str(Timming[0].text))
			except IndexError:
				dat.append(np.nan)
	return dat


# ==========================return year============================#
def year(data):
	y = []
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		Timming = more_soup.findAll("div", {'class': "_publicProdFeedInfo__timeRowTitle _5xhk"})
		if Timming:
			y.append(Timming[0])
	return y


# =====================return start and end time===================================#
def Timming(data):
	da = []
	for item in data:
		commentedHTML = item.find('code').contents[0]
		more_soup = bs4.BeautifulSoup(commentedHTML, 'lxml')
		Timming = more_soup.findAll("span")
		if Timming:
			try:
				da.append((Timming[2].text))
			except IndexError:
				da.append("NAN")
			try:
				da.append((Timming[3].text))
			except IndexError:
				da.append("NAN")
	return da


# =================================return time in seconds==========================#
def startseconds(stdatetime):
	import time
	dt_obj = time.strptime(str(stdatetime), "%d %B %Y %H:%M")
	print(dt_obj)
	timestamp = time.mktime(dt_obj)
	print((repr(timestamp)))
	return timestamp


def endseconds(endatetime):
	import time
	try:
		dt_obj = time.strptime(str(endatetime), "%d %B %Y %H:%M")
		timestamp = time.mktime(dt_obj)
	except ValueError:
		timestamp = np.nan
	print((repr(timestamp)))
	return timestamp


# ================Getting Latitude and longitude================================#


def Lat_long(Locate, moreinfo):
	try:
		address = str(Locate + moreinfo)
		response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address= ' + address)
		resp_json_payload = response.json()
		Latlong = list((resp_json_payload['results'][0]['geometry']['location']).values())
	except IndexError:
		pass
	try:
		address = str(moreinfo)
		response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address= ' + address)
		resp_json_payload = response.json()
		Latlong = list((resp_json_payload['results'][0]['geometry']['location']).values())
	except IndexError:
		try:
			address = str(Locate)
			response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address= ' + address)
			resp_json_payload = response.json()
			Latlong = list((resp_json_payload['results'][0]['geometry']['location']).values())
		except IndexError:
			Latlong = "nan"

	return Latlong

#=============================download excel spreadsheet sheet1 in pandas dataframe=====================#

def excel_sheet():
	spreadsheet = '1Wne9gj7CIgEtNJgcvuEgL1EMxqQRZ9UEfSJMp0hqKic'
	wks_name = 'Sheet1'
	df = g2d.download(spreadsheet, wks_name, col_names=True, row_names=True)      
	return df

#=============================download excel spreadsheet sheet1 in pandas dataframe=====================#	
def urld():
	spreadsheet = '1Wne9gj7CIgEtNJgcvuEgL1EMxqQRZ9UEfSJMp0hqKic'
	wks_name = 'Sheet2'
	df = g2d.download(spreadsheet, wks_name, col_names=True, row_names=True)      
	return df


#======================================merge images and upload to firebase and get url ============#


def firebase_url():
	import glob
	import shutil
	import os
	import time
	path = ('/root/Desktop/Civew_Infotech/image_merge/images/')
	config = {
	"apiKey": "AIzaQWERTYUIOPs65yzzMRdDI621eEEDgpU",
	"authDomain": "QWERTYUIOP-621eEED.firebaseapp.com",
	"databaseURL": "https://QWERTYUIOP.firebaseio.com",
	"storageBucket": "QWERTYUIOP-621eEED.appspot.com",
	}
	firebase = pyrebase.initialize_app(config)
	st = firebase.storage()
	a = 0
	image_merge_url = []
	c = 0 
	for filename in sorted(glob.glob('/root/Desktop/Civew_Infotech/image_merge/images/*.png'),key=os.path.getmtime):
		millis = int(round(time.time() * 1000))
		urlfilename = str(millis) + '.png'
   
		st.child(str(urlfilename)).put(str(filename))
		b = st.child(str(urlfilename)).get_url("null")
		print (b)
		image_merge_url.append(b)
		a = (a+1)
#===================removing all images from directory after uploading to cloud ==========#  
	files = glob.glob('/root/Desktop/Civew_Infotech/image_merge/images/*.png')
	for f in files:
		os.remove(f)	
	print("all images in directory removed successfully")	
   # shutil.rmtree('/root/Desktop/Civew_Infotech/image_merge/images/*.png')	
	return image_merge_url	



# =============Getting Urls From A text File ========#

def main(request):


	df = urld()
	urls = df['Url'].tolist()	
	A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y = ([] for i in range(25))
	fetch = []
	for url in urls:	
		print (url)
		headers = {"Accept-Language": "en-US,en;q=0.5"}
		page = requests.get(url, headers=headers)
		soup = bs4.BeautifulSoup(page.text, 'lxml')
		data = soup.findAll("div", {'class': "hidden_elem"})

		# =====================Appending Data To List=============#
		S.append(url)

		head1 = heading(soup)
		A.append(head1)

		date1 = date(soup)

		Url1 = ur_l(soup)
		C.append(Url1)

		Event = Event_Details(data)
		D.append(Event)

		Locate = Location(data)
		E.append(Locate)

		mainData = Tick_Time_Info(data)
		F.append(mainData[0])
		H.append(mainData[2])
		da = Timming(data)
		time = da[0]

		global entime1

		if (len(time) < 6):
			starttime = time
			J.append(starttime)
			endtime = str(da[1]).strip("UTC+05:30")
			if (len(endtime) < 3):
				en = str(starttime).rstrip(' \t\r\n\0')
				start_datetime = datetime.datetime.strptime(en, '%H:%M')
				start_datetime = start_datetime + datetime.timedelta(hours=3)
				x, y = str(start_datetime).split(" ")
				entime1 = y[:5]
				K.append(entime1)
			else:
				K.append(endtime)	

		elif (len(time) < 17):
			starttime = time.strip("UTC+05:30")
			J.append(starttime)
			endtime = str(da[1]).strip("UTC+05:30")
			if (len(endtime) < 3):
				en = str(starttime).rstrip(' \t\r\n\0')
				start_datetime = datetime.datetime.strptime(en, '%H:%M')
				start_datetime = start_datetime + datetime.timedelta(hours=3)
				x, y = str(start_datetime).split(" ")
				entime1 = y[:5]
				K.append(entime1)
			else:
				K.append(endtime)
		else:
			time = time.strip("UTC+05:30")
			starttime, endtime = time.split('to')
			starttime = starttime[-6:]
			endtime = endtime[-6:]
			J.append(starttime)	
			if (len(endtime) < 3):					
				en = str(starttime).rstrip(' \t\r\n\0')
				start_datetime = datetime.datetime.strptime(en, '%H:%M')
				start_datetime = start_datetime + datetime.timedelta(hours=3)
				x, y = str(start_datetime).split(" ")
				entime1 = y[:5]
				K.append(entime1)					
			else:
				K.append(endtime)		
		#	print(entime)	

		#print (len(endtime))
		#print(entime)

		# ============================year============================
		y = year(data)
		yea = str(y[0])
		a, b = yea.split('content="')
		yr = str(b[:4])
		# =================================getting year=======================================#


		dat = Date(data)
		stdate = str(dat[0] + " " + yr)
		G.append(stdate)
		endate = str(dat[0] + " " + yr)
		
		B.append(endate)

		# ========================str time || end time to seconds===================#

		stdatetime = (str(stdate) + " " + str(starttime)).rstrip(' \t\r\n\0')
		startsec = startseconds(stdatetime)
		P.append(startsec)

		endatetime = (str(endate) + " " + str(entime1)).rstrip(' \t\r\n\0')
		print(("strdatetime" + endatetime))
		endsec = endseconds(endatetime)
		Q.append(endsec)
		# ==============================append email and contact number=======================#
		R.append("Civew_Infotech@Civew_Infotech.in")
		L.append("9**********1")
		M.append("others")
		O.append("nan")
		N.append("nan")
		T.append("nan") 
		U.append("nan") 
		V.append("nan") 
		W.append("100")
		X.append("0")
		Y.append("nan")
		# =================================================append Latitude and Longitude=================================#
		moreinfo = mainData[0]
		Latlong = Lat_long(Locate, moreinfo)
		a1 = str(Latlong).strip("[]")
		a1 = a1.replace(',', 'X')
		a1 = a1.replace(" ", "")
		I.append(a1)
		# ================================================ print uploaded events heading on httpresponse===================#
		fetch.append(head1)
		fetch.append('<br/>')
		#count +=1	

		# ======================Converting Data To Data Frames Using Pandas==================#
	my_dictionary = OrderedDict()
	my_dictionary['URL'] = S
	my_dictionary['Title'] = A
	my_dictionary['StartDate'] = B
	my_dictionary['EndDate'] = G
	my_dictionary['StartTime'] = J
	my_dictionary['EndTime'] = K
	my_dictionary['Start_Seconds'] = P
	my_dictionary['End_Seconds'] = Q
	my_dictionary['Location'] = E
	my_dictionary['Latitude_Longitude'] = I
	my_dictionary['More_info'] = F
	my_dictionary['Image_Url'] = C        
	my_dictionary['Email'] = R
	my_dictionary['Mobile_Number'] = L
	my_dictionary['Categories'] = M       
	my_dictionary['KeyWords'] = O
	my_dictionary['Tickets'] = H
	my_dictionary['ticket_name'] = T
	my_dictionary['ticket_price'] = U
	my_dictionary['ticket_old_price'] = V 
	my_dictionary['ticket_quantity'] = W 
	my_dictionary['ticket_capping'] = X  
	my_dictionary['ticket_description'] = Y 
	my_dictionary['Event_Details'] = D

	df = pd.DataFrame(my_dictionary)

	# ============ Spreadsheet Id & Sheet Name ==================#

	spreadsheet = '1Wne9gj--sheet id here---qQRZ9UEfSJMp0hqKic'
	wks_name = 'Sheet1'

	# =============upload data to spreadsheet===================#
	d2g.upload(df, spreadsheet, wks_name)
	#=====================empty urls ========================#
	wks_name2 = 'Sheet2'
	df_ = pd.DataFrame(index= range(0,2),columns=['Url'])
	d2g.upload(df_, spreadsheet, wks_name2)
	return HttpResponse(fetch)


def excel_spreadsheet(request):
	df = excel_sheet()
	dd = df.to_html()   

	# ========================== None and Empty Cells Checking In Dataframe==============================#
	event = str((~df.Event_Details.str.contains(r' ')).sum())
	Image_Url = str((df.Image_Url.str.contains(r' ')).sum())
	Location = str(((~df.Location.str.contains(r' ')).sum()) - 1)
	More_info = str((~df.More_info.str.contains(r' ')).sum())
	StartDate = str((~df.StartDate.str.contains(r' ')).sum())
	Tickets = str((df.Tickets.str.contains(r'nan')).sum())
	EndTime = str((df.EndTime.str.contains(r' ')).sum())
	Title = str((~df.Title.str.contains(r' ')).sum())
	EndDate = str((~df.EndDate.str.contains(r' ')).sum())
	StartTime = str((df.StartTime.str.contains(r' ')).sum())
	Start_Seconds = str((df.Start_Seconds.str.contains(r' ')).sum())
	End_Seconds = str((df.End_Seconds.str.contains(r'nan')).sum())
	Latitude_Longitude = str((df.Latitude_Longitude.str.contains(r'nan')).sum())
	Email = str((df.Email.str.contains(r' ')).sum())
	Mobile_Number = str((df.Mobile_Number.str.contains(r' ')).sum())
	Categories = str((df.Categories.str.contains(r' ')).sum())
	Ticket_Types = str((df.ticket_name.str.contains(r'nan')).sum())
	ticket_price = str((df.ticket_name.str.contains(r'nan')).sum())
	ticket_old_price = str((df.ticket_name.str.contains(r'nan')).sum())
	ticket_description = str((df.ticket_name.str.contains(r'nan')).sum())
	KeyWords = str((df.KeyWords.str.contains(r'nan')).sum())
	print ("=============starts====================")
	#print (pd.isnull(df['KeyWords']))
	print (df.count(axis=0))
	print ("==============ends====================")

	print((df.astype(bool).sum(axis=0).tolist()))
	print((df.isnull().sum(axis=1)))
	print((len(df)))
	cg = ( "No. Of Blank Cells:" "</br> " + "Title: " + "<b>" + Title + "</b>" + "StartDate: " + StartDate + 
	"EndDate: " + EndDate + "StartTime: " + StartTime + "EndTime: " + EndTime + "Start_Seconds: " + Start_Seconds + 
	"End_Seconds: " + End_Seconds + "Location: " + Location + "Latitude_Longitude: " + Latitude_Longitude + "More_info: " +
	 More_info + "Image_Url: " + Image_Url + "Tickets: " + Tickets + "Email: " + Email + "Mobile_Number: " + Mobile_Number + 
	 "Categories: " + Categories + "\nTicket_Types: \n" + Ticket_Types + "ticket_price" + ticket_price + "ticket_old_price"+
	 ticket_old_price+"ticket_description"+ticket_description+"KeyWords: " + KeyWords + "Event_Details: " + event )
	
	de = cg + '<br/>' + dd
	return render(request, 'layout1.html', {'df': de})



def upload(request):
	df = excel_sheet()
	url_list = []
	df1 = df['Image_Url']    
	print (df1) 
	a = 0
	for url in df1:
		r = requests.get(url, stream=True)
		r.raw.decode_content = True       
		background = Image.open("a.png").convert("RGBA")
		x, y = background.size
		print(x)
		print(y)
		background_width  = 570
		background_height = 295
		background = background.resize((background_width, background_height), Image.ANTIALIAS) 
		foreground = Image.open(r.raw).convert("RGBA")
		width, height = foreground.size
		print("foregrund/n:"+ str(width)+str(height))
		if (width > height and width < 570):
			height =  (height * 570)/width
			height = 280
			width = background_width
			foreground = foreground.resize((int(width), int(height)), Image.ANTIALIAS)
			xx = (570 - width)/2
			yy = (295 - height )/2
			print("x"+str(x)+"y:"+str(y))
			print("x"+str(width)+"y:"+str(height))
			background.paste(foreground, (int(xx), int(yy)), foreground)
			background.show()
			background.save('/root/Desktop/Civew_Infotech/image_merge/images/'+str(a)+".png","PNG")
			a = (a+1)
		elif (width > height):
			height =  (height * 570)/width
			width = background_width
			foreground = foreground.resize((int(width), int(height)), Image.ANTIALIAS)

			xx = (570 - width)/2
			yy = (295 - height )/2
			print("x"+str(x)+"y:"+str(y))
			print("x"+str(width)+"y:"+str(height))
			background.paste(foreground, (int(xx), int(yy)), foreground)
			background.show()
			background.save('/root/Desktop/Civew_Infotech/image_merge/images/'+str(a)+".png","PNG")
			a = (a+1)
		else :
			width = (width * 295)/height
			height = background_height
			foreground = foreground.resize((int(width), int(height)), Image.ANTIALIAS)
			xx = (570 - width)/2
			yy = (295 - height )/2
			print("x"+str(x)+"y:"+str(y))
			print("x"+str(width)+"y:"+str(height))
			background.paste(foreground, (int(xx), int(yy)), foreground)
			background.show()
			background.save('/root/Desktop/Civew_Infotech/image_merge/images/'+str(a)+".png","PNG")
			a = (a +1)

	image_merge_url = firebase_url()
	print (image_merge_url)			        
	df['Image_Url'] = image_merge_url
	print (df['Image_Url'])

 #==========================upload url updated dataframe to spreadsheet==========================#

	spreadsheet = '1Wne9gj7CIgEt___Sheet ID here___xqQRZ9UEfSJMp0hqKic'
	wks_name = 'Sheet1'
	d2g.upload(df, spreadsheet, wks_name)
	return HttpResponse("merged successfully")        
		
def database_push(request):
	import time
	import collections

	df = excel_sheet()
	print (len(df))
	config = {
	"apiKey": "AIzaQWERTYUIOPs65yzzMRdDI621eEEDgpU",
	"authDomain": "QWERTYUIOP-621eEED.firebaseapp.com",
	"databaseURL": "https://QWERTYUIOP.firebaseio.com",
	"storageBucket": "QWERTYUIOP-621eEED.appspot.com",
	}
	vendor_id = '10110269'
	firebase = pyrebase.initialize_app(config)
	database = firebase.database()
	event_ids = database.child('vendor').child(vendor_id).shallow().child('events').get().val()
	#od = collections.OrderedDict(sorted(event_ids.keys()))
	lis=[]
	for item in event_ids:
		f, l = item.split('_')		
		lis.append(l)
	lists = sorted(lis, key=int)
	event_id =  (int(lists[-1]) + 1)	
	
	print(event_id)


	b = 0
	c = len(df)
	while b< c:
		df = excel_sheet()
		df.rename(columns={'Title': 'name', 'Start_Seconds': 'start_time', 'End_Seconds':'end_time','Location':'venue_name',
		 'Latitude_Longitude':'venue','Image_Url':'image','Email':'email','Mobile_Number':'mobile','KeyWords':'keyword',
		 'Categories':'category', 'Event_Details':'description'}, inplace=True)
		df = df.iloc[[b]]
		tktInfo = df[['ticket_name', 'ticket_price', 'ticket_quantity','ticket_capping','ticket_description',
		'ticket_old_price' ]].copy()
		tktInfo = tktInfo.to_dict(orient='records')
		tktId = int(round(time.time() * 1000))
		newEventId = str(vendor_id)+"_"+str(event_id)
		data = df[['keyword', 'category', 'image', 'end_time', 'start_time', 'name', 'email', 'mobile', 'venue_name', 
		'venue',  'description']].copy()
		data['event_id']= newEventId
		data['status']='pending'
		data['page_views']='0'
		print("====================dataframe starts here============================")
		#print(data)
		data = data.to_dict(orient='records')

		dataV = df[['category', 'image', 'end_time', 'start_time', 'name']].copy()
		dataV['event_id']= newEventId
		dataV = dataV.to_dict(orient='records')
		print(newEventId)
		#print (dataV)
		print("it ends=======================================")
		#print (data)
		firebase = pyrebase.initialize_app(config)
		database = firebase.database()


		database.child('event').child(newEventId).child('details').set(data[0])


		database.child('vendor').child(vendor_id).child('events').child(newEventId).set(dataV[0])
		
		database.child('event').child(newEventId).child('details').child('ticket_category').child(tktId).set(tktInfo[0])		

		event_id +=1
		b +=1
	return HttpResponse("datapushed successfully")


