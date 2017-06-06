"""
Experimenting with an easier interface ...


>>> a = Tree("a@ID=a_id")
>>> c = a.make("b@ID=id2@?=cdata stuff/c@!=Text!/d@#=comm!")
>>> 
>>> pretty = etree.tostring(a.root, pretty_print=True)
>>> print(pretty.decode())
<a ID="a_id">
  <b ID="b_id"><![CDATA[cdata stuff]]><c>Text!<d><!--comm!--></d></c></b>
</a>


>>> 

"""

from lxml import etree
from lxml.etree import CDATA
from lxml.etree import Comment

class Tree():
    def __init__(self, name):
        self.root = self.elem(name)#etree.Element(name)

    def elem(self, name):
        splits = name.split("@")
        name, atts = splits[0], splits[1:]
        name_el = etree.Element(name)
        for att in atts:
            k,v = att.split("=")
            if k == "!":
                name_el.text = v
            elif k == "?":
                name_el.text = CDATA(v)
            elif k =="#":
                name_el.append(Comment(v))
            else:
                name_el.set(k,v)
        return name_el
        
    def make(self, name):

        name = name.replace("\n", "")
        names = name.split("/")
        name0 = names[0]
        root_el = self.elem(name0)#etree.Element(name0)
        self.root.append(root_el)

        last_parent = root_el
        for n in names[1:]:
            n_el = self.elem(n)#etree.Element(n)
            last_parent.append(n_el)
            last_parent = n_el
            
        return last_parent


    
