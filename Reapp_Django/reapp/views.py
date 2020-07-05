from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
from .models import Search,Product
import requests
import re



# Create your views here.
def index(request):
	return render(request, 'reapp/index.html')

# Search results
@csrf_exempt
def search(request):
	search_text = request.POST['search-text']
	output = 'Searching '+search_text
	# Clear data from databases
	Product.objects.all().delete()
	Search.objects.all().delete()
	search_api(search_text)
	result_list = Search.objects.all()
	context = {'result_list':result_list}
	return render(request, 'reapp/search_result.html',context)


# Search functionality
def search_api(data):
	srch_url = "https://www.amazon.in/s?k="
	ref = "&ref=nb_sb_noss2"
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
	if data > ' ':
		bstr = data.replace(" ","+")
		f_url = srch_url+str(bstr)+ref
		page = requests.get(f_url,headers=headers)
		src  = page.text
		soup =BeautifulSoup(src, 'html.parser')
		srch_result = []
		prc_list = []
		prc = ''
		srch_cnt = 1
		
		for grid_tag in soup.find_all("div",class_="sg-row"):
			#Image capture
			img_tag = grid_tag.find("img")
			if img_tag !=None:
				img = img_tag.attrs['src']
			
			#Price capture
			div_tag = grid_tag.find("div",class_ ="a-section a-spacing-none a-spacing-top-small")
			if div_tag !=None:
				prc_tag = div_tag.find("span",class_="a-price-whole")
				if prc_tag != None:
					prc = prc_tag.text
					prc = prc.replace(',','')
					prc = prc.replace('.','')

			#Title capture
			h2_tag = grid_tag.find('h2')
			if h2_tag !=None:
				a_tag  = h2_tag.find('a') 
				if a_tag != None and srch_cnt <=20 and 'primevideo' not in a_tag.attrs['href'] and prc!= '':
					if srch_cnt >= 2:
						if a_tag.text not in srch_result[srch_cnt-2]['Title']:
							s = Search(name = a_tag.text,price=int(prc),image_link=img)
							s.save()
							srch_result.append({'Title':a_tag.text,'Price':prc,'Image':img})
							srch_cnt+=1
					else:
						s = Search(name = a_tag.text,price=int(prc),image_link=img)
						s.save()
						srch_result.append({'Title':a_tag.text,'Price':prc,'Image':img})
						srch_cnt+=1
	else:
		return HttpResponse("Error: No name provided. Please specify a book name")

