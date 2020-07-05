from flask import Flask, render_template, url_for,request,redirect,jsonify
from bs4 import BeautifulSoup
import requests
import sqlite3


app = Flask(__name__)
srch_url = "https://www.amazon.in/s?k="
ref = "&ref=nb_sb_noss"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}



# DB for search result
conn = sqlite3.connect('test.db')
c = conn.cursor()

with conn:
	c.execute('''CREATE TABLE IF NOT EXISTS PRODUCT
				(ID INT PRIMARY KEY NOT NULL,
				 NAME TEXT NOT NULL,
				 PRICE TEXT NOT NULL);''')


@app.route('/')
def my_home():
	return render_template('index.html')

@app.route('/<string:page_name>')
def about(page_name):
	return render_template(page_name)

def search_api(data):
	if data > ' ':
		bstr = data.replace(" ","+")
		f_url = srch_url+str(bstr)+ref
		page = requests.get(f_url,headers=headers)
		src  = page.content
		soup =BeautifulSoup(src, 'lxml')
		srch_result = []
		prc_list = []
		srch_cnt = 1
		conn = sqlite3.connect('test.db')
		for prc_tag in soup.find_all("span",{"class":"a-price-whole"}):
			if prc_tag.text !='0':
				prc = str(prc_tag.text).replace(',','')
				prc_list.append(prc)

		for h2_tag in soup.find_all("h2"):
			a_tag = h2_tag.find("a")
			if a_tag != None and srch_cnt <=20 and 'primevideo' not in a_tag.attrs['href'] :
				srch_result.append({'Title':a_tag.text,'Price':prc_list[srch_cnt-1],'Link':a_tag.attrs['href']})
				conn = sqlite3.connect('test.db')
				c = conn.cursor()
				with conn:
					c.execute("INSERT OR IGNORE INTO PRODUCT (ID,NAME,PRICE) \
						VALUES (:id,:name,:price)" ,{'id':srch_cnt,'name':a_tag.text,'price':prc_list[srch_cnt-1]})
					conn.commit()
				srch_cnt+=1
		return srch_result
	else:
		return "Error: No name provided. Please specify a book name"


@app.route('/search',methods=['POST','GET'])
def submit_form():
	if request.method == 'POST':
		try:
			#Clear data before loading
			conn = sqlite3.connect('test.db')
			c = conn.cursor()
			with conn:
				c.execute("DELETE FROM PRODUCT WHERE ID > 0")
				conn.commit()
			data = request.form.get("search-text")
			srch_result = search_api(data)
			return render_template('search_result.html',data=srch_result)
		except:
			return 'Sorry not able to search '
	else:
		return 'something went wrong try again!!'

@app.route('/order', methods=['GET'])
def api_name():
	query_parms = request.args
	orderid = int(query_parms.get('id'))
	if orderid >= 0:
		bname = []
		conn = sqlite3.connect('test.db')
		c = conn.cursor()
		with conn:
			c.execute("SELECT NAME,PRICE FROM PRODUCT WHERE ID = :id",{'id':orderid+1})
			rows = c.fetchall()
			for row in rows:
				bname.append({'Title':row[0],'Price':row[1]})	
		return render_template('product_summ.html',data=bname)

@app.route('/placeorder',methods=['POST','GET'])
def order():
	if request.method == 'POST':
		try:
			return 'Your Order has been placed successfully!'
		except:
			return 'Sorry not able to place order '
	else:
		return 'something went wrong try again!!'
    
if __name__ == '__main__':
	app.run(debug=True)