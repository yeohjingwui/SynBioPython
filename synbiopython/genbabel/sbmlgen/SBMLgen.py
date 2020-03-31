"""
Synbiopython (c) Global BioFoundry Alliance 2020

Synbiopython is licensed under the MIT License.

@author: yeohjingwui
This module is to create SBML file for ODE model using simplesbml package, which relies on libSBML. Reference: https://github.com/sys-bio/simplesbml
The simplesbml package can be installed via pip
> pip install simplesbml
"""

from . import simplesbml
import datetime


class SBMLgen:

    """ class to generate SBML file for ODE model """

    def exportsbml(self, ODE, Variable, Init, ParamName, Param, ParamUnit, **kwargs):

        """ ODE      : The ODEs in the form of string stored in a list
            Variable : The names of variable in a list of string
            Init     : Initial conditions for the variables in a list of values
            ParamName: The names of the parameters stored in a list
            Param    : The parameters values
            ParamUnit: The unit for the parameter according to available unit definition """

        for u in ParamUnit:
            if u == "molL-1min-1":
                ParamUnit[ParamUnit.index(u)] = "molperLmin"
            elif u == "molL-1":
                ParamUnit[ParamUnit.index(u)] = "molperL"
            elif u == "s-1":
                ParamUnit[ParamUnit.index(u)] = "per_second"
            elif u == "min-1":
                ParamUnit[ParamUnit.index(u)] = "per_min"
            elif u == "dimensionless":
                ParamUnit[ParamUnit.index(u)] = "Dimension_less"
            else:
                print("Error in the defined units for parameters")

        model = simplesbml.sbmlModel()

        for s in range(len(Variable)):
            model.addSpecies("[" + Variable[s] + "]", Init[s])

        for p in range(len(Param)):
            model.addParameter(ParamName[p], Param[p], ParamUnit[p])

        for r in range(len(ODE)):
            model.addRateRule(Variable[r], ODE[r])

        Model = model.toSBML()

        output_file = self.getXMLfilename()

        for key, value in kwargs.items():
            if "outputfile" in key:
                output_file = value

        print(Model, file=open(output_file, "w"))

        return Model

    def getXMLfilename(self):

        """ return filename to the XML file according to the export time"""

        timenow = datetime.datetime.now()

        year = str(timenow.year % 100)
        month = str(timenow.month).zfill(2)
        day = str(timenow.day).zfill(2)
        hour = str(timenow.hour).zfill(2)
        minute = str(timenow.minute).zfill(2)

        XMLfilename = year + month + day + "_" + hour + minute + ".xml"

        return XMLfilename