import xml.dom
import xml.sax


def interpret_text(txt):
    def builder(doc):
        return doc.createTextNode(txt)
    return builder


def interpret_document_template(template):
    def builder(dictionary):
        doc = xml.dom.getDOMImplementation().createDocument(None, None, None)
        stack = [doc]

        class Builder(xml.sax.ContentHandler):

            def startElement(self, name, attrs):
                if name == 'PARAM':
                    param = dictionary[attrs['name']]
                    if type(param) == str:
                        elmt = doc.createTextNode(param)
                        assert isinstance(elmt, xml.dom.Node)
                    else:
                        elmt = param(doc)
                        assert isinstance(elmt, xml.dom.Node)
                    assert isinstance(elmt, xml.dom.Node)
                else:
                    elmt = doc.createElement(name)
                    for name in attrs.getNames():
                        elmt.setAttribute(name, attrs[name])
                stack.append(elmt)

            def endElement(self, name):
                elmt = stack.pop()
                elmt.normalize()
                stack[-1].appendChild(elmt)

            def characters(self, content):
                node = doc.createTextNode(content)
                stack[-1].appendChild(node)

            def ignorableWhitespace(self, content):
                pass

            def processingInstruction(self, target, data):
                pi = doc.createProcessingInstruction(target, data)
                stack[-1].appendChild(pi)

        xml.sax.parseString(template, Builder())
        return doc

    return builder


def interpret_template(template):
    def parameterizer(dictionary):
        def builder(document):
            doc = document
            stack = []

            class Builder(xml.sax.ContentHandler):

                def startElement(self, name, attrs):
                    if name == 'PARAM':
                        param = dictionary[attrs['name']]
                        if type(param) == str:
                            elmt = doc.createTextNode(param)
                        else:
                            elmt = param(doc)
                    else:
                        elmt = doc.createElement(name)
                        for name in attrs.getNames():
                            elmt.setAttribute(name, attrs[name])
                    assert isinstance(elmt, xml.dom.Node)
                    stack.append(elmt)

                def endElement(self, name):
                    elmt = stack.pop()
                    elmt.normalize()
                    if stack:
                        stack[-1].appendChild(elmt)
                    else:
                        stack.append(elmt)

                def characters(self, content):
                    node = doc.createTextNode(content)
                    stack[-1].appendChild(node)

            xml.sax.parseString(template, Builder())
            return stack[-1]
        return builder
    return parameterizer