# -*- coding: utf-8 -*-
import scrapy


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.lk']

    def start_requests(self):
        start_urls = ['http://books.lk/home.php?cat=1&objects_per_page=20']
        #start_urls = ['http://books.lk/home.php?cat=119']
        #start_urls = ['http://books.lk/product.php?productid=2365']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_and_extract_book_urls)

    def parse_and_extract_book_urls(self, response):

        book_links = response.css('div.disc-con a::attr(href)').extract()
        #book_names = response.css('div.disc-con p::text').extract()

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

        #shape summary
        res = response.css('div.iview-contblock p').extract()

        summary_str = ""

        if len(res) > 1:
            x = res[1].split(">")
            y = []

            for i in range (1, len(x), 1):
                y.append(x[i].split("<"))

            for i in y:
                summary_str = summary_str + i[0].replace(';', ':').replace('\r', '').replace('\n', '').replace('\t', '').replace(u'\x96', '-').encode('utf-8')


        yield{
            'Book Title':str(response.css('div.page-head h2::text').extract_first()).replace(';', ':').replace('\r', '').replace('\n', '').replace('\t', ''),
            'Author': additional_details_dict['Author'],
            'Summary': summary_str,
            'Publisher': additional_details_dict['Publisher'],
            'Published Date': additional_details_dict['Published Date'],
            'ISBN-10': additional_details_dict['ISBN-10'],
            'ISBN-13': additional_details_dict['ISBN-13'],
            'Binding': additional_details_dict['Binding'],
            'Product Dimensions': additional_details_dict['Product Dimensions'],
            'Pages': additional_details_dict['Pages'],
            'Price': 'Rs. '+ str(response.css('span.currency span::text').extract_first()).replace('\r', '').replace('\n', '').replace('\t', '')
        }
		






















