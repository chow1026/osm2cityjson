import xml.sax


class OSMContentHandler(xml.sax.handler.ContentHandler):
    """
    SAX content handler for OSM XML.

    Inspired by https://github.com/gboeing/osmnx/tree/master/osmnx
    /osm_content_handler.py
    """
    def __init__(self):
        self._element = None
        self.object = {'elements': {'nodes': {}, 'ways': {}, 'relations': {}}}
        self.nodes = self.object['elements']['nodes']
        self.ways = self.object['elements']['ways']
        self.relations = self.object['elements']['relations']

    def startElement(self, name, attrs):
        if name == 'osm':
            self.object.update({k: attrs[k] for k in attrs.keys()
                                if k in ('version', 'generator')})

        else:
            if name in ('node', 'way', 'relation'):
                self._element = dict(type=name, tags={}, nodes=[], members=[],
                                     **attrs)
                self._element.update({k: float(attrs[k]) for k in attrs.keys()
                                      if k in ('lat', 'lon')})
                self._element.update({k: str(attrs[k]) for k in attrs.keys()
                                      if k in ('id', 'uid', 'version', 'changeset')})

            elif name == 'tag':
                self._element['tags'].update({attrs['k']: attrs['v']})

            elif name == 'nd':
                self._element['nodes'].append(str(attrs['ref']))

            elif name == 'member':
                member_dict = {"type": str(attrs["type"]),
                               "ref": str(attrs["ref"])}
                if str(attrs["role"]).strip() != "":
                    member_dict.update({"role": str(attrs["role"])})
                self._element['members'].append(member_dict)


    def endElement(self, name):
        if name in ('node', 'way', 'relation'):
            if len(self._element["tags"]) == 0:
                self._element.pop("tags")

            if len(self._element["nodes"]) == 0:
                self._element.pop("nodes")

            if len(self._element["members"]) == 0:
                self._element.pop("members")

            _id = str(self._element.pop("id"))
            if name == 'node':
                self.object['elements']['nodes'].update({_id: self._element})

            if name == 'way':
                self.object['elements']['ways'].update({_id: self._element})

            if name == 'relation':
                self.object['elements']['relations'].update({_id: self._element})
