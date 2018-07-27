# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup as bs

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.lk']

    def start_requests(self):
        start_urls = [
            'http://books.lk/home.php?cat=760',     #Sinahala
            'http://books.lk/home.php?cat=770',     #English
            'http://books.lk/home.php?cat=761'      #Tamil
        ]

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_and_extract_category_urls)    


    def parse_and_extract_category_urls(self, response):

        #check for products or categories are available
        bookcat_top = response.css('div.bookcat-top').extract()

        if len(bookcat_top) == 0:
            return

        #get sub categories
        subcat_main = bs(response.css('div.subcat-main').extract_first())
        subcat_blocks = subcat_main.find_all('span')        #keeps all the sub categories

        if len(subcat_blocks) > 0:
            subcat_urls = [('http://books.lk/'+i.a['href']) for i in subcat_blocks]

            for url in subcat_urls:
                yield scrapy.Request(url=url, callback=self.parse_and_extract_category_urls)

        else:
            yield scrapy.Request(url=(response.url + '&objects_per_page=20'), callback=self.parse_and_extract_book_urls)


    def parse_and_extract_book_urls(self, response):

        book_links = response.css('div.disc-con a::attr(href)').extract()

        book_urls = []

        for link in book_links:
            new_link_arr = link.split('&')
            book_urls.append('http://books.lk/' + new_link_arr[0])

        for url in book_urls:
            yield scrapy.Request(url=url, callback=self.parse)

        next_page_url = str(response.css('a.right-arrow::attr(href)').extract_first())
        split_url = next_page_url.split('&')
        next_page_url = 'http://books.lk/' + split_url[0] + '&objects_per_page=20&' + split_url[-1]

        yield scrapy.Request(url=next_page_url, callback=self.parse_and_extract_book_urls)


    def parse(self, response):

        additional_details_arr = response.css('div.table-block table td::text').extract()
        additional_details_dict = {}
        headings_arr = ['Author', 'Publisher', 'Published Date', 'ISBN-10', 'ISBN-13', 'Binding', 'Product Dimensions', 'Pages']

        for i in range(0, len(additional_details_arr), 2):
            additional_details_dict[additional_details_arr[i]] = additional_details_arr[i+1].replace(';', ':').replace('\r', '').replace('\n', '').replace('\t', '')

        for i in range(0, len(headings_arr), 1):
            if headings_arr[i] not in additional_details_dict:
                additional_details_dict[headings_arr[i]] = '-'

        summary_str = bs(response.css('div.iview-contblock')[3].extract()).get_text()
        summary_str.encode('utf-8').replace('\xc3\xa2\xe2\x82\xac', '').replace('\xe2\x84\xa2', '\'').replace('\xc2\xa2 ', ' *').replace('\xe2\x80\x9d', ' ').replace('\xc3\x83\xe2\x80\xb0g\xc3\x83\xe2\x80\xb0', '').replace('\xc3\x83\xe2\x80\xb0', 'e').replace(';', ':').replace('\r', '').replace('\n', '').replace('\t', '').replace('\x96', '-')

        nav_bar = bs(response.css('div.beadcrumb')[0].extract()).get_text().replace('\n\n\n', '*').replace('\n\n', '*').replace('\n', '*').split('*')
        language = nav_bar[2]
        product_type = (nav_bar[3])
        genre = nav_bar[-3]


        yield{
            'Product Title':str(response.css('div.page-head h2::text').extract_first().encode('utf-8')).replace(';', ':').replace('\r', '').replace('\n', '').replace('\t', ''),
            'Author': additional_details_dict['Author'],
            'Summary': summary_str,
            'Publisher': additional_details_dict['Publisher'],
            'Published Date': additional_details_dict['Published Date'],
            'ISBN-10': additional_details_dict['ISBN-10'],
            'ISBN-13': additional_details_dict['ISBN-13'],
            'Binding': additional_details_dict['Binding'],
            'Product Dimensions': additional_details_dict['Product Dimensions'],
            'Pages': additional_details_dict['Pages'],
            'Price': 'Rs. '+ str(response.css('span.currency span::text').extract_first()).replace('\r', '').replace('\n', '').replace('\t', ''),
            'Language': language,
            'Product Type': product_type,
            'Genre': genre
        }
		
