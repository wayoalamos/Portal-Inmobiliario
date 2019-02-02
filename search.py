from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import csv
import time

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

        self.ratio_one = None # UF / Superficie
        self.ratio_two = None #UF / Terreno

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

    def change_href(self, href):
        self.href = href

    def change_dorms(self, dorms):
        self.dorms = dorms

    def change_surface(self, surface):
        try:
            surface = self.clean_surface(surface)
        except:
            print("error al limpiar surface string")
        self.surface_built = float(surface[0])
        if len(surface) > 1:
            self.surface_all = float(surface[1])

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

    def calculate_ratios(self):
        try:
            if(self.surface_built):
                self.ratio_one = self.value / self.surface_built
            if(self.surface_all):
                self.ratio_two = self.value / self.surface_all
        except:
            self.ratio_one = "Error"
            self.ratio_two = "Error"

    def list_of_attr(self):
        self.calculate_ratios()
        attr = [self.title, self.category, self.location, self.code, self.dorms,
        self.surface_built, self.surface_all, self.value, self.ratio_one, self.ratio_two, self.href]
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
        self.data = []
        self.mode = 1 # 0 in file, 1 in web
        self.workbook = None
        self.workbook_active = None
        self.status = 1 # 0 if it was uncomplete request
        self.last_url = None

    def find_products(self, url):
        # has_items: if the website has product_item or not
        if not "&pg=" in url:
            url = url + "&pg=1"
        has_items = True
        start_time = time.time()
        while has_items:
            has_items = False
            response = self.simple_get(url)
            if response:
                # conver html with BeautifulSoup

                print(" la url: ", url)
                html = BeautifulSoup(response, 'html.parser')
                for div in html.find_all("div", class_=self.is_product_item_propiedad):
                    has_items = True
                    self.take_info(div)

                # take last number of the url and add 1
                page_number = int(url[url.rfind("=")+1:]) + 1
                page_number = str(page_number)

                # change url adding one to the page
                url = url[:url.rfind("=")+1] + page_number

                """
                PARA QUE NO SE CAIGA A LOS 28 seg

                if time.time() - start_time > 28:
                    print("no more!!")
                    self.status = 0
                    self.last_url = url
                    return"""


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
            for a in elem.find_all('a', href=True):
                item.href = "http://www.portalinmobiliario.com" + a["href"]

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
            headers = {'User-Agent': 'Mozilla/5.0'}
            with closing(get(url, headers=headers, stream=True)) as resp:
                # print("url: ", url)
                # print("url type:", type(url))
                # print("resp: ", resp)
                # print("is good:", self.is_good_response(resp))
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            print('Error en la request {0} : {1}'.format(url, str(e)))
            return None

    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        print("content type: ", content_type)
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def is_product_item_propiedad(self, css_class):
        if css_class:
            if "row product-item propiedad" in css_class:
                return css_class

    def is_product_item_summary(self, css_class):
        if css_class:
            if "product-item-summary" in css_class:
                return css_class

    def write_file(self, item):
        if self.mode == 0:
            self.writer.writerow(item.list_of_attr())
        if self.mode == 1:
            self.workbook_active.append(item.list_of_attr())
        else:
            if self.data == []:
                self.data = ""
            line = item.str_of_attr()
            self.data += line

if __name__ == "__main__":
    s = Search()
    url = 'https://www.portalinmobiliario.com/venta/departamento/las-condes-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=1'
    url = 'https://www.portalinmobiliario.com/venta/sitio/las-condes-metropolitana?ca=3&ts=1&mn=2&or=&sf=1&sp=0&at=0&pg=5'
    s.find_products(url)
