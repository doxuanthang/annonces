# -*- coding:utf-8 -*-

import scrapy
import re
from annonces.items import AnnoncesProductItem

class AnnoncesSpider(scrapy.Spider):
    name = "annonces"

    start_urls = ["http://www.annonces.nc/"]

    def parse(self, response):
        categories = response.css("div#global > table")[1].css("ul")[0].css("a.btnMenuAccueil")[1:]
        for c in categories:
            category_url = "http://www.annonces.nc/async_annonces.php?generic=cat&id_cat={}&filtre_type=0&no_reload_pub=1&form_par_page=500".format(
                c.css("::attr(data-idcat)")[0].extract())
            # print c.css("::attr(data-idcat)")[0].extract()
            category = c.css("::attr(data-libelle)")[0].extract().replace("-", " ")
            # if category == "informatique":
            yield scrapy.Request(category_url, callback=self.parse_category, meta={"category": category, "page": 1})
            return ###############################################################################################


    def parse_category(self, response):
        products = response.css("span[id*='header_annonce']::attr(id)")
        # print len(products), response.meta["category"]
        # print response.url
        for p in products:
            product_id = p.extract().split("header_annonce_")[1]
            product_url = "http://www.annonces.nc/a_an.php?g=detail_annonce&id={}".format(product_id)
            yield scrapy.Request(product_url, callback=self.parse_product, meta={"category": response.meta["category"], "product_id": product_id})
            return ###############################################################################################
        if len(products) >= 500:
            url_next_page = "{}&posNopage={}".format(response.url, response.meta["page"]+1)
            yield scrapy.Request(url_next_page, callback=self.parse_category, meta={"category": response.meta["category"], "page": response.meta["page"]+1})

    def parse_product(self, response):
        product_id = response.meta["product_id"]
        hd = response.css("table.antnmo")[0]
        product_type = hd.css("td.antyp::text")[0].extract().strip().encode("utf-8")
        title = hd.css("b::text")[0].extract().strip().encode("utf-8")
        date = hd.css("td[align=right]::text")[0].extract().strip().encode("utf-8")

        #content = response.css("div#detail_{}::text".format(product_id))[0].extract().strip().split("Prix :")
        content = response.xpath("//div[@id='detail_{}']".format(product_id)).extract()#.strip().split("Prix :")
        content = striphtml("\n".join(map(lambda x: x.strip(), content))).split("Prix :")
        description = content[0].strip().encode("utf-8")

        try:
            price = content[1].strip().split("\n")[0].strip().encode("utf-8")
        except:
            price = "-"
        pass
        thumbnails = response.css("a[data-divdest=detailPhoto_{}] > img::attr(data-src)".format(product_id))
        thumbnails = map(lambda t: "http://www.annonces.nc{}".format(t.extract().replace("/_thumbs/", "/")), thumbnails)

        item = AnnoncesProductItem()
        item["category"] = response.meta["category"]
        item["url"] = response.url
        item["product_type"] = product_type
        item["title"] = title
        item["date"] = date
        item["description"] = description
        item["price"] = price
        item["thumbnails"] = thumbnails

        yield item

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)