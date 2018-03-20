#-*- coding: utf-8 -*-
#XRD technique
import csv, os, math, xml.etree.ElementTree as ET, numpy as np
import json
from xml.etree import ElementTree
import zipfile
import numpy as np, matplotlib.pyplot as plt
import os, sys
import types

# Parent Classes
class _ReferenceFile():
        """Parent Class for all XRD Reference Pattern Files"""
        filename = ""
        shortname = ""
        legend = ""
        xtal_system = ""
        flavour = ""
        reference = ""

# Object classes to open and process data files from different sources
# and formats
class ICDDXmlFile(_ReferenceFile):
        """
        Class that imports ICDD xml file containing XRD reference
        data. 'flavour' ("thousand" or "hundred") optional argument
        gives the option to not divide all values by 10
        """
        pdf_number = ""
        dataframe = ""

        def __init__(self, filename):
                self.filename = filename
                tree = ET.parse(filename)
                root = tree.getroot()
                formula = root.find('.//chemical_formula')
                self.shortname = formula.text
                try:
                        self.xtal_system = xtal.text
                except:
                        pass
                pdf = root.find('.//pdf_number')
                self.pdf_number = pdf.text
                legend = filename[:-4].split(r'/')
                self.legend = legend[-1]
                try:
                        self.reference = root.find('.//references/reference_group/reference').text
                except:
                        pass
                # self.dataframe = 
                
        
        @property               # Now Legacy
        def peak_data(self):#Used by other functions
                tree = ET.parse(self.filename)
                root = tree.getroot()

                theta_list, intensity_list, h_list, k_list, l_list, hkl_list, d_list = [],[],[],[],[],[],[]

                for theta in root.findall('.//theta'):
                        theta_list.append(float(theta.text))

                for intensity in root.findall('.//intensity/intensity'):
                        intensity_list.append(intensity.text)
                
                for h in root.findall('.//intensity/h'):
                        h_list.append(h.text)
                
                for k in root.findall('.//intensity/k'):
                        k_list.append(k.text)
                        
                for l in root.findall('.//intensity/l'):
                        l_list.append(l.text)
                
                for h in range (0, len(h_list)):
                        try:
                                hkl_list.append(str(h_list[h] + k_list[h] + l_list[h]))
                        except:
                                pass

                for d in root.findall('.//intensity/da'):
                        d_list.append(float(d.text))
                
                intensity_list[:] = [x for x in intensity_list if x != '\n']
                intensity_list[:] = [x.rstrip('m') for x in intensity_list]
                intensity_list[:] = [x.lstrip('<') for x in intensity_list]
                intensity_list[:] = [x or 1 for x in intensity_list]
                intensity_list[:] = [100*int(x)/int(max(intensity_list)) for x in intensity_list]
                intensity_list[:] = [x if x > 1 else 0 for x in intensity_list]
                
                return theta_list, intensity_list, hkl_list, h_list, k_list, l_list, d_list
        
        def bragg_law(self, d_list, wavelength):
                """Returns a list of new 2theta values given a list of d_values and a wavelength via Braggs law"""
                new_twotheta = []
                for d in d_list:
                        new_twotheta.append(2*math.degrees(np.arcsin(wavelength/(2*d))))
                return new_twotheta

        def export_csv(self, export_to):
                # if export_to[-3:] != "csv":
                #         export_to = export_to + '.csv'
                x, y = self.peak_data[0:2]
                _export_csv(x, y, export_to)

def _export_csv(x, y, export_to):
        """Exports x and y data to a comma-separated ascii file.

        Arguments
        ---------
        x : list
            list of x values to be written to the first column in the
            .csv file

        y : list
            list of y values to be written to the second column in the
            .csv file

        export_to : str
            destination path to file
        """

        with open(export_to, 'w', newline='') as e:
                writer = csv.writer(e, delimiter=',')
                for i in range (0, len(x)):
                        writer.writerow([x[i], y[i]])

                
if __name__ == '__main__':
    args = sys.argv[1:]
    print(args)
    for arg in args:
            print(arg)
            if os.path.exists(arg):
                    print (os.path.basename(arg))
    t, i, h, j, k, l, m = ICDDXmlFile(arg).peak_data
    _export_csv(t, i, os.path.splitext(arg)[0] + '.csv')
