
f = open("schema.xml")
content = f.read()
f.close()

content = content.replace('stopwords_en', 'stopwords')

newline = """<!-- general -->
	<field name="_version_" type="long" indexed="true" stored="true" multiValued="false"/>"""

content = content.replace('<!-- general -->', newline)

f = open('schema.xml', 'w')
f.write(content)
f.close()
