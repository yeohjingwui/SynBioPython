"""
Synbiopython (c) Global BioFoundry Alliance 2020

Synbiopython is licensed under the MIT License.

Code to invoke the SBOL Validator server over the internet

@author: yeohjingwui
This module provides code to work with SBOL validator
https://validator.sbolstandard.org/

Use sample sbol file from github (can also be obtained from iBioSim)

Reference:
    https://github.com/SynBioDex/SBOL-Validator/blob/master/src/test/sequence1.xml
    https://www.w3schools.com/python/ref_requests_post.asp
    http://synbiodex.github.io/SBOL-Validator/#query-parameters
    http://synbiodex.github.io/SBOL-Validator/#options
    http://biopython.org/DIST/docs/tutorial/Tutorial.html (Chapter 17 Graphics)
    https://www.reportlab.com/

install:
pip install biopython
pip install reportlab

The URI prefix is required for FASTA and GenBank conversion,
and optional for SBOL 1 conversion
"""

import requests
import os

from Bio import SeqIO
from Bio.Graphics import GenomeDiagram
from reportlab.lib import colors
from reportlab.lib.units import cm


class GenSBOLconv:

    """ Class to convert standard files (SBOL1, SBOL2, GenBank, Fasta, GFF3)"""

    def export_PlasmidMap(self, gbfile):

        """ Export Linear and Circular Plasmid Map for the generated GenBank file
        """

        record = SeqIO.read(gbfile, "genbank")

        gd_diagram = GenomeDiagram.Diagram(record.id)
        gd_track_for_features = gd_diagram.new_track(1, name="Annotated Features")
        gd_feature_set = gd_track_for_features.new_set()

        for feature in record.features:
            if feature.type != "CDS":
                # Exclude this feature
                continue
            if len(gd_feature_set) % 2 == 0:
                color = colors.lightblue

            else:
                color = colors.blue

            gd_feature_set.add_feature(
                feature,
                sigil="ARROW",
                color=color,
                label_size=12,
                label_angle=0,
                label=True,
            )

        # Draw Linear map from genbank
        gd_diagram.draw(
            format="linear",
            orientation="landscape",
            pagesize="A4",
            fragments=4,
            start=0,
            end=len(record),
        )
        gd_diagram.write("plasmid_linear.pdf", "PDF")
        gd_diagram.write("plasmid_linear.png", "PNG")

        # Draw circular map from genbank
        gd_diagram.draw(
            format="circular",
            circular=True,
            pagesize=(35 * cm, 30 * cm),
            start=0,
            end=len(record),
            circle_core=0.5,
        )
        gd_diagram.write("plasmid_circular.pdf", "PDF")
        gd_diagram.write("plasmid_circular.png", "PNG")

        return record.id

    def SBOLValidator(self, input_file, Output, uri_Prefix=""):

        """ Code to invoke the SBOL Validator server over the internet """

        file = open(input_file).read()

        request = {
            "options": {
                "language": Output,
                "test_equality": False,
                "check_uri_compliance": False,
                "check_completeness": False,
                "check_best_practices": False,
                "fail_on_first_error": False,
                "provide_detailed_stack_trace": False,
                "subset_uri": "",
                "uri_prefix": uri_Prefix,
                "version": "",
                "insert_type": False,
                "main_file_name": "main file",
                "diff_file_name": "comparison file",
            },
            "return_file": True,
            "main_file": file,
        }

        # send POST request to the specified url (Response [200] means ok)
        response = requests.post(
            "https://validator.sbolstandard.org/validate/", json=request
        )

        return response

    def get_outputfile_extension(self, Filetype):

        """ Get the output file extension based on the requested output language
        """

        switcher = {
            "GenBank": ".gb",
            "FASTA": ".fasta",
            "GFF3": ".gff",
            "SBOL1": ".sbol",
            "SBOL2": ".sbol",
        }
        return switcher.get(Filetype, "unknown filetype")

    def export_OutputFile(self, input_filename, Response, Output):

        """ Export the converted output file """

        filename_w_ext = os.path.basename(input_filename)
        filename, file_extension = os.path.splitext(filename_w_ext)

        if Response.json()["valid"]:
            # export the result from json into the specific output file format
            output_filename = filename + self.get_outputfile_extension(Output)
            print("Output file: ", output_filename)

            with open(output_filename, "w", newline="\n") as f:
                f.write(Response.json()["result"])
        else:
            print("Error message: ", Response.json()["errors"])

    def AutoRunSBOLValidator(self, Input_file, Output, uri_Prefix=""):

        """ This wrapper function takes in
          input_file: input file or path to input file
          Output: the Output file type (GenBank, FASTA, GFF3, SBOL1, SBOL2)
          uri_Prefix: '' as default, URI Prefix is required for FASTA and GenBank
                      input conversion
          export output file in your folder """
        Response = self.SBOLValidator(Input_file, Output, uri_Prefix)
        self.export_OutputFile(Input_file, Response, Output)

        return "valid: " + str(Response.json()["valid"])
