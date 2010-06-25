"""
Represents a call to a service.
"""
import os, traceback, shutil
import Exscript
from Exscript.util.file import get_hosts_from_csv
from sqlalchemy         import *
from sqlalchemy.orm     import relation, synonym
from tempfile           import NamedTemporaryFile
from lxml               import etree
from util               import mkorderid

class Order(object):
    """
    An order includes all information that is required to make a
    service call.
    """

    def __init__(self, service_name):
        """
        Constructor. The service_name defines the service to whom
        the order is delivered. In other words, this is the
        service name is assigned in the config file of the server.

        @type  service_name: str
        @param service_name: The service that handles the order.
        """
        self.id      = mkorderid(service_name)
        self.status  = 'new'
        self.service = service_name
        self.hosts   = []

    def __repr__(self):
        return "<Order('%s','%s','%s')>" % (self.id, self.service, self.status)

    @staticmethod
    def from_xml(xml):
        """
        Creates a new instance by parsing the given XML.

        @type  xml: str
        @param xml: A string containing an XML formatted order.
        @rtype:  Order
        @return: A new instance of an order.
        """
        # Parse required attributes.
        xml     = etree.fromstring(xml)
        element = xml.find('order')
        order   = Order(element.get('service'))
        order._read_hosts_from_xml(element)
        return order

    @staticmethod
    def from_xml_file(filename):
        """
        Creates a new instance by reading the given XML file.

        @type  filename: str
        @param filename: A file containing an XML formatted order.
        @rtype:  Order
        @return: A new instance of an order.
        """
        # Parse required attributes.
        xml     = etree.parse(filename)
        element = xml.find('order')
        order   = Order(element.get('service'))
        order._read_hosts_from_xml(element)
        return order

    def _read_hosts_from_xml(self, element):
        for host_elem in element.iterfind('host'):
            address = host_elem.get('address').strip()
            args    = self._read_arguments_from_xml(host_elem)
            host    = Exscript.Host(address)
            host.set_all(args)
            self.hosts.append(host)

    def _read_arguments_from_xml(self, host_elem):
        arg_elem = host_elem.find('argument-list')
        if arg_elem is None:
            return {}
        args = {}
        for child in arg_elem.iterfind('variable'):
            name       = child.get('name').strip()
            args[name] = child.text.strip()
        return args

    def fromxml(self, xml):
        """
        Updates the order using the values that are defined in the
        given XML string.

        @type  xml: str
        @param xml: XML
        """
        xml = etree.fromstring(xml)
        self._read_hosts_from_xml(xml.find('order'))

    def _list_to_xml(self, root, name, thelist):
        list_elem = etree.SubElement(root, 'list', name = name)
        for value in thelist:
            item = etree.SubElement(list_elem, 'list-item')
            item.text = value
        return list_elem

    def _arguments_to_xml(self, root, args):
        arg_elem = etree.SubElement(root, 'argument-list')
        for name, value in args.iteritems():
            if isinstance(value, list):
                self._list_to_xml(arg_elem, name, value)
            elif isinstance(value, str):
                variable = etree.SubElement(arg_elem, 'variable', name = name)
                variable.text = value
            else:
                raise Exception('unknown variable type')
        return arg_elem

    def toxml(self, pretty = True):
        """
        Returns the order as an XML formatted string.

        @rtype:  str
        @return: The XML representing the order.
        """
        xml   = etree.Element('xml')
        order = etree.SubElement(xml, 'order', service = self.service)
        for host in self.hosts:
            elem = etree.SubElement(order, 'host', address = host.address)
            self._arguments_to_xml(elem, host.get_all())
        return etree.tostring(xml, pretty_print = pretty)

    def write(self, filename):
        """
        Export the order as an XML file.

        @type  filename: str
        @param filename: XML
        """
        dirname  = os.path.dirname(filename)
        file     = NamedTemporaryFile(dir = dirname, prefix = '.') #delete = False)
        file.write(self.toxml())
        file.flush()
        os.chmod(file.name, 0644)
        os.rename(file.name, filename)
        try:
            file.close()
        except:
            pass

    def is_valid(self):
        """
        Returns True if the order validates, False otherwise.

        @rtype:  bool
        @return: True if the order is valid, False otherwise.
        """
        return True #FIXME

    def get_id(self):
        """
        Returns the order id.

        @rtype:  str
        @return: The id of the order.
        """
        return self.id

    def get_service_name(self):
        """
        Returns the name of the service that is ordered.

        @rtype:  str
        @return: The service name.
        """
        return self.service

    def get_status(self):
        """
        Returns the order status.

        @rtype:  str
        @return: The order status.
        """
        return self.status

    def get_filename(self):
        """
        Creates a filename from the id.

        @rtype:  str
        @return: A filename for the order.
        """
        return self.id + '.xml'

    def add_host(self, host):
        self.hosts.append(host)

    def add_hosts_from_csv(self, filename):
        """
        Parses the given CSV file using
        Exscript.util.file.get_hosts_from_csv(), and adds the resulting
        Exscript.Host objects to the order.
        Multi-column CSVs are supported, i.e. variables defined in the
        Exscript.Host objects are preserved.

        @type  filename: str
        @param filename: A file containing a CSV formatted list of hosts.
        """
        for host in get_hosts_from_csv(filename):
            self.add_host(host)

    def get_hosts(self):
        """
        Returns Exscript.Host objects for all hosts that are
        included in the order.

        @rtype:  [Exscript.Host]
        @return: A list of hosts.
        """
        return self.hosts

if __name__ == '__main__':
    order = Order('test')
    order.add_hosts_from_csv('/nmc/scripts/data/xpc3_discovery/tmdxpc3discovery_2010.05.05_17.03.14.csv')
    print order.toxml()