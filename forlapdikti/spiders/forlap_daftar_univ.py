# -*- coding: utf-8 -*-
import scrapy
import logging

class ForlapDaftarUnivSpider(scrapy.Spider):
    name = 'forlap_daftar_univ'
    # allowed_domains = ['https://forlap.ristekdikti.go.id/perguruantinggi/search']
    start_urls = ['https://forlap.ristekdikti.go.id/perguruantinggi']
    total_dosen = 0

    def parse(self, response):
    	# cookies = response.request.headers.getlist('Cookie')
    	searchPTForm = response.xpath('//form[@id="searchPtForm"]')
    	captchas = searchPTForm.xpath('//input[contains(@name, "captcha_value_")]/@value').extract()
    	post_url = searchPTForm.xpath('@action').extract_first()
    	kode_pengaman = 0
    	for captcha in captchas:
    		kode_pengaman += int(captcha)
    	yield scrapy.http.FormRequest(post_url, 
    		formdata={
    			'kode_pengaman': str(kode_pengaman),
    			'id_will' : '',
    			'kode_koordinasi': '86942CDF-44F1-446E-8E9E-CB37BBBB16E6',
    			'id_bp' : '',
    			'stat_sp': '',
    			'keyword': '',
    			'searchfullpt': '',
    			'captcha_value_1': str(captchas[0]),
    			'captcha_value_2': str(captchas[1])
    		},
    		callback=self.parse_list_universitas)

    def parse_list_universitas(self, response):
    	# universitas = response.meta['universitas'] || []
    	univ_col = response.xpath('//table/tr[@class="ttop"]')
    	universitas_s = univ_col.xpath('td[3]/a/text()').extract()
    	dosen_s = univ_col.xpath('td[7]/text()').extract()
    	index = -1
    	# universitas.extend(universitas_s)
    	for univ in universitas_s:
    		index += 1
    		jumlah_dosen = int(dosen_s[index].replace('.',''))
    		self.total_dosen += jumlah_dosen
    		yield {
    			'univ_name': univ,
    			'jumlah_dosen': str(jumlah_dosen)
    		}

    	next_button = response.xpath('//div[@class="pagination"]/ul/li[@class="active"]/following-sibling::li/a/@href').extract_first()
    	print(next_button)
    	if next_button is not None:
    		yield response.follow(next_button, callback=self.parse_list_universitas)
    	else:
    		logging.info("TOTAL JUMLAH DOSEN : " + str(self.total_dosen))