import lxml.etree as le

#needed_tags=[']

def get_tag_name(tag_name):
	# remove account prefix from the tag_name by splitting it with '}'
	tag_names=tag_name.split('}',1)
	
	if(len(tag_names)==2):
		return tag_names[1]
	else:
		return tag_name
		
def is_valid_name_tag(elem):

	tag_name=get_tag_name(elem.tag)
	if tag_name == "Name":
		if elem.text=="To" or elem.text=="From" or elem.text=="Date" or elem.text=="Subject":
			return True;
		elif get_tag_name(elem.getparent().tag)=="Folder":
			return True;
		else:
			return False;
	
	return False;


def is_valid_value_tag(elem):
	
	tag_name=get_tag_name(elem.tag)
	
	if tag_name == "Value":
		prev_elem=elem.getprevious()
		prev_tag=None
		
		if(prev_elem is not None):
			prev_tag=get_tag_name(prev_elem.tag)
			print("value =" + tag_name + " , previous tag=" +str(prev_tag))
			return is_valid_name_tag(prev_elem)

	return False;

def check_if_to_be_filtered(elem):

	tag_name=get_tag_name(elem.tag)
		
	# Contain root - Account
	if tag_name == "Account":
		return False
	
	if tag_name == "GlobalId":
		return False
	
	if tag_name == "Folder":
		return False
	
	if tag_name == "Message":
		return False
	
	if is_valid_name_tag(elem):
		return False
	
	if is_valid_value_tag(elem):
		return False
	
	# Contain <BodyContent> tag
	if tag_name == "BodyContent":
		return False
	else:
		return True
	
	
if __name__ == "__main__":

	f=open('myTest.xml','r')
	doc=le.parse(f)
	root=doc.getroot()
	#doc.
	#print(str(root))
	fo=open('myTest_out.xml','w')

	for elem in doc.getiterator():
		
		tag_name=get_tag_name(elem.tag)
		#print(str(tag_name))
		
		is_filtered = check_if_to_be_filtered(elem)
		if not is_filtered:
			fo.write("<"+tag_name+">" + str(elem.text).strip() + "</"+tag_name+">\n")
	
	fo.close()