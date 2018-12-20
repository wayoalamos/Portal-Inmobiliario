from openpyxl import Workbook

wb = Workbook()
ws = wb.active
a = "1,2,3,4\n 6,5,3"

ws.append([1,2,3])

wb.save("sample.xlsx")
