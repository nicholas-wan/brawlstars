c9_output = './output/c9/c9aurac_brawler_levels_team.xlsx'
c9_output_html = './output/c9/c9aurac_brawler_levels_team.html'
c9_output_png = './output/c9/c9aurac_brawler_levels_team.png'
c9_output_pdf = './output/c9/c9aurac_brawler_levels_team.pdf'


import  jpype     
import  asposecells     
jpype.startJVM() 
from asposecells.api import Workbook
workbook = Workbook(c9_output)
workbook.Save(c9_output_pdf)
jpype.shutdownJVM()