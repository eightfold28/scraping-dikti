# -*- coding: utf-8 -*-
import scrapy
import csv
import urllib2
from  pymongo import  MongoClient

class ForlapDaftarDosenSpider(scrapy.Spider):
    name = 'forlap_daftar_dosen'
    # allowed_domains = ['https://forlap.ristekdikti.go.id/dosen']
    start_urls = ['https://forlap.ristekdikti.go.id/dosen']
    db_name = 'forlapdikti'
    db_collection_name = 'dosen'
    db_collection_post_req_name = 'post_req'
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[db_collection_name]
    collection_post_req = db[db_collection_post_req_name]

    def parse_list_dosen(self, response):
        list_dosen = response.xpath('//table/tr[@class="tmiddle"]/td[2]/a/@href').extract()
        for dosen_href in list_dosen:
            url_in_mongo = self.collection.find_one({ 'url': dosen_href })
            if url_in_mongo is None:
                self.collection.insert_one({ 'url': dosen_href })
                yield scrapy.Request(dosen_href, method='GET', callback=self.parse_page_dosen)

        next_button = response.xpath('//div[@class="pagination"]/ul/li[@class="active"]/following-sibling::li/a/@href').extract_first()
        if next_button is not None:
            yield response.follow(next_button, callback=self.parse_list_dosen, dont_filter=True)

    def strip_value(self, string):
        return string.strip() if string is not None else ''

    def parse_page_dosen(self, response):
        content_part = response.xpath('//div[@class="main"]/div[@class="row-fluid"]')
        image_url = self.strip_value(content_part.xpath('div[@class="span2"]/img/@src').extract_first())
        detail_part = content_part.xpath('div[@class="span10"]/table[@class="table1"]')
        nama_dosen = self.strip_value(detail_part.xpath('tr[1]/td[3]/text()').extract_first())
        perguruan_tinggi = self.strip_value(detail_part.xpath('tr[2]/td[3]/text()').extract_first())
        program_studi = self.strip_value(detail_part.xpath('tr[3]/td[3]/text()').extract_first())
        jenis_kelamin = self.strip_value(detail_part.xpath('tr[4]/td[3]/text()').extract_first())
        jabatan_fungsional = self.strip_value(detail_part.xpath('tr[5]/td[3]/text()').extract_first())
        pendidikan_tertinggi = self.strip_value(detail_part.xpath('tr[6]/td[3]/text()').extract_first())
        status_ikatan_kerja = self.strip_value(detail_part.xpath('tr[7]/td[3]/text()').extract_first())
        status_aktivitas = self.strip_value(detail_part.xpath('tr[8]/td[3]/text()').extract_first())
        riwayat_pendidikan = []
        arr_riwayat_pendidikan = response.xpath('//div[@id="riwayatpendidikan"]/table/tr[@class="tmiddle"]')
        for single_riwayat_pendidikan in arr_riwayat_pendidikan:
            rp = dict(
                no = self.strip_value(single_riwayat_pendidikan.xpath('td[1]/text()').extract_first()),
                perguruan_tinggi = self.strip_value(single_riwayat_pendidikan.xpath('td[2]/text()').extract_first()),
                gelar_akademik = self.strip_value(single_riwayat_pendidikan.xpath('td[3]/text()').extract_first()),
                tanggal_ijazah = self.strip_value(single_riwayat_pendidikan.xpath('td[4]/text()').extract_first()),
                jenjang = self.strip_value(single_riwayat_pendidikan.xpath('td[5]/text()').extract_first())
            )
            riwayat_pendidikan.append(rp)
        arr_penelitian = response.xpath('//div[@id="penelitian"]/table/tr[@class="tmiddle"]')
        penelitian = []
        for single_penelitian in arr_penelitian:
            p = dict(
                no = self.strip_value(single_penelitian.xpath('td[1]/text()').extract_first()),
                judul_penelitian = self.strip_value(single_penelitian.xpath('td[2]/text()').extract_first()),
                bidang_ilmu = self.strip_value(single_penelitian.xpath('td[3]/text()').extract_first()),
                lembaga = self.strip_value(single_penelitian.xpath('td[4]/text()').extract_first()),
                tahun = self.strip_value(single_penelitian.xpath('td[5]/text()').extract_first())
            )
            penelitian.append(p)
        arr_riwayat_mengajar = response.xpath('//div[@id="riwayatmengajar"]/table/tbody/tr[@class="tmiddle"]')
        riwayat_mengajar = []
        for single_riwayat_mengajar in arr_riwayat_mengajar:
            rw = dict(
                no = self.strip_value(single_riwayat_mengajar.xpath('td[1]/text()').extract_first()),
                semester = self.strip_value(single_riwayat_mengajar.xpath('td[2]/text()').extract_first()),
                kode_mata_kuliah = self.strip_value(single_riwayat_mengajar.xpath('td[3]/text()').extract_first()),
                nama_mata_kuliah = self.strip_value(single_riwayat_mengajar.xpath('td[4]/text()').extract_first()),
                kode_kelas = self.strip_value(single_riwayat_mengajar.xpath('td[5]/text()').extract_first()),
                perguruan_tinggi = self.strip_value(single_riwayat_mengajar.xpath('td[6]/text()').extract_first()),
            )
            riwayat_mengajar.append(rw)
        yield {
            'image_url': image_url,
            'nama_dosen': nama_dosen,
            'perguruan_tinggi': perguruan_tinggi,
            'program_studi': program_studi,
            'jenis_kelamin': jenis_kelamin,
            'jabatan_fungsional': jabatan_fungsional,
            'pendidikan_tertinggi': pendidikan_tertinggi,
            'status_ikatan_kerja': status_ikatan_kerja,
            'status_aktivitas': status_aktivitas,
            'riwayat_pendidikan': riwayat_pendidikan,
            'riwayat_mengajar': riwayat_mengajar,
            'penelitian': penelitian,
            'url': response.url
        }

    def parse(self, response):
        # cookies = response.request.headers.getlist('Cookie')
        with open('data_univ_id.csv', 'rb') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            searchDosenForm = response.xpath('//form[@id="searchDosenForm"]')
            captchas = searchDosenForm.xpath('//input[contains(@name, "captcha_value_")]/@value').extract()
            post_url = searchDosenForm.xpath('@action').extract_first()
            kode_pengaman = 0
            for captcha in captchas:
                kode_pengaman += int(captcha)
            for row in csv_reader:
                yield scrapy.http.FormRequest(post_url, 
                    formdata={
                        'kode_pengaman': str(kode_pengaman),
                        'dummy' : '',
                        'id_sp' : row['univ_id'],
                        'keyword': '',
                        'captcha_value_1': captchas[0],
                        'captcha_value_2': captchas[1] }, callback=self.parse_list_dosen, dont_filter=True)
        
           








