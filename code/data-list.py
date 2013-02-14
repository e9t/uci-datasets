#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import html5lib, json

import encoding

def read(url):
    with open(url, 'r') as f:
        parser = html5lib.HTMLParser(\
                tree=html5lib.treebuilders.getTreeBuilder("lxml"),\
                namespaceHTMLElements=False)
        root = parser.parse(f)
    return root

def parse(table, stops):
    rows = []
    for row in table[1::2]:
        columns = list(row.itertext())[2::2]
        columns = columns[0:1] + [columns[1].replace('\n','')] + columns[2:]
        columns = [sanitize(item, stops) for item in columns]
        rows.append(columns)
    return rows

def sanitize(item, stops):
    item = encoding.to_unicode_or_bust(item)
    for s in stops:
        item = item.replace(s, '')
    item = item.strip()
    return item

def concat(rows, baseurl, urlhash):
    return [row + ["%s%s" % (baseurl, urlhash[row[0]])] for row in rows]

def write(rows, attrs, outp):
    with open(outp, 'w') as f:
        f.write('\t'.join(attrs + ['\n']))
        i = 1
        for row in rows:
            row = '\t'.join([str(i)] + row)
            f.write(row.encode('utf-8'))
            f.write('\n')
            i += 1

def main():
    BASEURL = 'http://archive.ics.uci.edu/ml/'
    URL = 'archive.ics.uci.edu-ml-datasets-20130204.html'
    OUTP = 'data-list.tsv'
    STOPS = [u'\n', u'\t', u' <td><p class="normal">', u'</p></td> ', u'&nbsp;']
    ATTRS = ['id', 'name', 'abstract', 'data_type', 'default_task', 'attribute_type',
            'n_instances', 'n_attrs', 'y', 'area', 'url']

    root = read(URL)
    table = root.xpath('//table[@border="1"]//tr')
    names = root.xpath('//p[@class="normal"]/b/a/text()')
    urls = root.xpath('//p[@class="normal"]/b/a/@href')
    urlhash = dict(zip(names, urls))

    rows = parse(table, STOPS)
    rows = concat(rows, BASEURL, urlhash)
    write(rows, ATTRS, OUTP)

main()
