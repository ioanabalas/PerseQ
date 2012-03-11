#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from wikitools import wiki, page, api
import jinja2
from jinja2 import Environment, FileSystemLoader
import os

from xml.dom.minidom import parseString
from Bio import Entrez
from models import snp, snp_url, domain_tag

# list of valid rsids..
snpids = [
"8045560",
"3212346",
"3212350",
"11645278",
"3212352",
"3212353",
"3212354",
"3212356",
"3212358",
"34057592",
"3212379",
"3212360",
"3212361",
"3212362",
"1805005",
"34090186",
"1805006",
"2228479",
"1805007",
"1110400",
"3212365",
"1805008",
"885479",
"35040147",
"34612847",
"35784916",
"34209185",
"3212366",
"34490506",
"12102534",
"3212367",
"2228478",
"3212368",
"34020587",
"3212370",
"3209524",
"3212371",
"2302898",
"12207",
"4395073",
"8049897",
"4785755",
"4408545"]

Entrez.email = 'pamad05+entrez@gmail.com'
# import webapp2
# import pysam

import pprint
pp = pprint.PrettyPrinter(indent=4)

e = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class snpsList(webapp.RequestHandler):
    def get(self):
        t = e.get_template('snplist.html')
        self.response.out.write(t.render(snps = snpids))

class dbSNP(webapp.RequestHandler):
    def get(self):
        snp = self.request.get("snp")
        if not snp:
            snp = "1805007"
        
        res = Entrez.efetch("snp", id=snp, rettype="xml", retmode="text")
        dom = parseString(res.read())

        for node in dom.getElementsByTagName("Rs"):
            # print node.hasAttributes()
            rsid = node.getAttribute("rsId")
            print rsid

        self.response.out.write(dom.toprettyxml())
        # self.response.out.write(res.read().replace("\n","<br>"))


class LookUpSNP(webapp.RequestHandler):
    def get(self):
        snp = self.request.get("snp")
        if len(snp) == 0:
            self.response.out.write("No SNP title given (snp='')")
            return
        site = wiki.Wiki("http://bots.snpedia.com/api.php")
        params = {
            'action': 'query',
            'prop': 'revisions',
            'rvprop': 'content',
            'rvlimit': '1',
            'titles':snp
        }
        req = api.APIRequest(site, params)
        result = req.query(querycontinue=False)

        # if pageid == -1 <=> title=snp does not exist
        pageid = int(result['query']['pages'].keys()[0])
        if pageid == -1:
            self.response.out.write("SNP title does not exist (NoPage)")
            return

        # OMFG this is ugly..
        self.response.out.write(result['query']["pages"][str(pageid)]["revisions"][0]["*"].encode('utf-8').replace("{{","<br>").replace("}}", "<br>").replace("\n","<br>"))

class TestJinja(webapp.RequestHandler):
    def get(self):
        t = e.get_template('hello.html')
        self.response.out.write(t.render(msg = 'Hello World!!!'))


def main():
    application = webapp.WSGIApplication([('/', snpsList),
                                          ('/test', TestJinja),
                                          ('/dbsnp/', dbSNP),
                                          ], debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
