from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

class Item:
    def __init__(self):
        self.title = None
        self.category = None
        self.location = None
        self.address = None
        self.code = None
        self.value = None
        self.low_value = None
        self.high_value = None
        self.surface_built = None
        self.surface_all = None
        self.dorms = None

        self.ratio_departamentos = None # UF / Superficie
        self.ratio_casas = None #UF / Terreno

        # self.image = None
        # self.href = None

    def change_title(self, title):
        title = title.rstrip(",")
        self.title = title

    def change_category(self, category):
        self.category = category

    def change_location(self, location):
        self.location = location

    def change_address(self, address):
        self.address = address

    def change_code(self, code):
        self.code = code
        code_splited = code.split()
        if len(code_splited) > 1:
            self.code = code_splited[1]

    def change_dorms(self, dorms):
        self.dorms = dorms

    def change_value(self, value):
        value = value.lstrip("UF ")
        value = value.replace(".", "")
        value = value.replace(",", ".")
        value = value[:value.find("/")] # maybe change this
        value = float(value)
        self.value = value

    def change_surface(self, surface):
        try:
            surface = self.clean_surface(surface)
        except:
            print("error while cleaning surface string")
        self.surface_built = surface[0]
        self.surface_all = surface[1]

    def change_low_value(self, value):
        value = value.lstrip("UF ")
        value = value.replace(".", "")
        value = value.replace(",", ".")
        value = float(value)
        self.low_value = value

    def change_high_value(self, value):
        value = value.lstrip("UF ")
        value = value.replace(".", "")
        value = value.replace(",", ".")
        value = float(value)
        self.high_value = value

    def clean_surface(self, surface):
        # receives: surface string
        # returns: surface as a list of float

        surface = surface[:surface.find("m")].strip() # elements before m2
        surface = surface.split(" - ")
        for i in range(len(surface)):
            surface[i] = surface[i].replace(".", "")
            surface[i] = surface[i].replace(",", ".")
            surface[i] = float(surface[i])
        return surface

    def list_of_attr(self):
        attr = [self.title, self.category, self.location, self.address,
        self.surface_built, self.surface_all, self.code, self.value,
        self.low_value, self.high_value, self.dorms]
        return attr

    def str_of_attr(self):
        attr = self.list_of_attr()
        line = ""
        for elem in attr:
            try:
                elem = str(elem)
                line += elem + ","
            except:
                line += " - ,"
        line = line.rstrip(",")
        line += "\n"
        return line

    def test(self):
        """
        """
        print("title: ", self.title)
        print("category: ", self.category)
        print("location: ", self.location)
        if self.address:
            print("address: ", self.address)
        print("code: ", self.code)
        if self.value:
            print("value: ", self.value)
        if self.low_value:
            print("low_value: ", self.low_value)
        if self.high_value:
            print("high_value: ", self.high_value)
        if self.dorms:
            print("dorms: ", self.dorms)
        print("surface built: ", self.surface_built)
        print("*************")

class Search:
    def __init__(self):
        self.file_name = "portalinmobiliario.csv"
        self.file = open(self.file_name, "w")
        self.writer = csv.writer(self.file, delimiter=",")
        self.data = ""

    def find_products(self, url):
        has_response = True
        while has_response:
            has_response = False
            response = self.simple_get(url)
            if response is not None:
                html = BeautifulSoup(response, 'html.parser')
                for div in html.find_all("div", class_=self.is_product_item):
                    self.take_info(div)
                    has_response = True
                page_number = str(int(url[url.rfind("=")+1:]) + 1)
                url = url[:url.rfind("=")+1] + page_number
                print("url: ", url)

    def take_info(self, div):
        # in case there is no product summary returns null
        item = Item()
        for elem in div.find_all("div", class_=self.is_product_item_summary):
            counter = 0
            for string in elem.stripped_strings:
                try:
                    string = string.decode("utf-8")
                except:
                    pass
                string = string.encode("utf-8")
                string = str(string)
                if counter == 0:
                    item.change_title(string)
                elif counter == 1:
                    item.change_category(string)
                elif counter == 2:
                    item.change_location(string)
                elif counter == 3:
                    if "Proyecto" in item.title:
                        item.change_address(string)
                    else:
                        item.change_code(string)
                elif counter == 4:
                    if "Proyecto" in item.title:
                        item.change_code(string)
                    else:
                        item.change_dorms(string)
                counter += 1
        type = 0
        for elem in div.find_all("div", class_="col-sm-3"):
            for string in elem.stripped_strings:
                try:
                    string = string.decode("utf-8")
                except:
                    pass
                string = string.encode("utf-8")
                string = str(string)
                if "Valor" in string:
                    type = 1
                elif "Superficie" in string:
                    type = 2
                elif "Desde" in string:
                    type = 3
                elif "Hasta" in string:
                    type = 4

                elif type == 1:
                    item.change_value(string)
                elif type == 2:
                    item.change_surface(string)
                elif type == 3:
                    item.change_low_value(string)
                elif type == 4:
                    item.change_high_value(string)
        self.write_file(item)

    def simple_get(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def is_product_item(self, css_class):
        if css_class:
            if "row product-item" in css_class:
                return css_class

    def is_product_item_summary(self, css_class):
        if css_class:
            if "product-item-summary" in css_class:
                return css_class

    def write_file(self, item):
        # line = item.str_of_attr()
        self.writer.writerow(item.list_of_attr())
        # self.data += line

if __name__ == "__main__":
    s = Search()
    url = 'https://www.portalinmobiliario.com/venta/casa/plaza-nunoa-santiago-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=1'
    s.find_products(url)



"""
x = "casa"
https://www.portalinmobiliario.com/venta/departamento/providencia-metropolitana?tp=2&op=1&ca=2&ts=1&dd=0&dh=6&bd=0&bh=6&or=&mn=2&sf=1&sp=0 #usados
https://www.portalinmobiliario.com/venta/departamento/providencia-metropolitana?tp=2&op=1&ca=3&ts=1&dd=0&dh=6&bd=0&bh=6&or=&mn=2&sf=1&sp=0 # nuevo y usados

https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?tp=1&op=1&ca=2&ts=1&dd=0&dh=6&bd=0&bh=6&or=&mn=2&sf=1&sp=0 #usados
https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?tp=1&op=1&ca=3&ts=1&dd=0&dh=6&bd=0&bh=6&or=&mn=2&sf=1&sp=0 #nuevo y usado
url = 'https://www.portalinmobiliario.com/venta/departamento/providencia-metropolitana'
s.find_products(url)
url = 'https://www.portalinmobiliario.com/venta/departamento/barrio-italia-providencia-santiago-metropolitana'
s.find_products(url)
url = 'https://www.portalinmobiliario.com/venta/departamento/barrio-italia-providencia-santiago-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=4'
s.find_products(url)
url = 'https://www.portalinmobiliario.com/venta/casa/las-condes-metropolitana?ca=2&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=4'
s.find_products(url)
"""
