from lxml import etree

f = StringIO("<foo><bar></bar></foo>")
tree = etree.parse(f)

r = tree.xpath("/foo/bar")
len(r)
