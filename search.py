from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv

# cuando un producto tiene /m2 en el valor de uf saca el /m2 -> deberia ser ignorado



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

        self.href = None
        # self.image = None

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

    def change_value(self, value):
        value = value.lstrip("UF ")
        value = value.replace(".", "")
        value = value.replace(",", ".")
        # value = value[:value.find("/")] # maybe change this
        try:
            value = float(value)
        except:
            pass
        self.value = value

    def change_dorms(self, dorms):
        self.dorms = dorms

    def change_surface(self, surface):
        try:
            surface = self.clean_surface(surface)
        except:
            print("error while cleaning surface string")
        self.surface_built = surface[0]
        if len(surface) > 1:
            self.surface_all = surface[1]

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
        attr = [self.title, self.category, self.location, self.code, self.dorms, 
        self.surface_built, self.surface_all, self.value]
        return attr

    def str_of_attr(self):
        attr = self.list_of_attr()
        line = ""
        for elem in attr:
            try:
                if elem:
                    elem = str(elem)
                    line += elem + "*#*"
                else:
                    line += " *#*"
            except:
                line += " - *#*"
        line = line.rstrip("*#*")
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
        self.mode = 1 # 0 in file, 1 in web

    def find_products(self, url, limit=0):
        # has_items: if the website has product_item or not
        has_items = True
        while has_items:
            has_items = False
            response = self.simple_get(url)
            if response:
                # conver html with BeautifulSoup
                html = BeautifulSoup(response, 'html.parser')
                for div in html.find_all("div", class_=self.is_product_item):
                    has_items = True
                    self.take_info(div)

                # take last number of the url and add 1
                page_number = int(url[url.rfind("=")+1:]) + 1
                if page_number >= limit and limit != 0:
                    break

                page_number = str(page_number)
                # change url adding one to the page
                url = url[:url.rfind("=")+1] + page_number
                print("url: ", url)

    def clean_string(self, string):
        # decode and encode depending on the string
        if isinstance(string, bytes):
            string = string.decode("utf-8")
        return string

    def take_info(self, div):
        # receives a div
        # write information with self.write_file method
        item = Item()

        # parse main information of the div
        for elem in div.find_all("div", class_=self.is_product_item_summary):
            # it should be just one elem in this for
            counter = 0
            for string in elem.stripped_strings:
                string = self.clean_string(string)
                if counter == 0:
                    if "Proyecto" in string:
                        return
                    item.change_title(string)
                elif counter == 1:
                    item.change_category(string)
                elif counter == 2:
                    item.change_location(string)
                elif counter == 3:
                    item.change_code(string)
                elif counter == 4:
                    item.change_dorms(string)
                counter += 1

        # parse second information of the div
        type = 0
        for elem in div.find_all("div", class_="col-sm-3"):
            for string in elem.stripped_strings:
                string = self.clean_string(string)

                if "Valor" in string:
                    type = 1
                elif "Superficie" in string:
                    type = 2
                elif type == 1:
                    # si el valor esta por m2 lo ignoramos
                    if "/" in string:
                        return
                    item.change_value(string)
                elif type == 2:
                    item.change_surface(string)
                """
                elif type == 3:
                    item.change_low_value(string)
                elif type == 4:
                    item.change_high_value(string)
                """
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
        if self.mode == 0:
            self.writer.writerow(item.list_of_attr())
        else:
            line = item.str_of_attr()
            self.data += line

if __name__ == "__main__":
    s = Search()
    url = 'https://www.portalinmobiliario.com/venta/departamento/las-condes-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=1'
    # s.find_products(url)
    s.find_products(url)

    # print(s.data)



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
