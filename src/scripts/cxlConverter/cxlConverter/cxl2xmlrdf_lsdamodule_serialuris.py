import xml.etree.ElementTree as ET
import owlready2
from sys import argv
from getopt import getopt,GetoptError
from owlready2 import *
from _datetime import datetime

#globals
nsDict = {}
nsPref = {}
sddoDict = {}
ontoClasses = {}
ontoProperties = {}

## parse cxl and extract classes and properties
def process_cxl(filename):

    ## read and parse cxl (xml) file into a tree
    print("reading file: " + filename)
    tree = ET.parse(filename)
    root = tree.getroot()
    ## print concept nodes and their contents
#    for concept in root:
#        print(concept,concept.attrib)

    ## initialize dicts for classes
    classDict = {}
    classDefs = {}

    for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}concept'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}concept'):
#        print(neighbor,neighbor.attrib)
        classId = neighbor.attrib['id']
        classLabel = neighbor.attrib['label']

        classDict[classId] = classLabel
#        print("found a class")
        classDefs[classLabel] = []

    ## initalize data structures for properties
    props = set()
    propDict = {}
    propDefs = []

    for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}linking-phrase'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}linking-phrase'):

        propId = neighbor.attrib['id']
        propLabel = neighbor.attrib['label']
        if propLabel == 'is a' or propLabel == 'is-a' or propLabel == 'are':
            propLabel = 'isA'

        propDict[propId] = propLabel
        props.add(propLabel)

        propDefs.append(propLabel)

    triples = set()

    for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):
    ## sometimes tags contain the namespace, if so use the next line instead of the previous
#     for neighbor in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

        fromId = neighbor.attrib['from-id']
        toId = neighbor.attrib['to-id']

        if fromId in classDict.keys():

            fromLabel = classDict[fromId]
            propLabel = propDict[toId]
            toLabel = ""

            for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):
            ## sometimes tags contain the namespace, if so use the next line instead of the previous
#             for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

                fromId1 = neighbor1.attrib['from-id']
                toId1 = neighbor1.attrib['to-id']

                if fromId1 == toId and toId1 in classDict.keys():
                    toLabel = classDict[toId1]

            if toLabel != "":
                triples.add((fromLabel,propLabel,toLabel))
#                print ("FROM: " + fromLabel + "PROP: " + propLabel + "TO: " + toLabel)
                if fromLabel not in classDefs.keys():
                    classDefs[fromLabel] = [(propLabel,toLabel)]
                else:
                    if (propLabel,toLabel) not in classDefs[fromLabel]:
                        classDefs[fromLabel].append((propLabel,toLabel))

        elif fromId in propDict.keys() and toId in classDict.keys():

            fromLabel = ""
            propLabel = propDict[fromId]
            toLabel = classDict[toId]


            for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):
            ## sometimes tags contain the namespace, if so use the next line instead of the previous
#             for neighbor1 in root.iter('{http://cmap.ihmc.us/xml/cmap/}connection'):

                fromId1 = neighbor1.attrib['from-id']
                toId1 = neighbor1.attrib['to-id']

                if fromId == toId1:
                    fromLabel = classDict[fromId1]

            triples.add((fromLabel,propLabel,toLabel))
#            print ("FROM: " + fromLabel + " PROP: " + propLabel + "TO: " + toLabel)
            if fromLabel not in classDefs.keys():
                classDefs[fromLabel] = [(propLabel,toLabel)]
            else:
                if (propLabel,toLabel) not in classDefs[fromLabel]:
                    classDefs[fromLabel].append((propLabel,toLabel))

    return classDefs,propDefs

def regNameSpaces(convertedOnto):
    # ET.register_namespace('', baseNamespace)
    # ET.register_namespace('owl', 'http://www.w3.org/2002/07/owl#')
    # ET.register_namespace('rdfs', 'http://www.w3.org/2000/01/rdf-schema#')
    # ET.register_namespace('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    # ET.register_namespace('obo', 'http://purl.obolibrary.org/obo/')
    # ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
    # ET.register_namespace('xsd', 'http://www.w3.org/2001/XMLSchema#')
    # ET.register_namespace('oboInOwl', 'http://www.geneontology.org/formats/oboInOwl#')
    # ET.register_namespace('sddo', 'http://purl.obolibrary.org/obo/sddo.owl#')

    obo = convertedOnto.get_namespace("http://purl.obolibrary.org/obo/")
    sddo = convertedOnto.get_namespace("http://purl.obolibrary.org/obo/sddo.owl#")
    oboInOwl = convertedOnto.get_namespace("http://www.geneontology.org/formats/oboInOwl#")
    lsda = obo


    nsDict["obo"] = obo
    nsDict["sddo"] = sddo
    nsDict["oboInOwl"] = oboInOwl
    nsDict["lsda"] = lsda
    nsPref["sddo"] = "SDDO_"
    nsPref["lsda"] = "LSDA_"
    nsPref["ro"] = "RO_"

def getOntologies():
    onto_path.append("./")
    sddoOnto = get_ontology('http://purl.obolibrary.org/obo/sddo.owl').load()
    roOnto = get_ontology('ro-base.owl').load()
    instr = sddoOnto.search_one(label = "instrument")
    for cls in sddoOnto.classes():
        sddoDict["sddo:" + cls.name] = cls.iri
        ontoClasses["sddo:" + str(cls.label.first())] = cls
#        print("Adding class to SDDO: " + "sddo:" + str(cls.label.first()))
#        print("SDDO Class: " + cls.iri)
    for prop in sddoOnto.object_properties():
        sddoDict["sddo:" + prop.name] = prop.iri
        ontoProperties["sddo:" + str(prop.label.first())] = prop
    for prop in roOnto.object_properties():
#        print("RO Property: " + prop.iri + " " + prop.label.first())
        ontoProperties["ro:" + str(prop.label.first())] = prop

    return sddoOnto, roOnto

def dataProp(classes,someClass):

    subjectClass = ""
    for cls in classes.keys():
        for propRel in classes[cls]:
            propLabel = propRel[0]
            objectLabel = propRel[1]
            if (propLabel == "has" and objectLabel == someClass):
                return cls
    return subjectClass



def main(argv):
#    filename = "LSDA-20220110DCB.xml"
    targetnamespace = ""

    try:
        opts, args = getopt(argv,"hi:n:o:p:",["input=","namespace=","outputFile=","prefix="])
    except GetoptError:
        print("cxl2xmlrdf_serialuris.py -n <namespace IRI> -i <inputCXL> -p <prefix>")
        exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('cxl2xmlrdf_serialuris.py -n <namespace IRI> -n <namespace> -i <inputFile> -o <outputFile> -p <prefix>')
            exit()
        elif opt in ("-n", "--namespace"):
            targetnamespace = arg
        elif opt in ("-p", "--prefix"):
            targetprefix = arg
        elif opt in ("-i", "--input"):
            filename = arg
        elif opt in ("-o", "--output"):
            outputfilename = arg



    sddoOnto, roOnto = getOntologies()
    convertedOnto = get_ontology(targetnamespace + outputfilename)
    regNameSpaces(convertedOnto)
    classes, properties = process_cxl("./input/"+filename)


    ## Initialize serialized URIs
    ## predefine entity URIs
    uri_pref = "SDDO_"
#    uri_seq = 3000000

    uri_prefixes = {
        "SDDO_" : 4000000,
        "LSDA_" : 1,
        "SPASE_" : 1
        }


#   "lsda:Mission" : "LSDA_3000008"

    ## Wrap classes and properties in XMLRDF tags
#    xml = '<?xml version="1.0" encoding="UTF-8"?><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:sddo="http://purl.obolibrary.org/obo/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#" xmlns:owl2="http://www.w3.org/2006/12/owl2-xml#" xmlns:owl="http://www.w3.org/2002/07/owl#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">'


    propSpace = ""
    propertyEntities = {}
    for propLabel in properties:

    ## assign namespace
        if ':' in propLabel:
            cleanLabel = propLabel[propLabel.find(':')+1:]
            if propLabel.find(':') > -1:
                propSpace = propLabel[0:propLabel.find(':')]

        # declare new properties
        if propSpace == "lsda":
            with nsDict["obo"]:
                with convertedOnto:
                    if (propLabel != "isA" and propLabel != "sameAs" and propLabel != "has"):
                        print("PropLabel = " + propLabel)
                        if (propSpace == targetprefix):
                            cls = ""
                            if (propLabel == 'has'):
                                cls = types.new_class(cleanLabel, (DataProperty,),)
                            else:
                                cls = types.new_class(cleanLabel, (ObjectProperty,),)
                                cls.label.append(cleanLabel)

                            cls.namespace = nsDict["obo"]
                            cls.iri = targetnamespace + nsPref[propSpace] + "{:07}".format(uri_prefixes[nsPref[propSpace]])
        #                    cls.ID = nsPref[propSpace] + format(uri_prefixes[nsPref[propSpace]])
                            uri_prefixes[nsPref[propSpace]] += 1
                            propertyEntities[propLabel] = cls

    #merge in ext ontology props
    propertyEntities = propertyEntities | ontoProperties

    for classLabel in classes.keys():
        classSpace = ""
        if classLabel.find(':') > -1:
            classSpace = classLabel[0:classLabel.find(':')]
            cleanLabel = classLabel[classLabel.find(':')+1:]
        if (dataProp(classes,classLabel) == ""):
            childOf = ["Thing"]
            for propRel in classes[classLabel]:
                propLabel = propRel[0]
                objectLabel = propRel[1]
                if propLabel == 'isA':
                    if (childOf[0] == "Thing"):
                        childOf =[]
                    childOf.append(objectLabel)

            with nsDict["obo"]:
                with convertedOnto:
                    if (classSpace == "lsda"):
                        cls = types.new_class(cleanLabel,(Thing,),)
    #                    print("classSPace: " + classSpace + " class: " + classLabel)
                        print("Adding class: " + cleanLabel + " " + targetnamespace + nsPref[classSpace] + "{:07}".format(uri_prefixes[nsPref[classSpace]]))
                        cls.label.append(cleanLabel)
                        cls.iri = targetnamespace + nsPref[classSpace] + "{:07}".format(uri_prefixes[nsPref[classSpace]])
                        uri_prefixes[nsPref[classSpace]] += 1
                        ontoClasses[classLabel]=cls

    for classLabel in classes.keys():
        classSpace = ""
        if classLabel.find(':') > -1:
            classSpace = classLabel[0:classLabel.find(':')]
            cleanLabel = classLabel[classLabel.find(':')+1:]
        subjClass = dataProp(classes,classLabel)
        if (subjClass != ""):
            with nsDict["obo"]:
                with convertedOnto:
                    cls = types.new_class(cleanLabel, (DataProperty,),)
                    print("Calculated subject = " + subjClass)
                    cls.domain.append(ontoClasses[subjClass])
                    cls.label.append(cleanLabel)
                    cls.iri = targetnamespace + nsPref["lsda"] + "{:07}".format(uri_prefixes[nsPref["lsda"]])
                    uri_prefixes[nsPref["lsda"]] += 1
                    print("Creating data property = " + cleanLabel + " " + cls.iri)
#            cls.label = cleanLabel
            ontoClasses[classLabel]=cls

    for classLabel in classes.keys():
        if (dataProp(classes,classLabel) == ""):
            classSpace = ""
            if classLabel.find(':') > -1:
                classSpace = classLabel[0:classLabel.find(':')]
                cleanLabel = classLabel[classLabel.find(':')+1:]
                ontoClass = ontoClasses[classLabel]

                with convertedOnto:
                    for propRel in classes[classLabel]:
                        propLabel = propRel[0]
                        propSpace = propLabel[0:propLabel.find(':')]
                        objectLabel = propRel[1]
                        print ("FROM: " + classLabel + " PROP: " + propLabel + " TO: " + objectLabel)
                        if (propLabel != 'isA' and propLabel != 'has'):
                            if (propSpace == 'ro'):
                                    print(ontoClass.name + " prop: " + propLabel + " " + ontoClasses[objectLabel].name)
                            ontoClass.is_a.append(propertyEntities[propLabel].some(ontoClasses[objectLabel]))
                        elif propLabel == 'isA':
                            print(classLabel + " is a " + objectLabel)
                            ontoClass.is_a.clear()
                            ontoClass.is_a.append(ontoClasses[objectLabel])
 #
 #                       cls.is_a.append(propLabel.some(objectLabel))

    #Add imports
    convertedOnto.imported_ontologies.append(sddoOnto)
    convertedOnto.imported_ontologies.append(roOnto)
    # write output ontology module
    convertedOnto.save(file = "lsdao_module.owl", format = "rdfxml")
#===============================================================================
#         entities[propLabel] = uri
#
#
#     ## owl-specific
#     xml += '<owl:Ontology  rdf:about="http://purl.obolibrary.org/obo/sddo.owl">'
#     xml += '</owl:Ontology>'
#
#     ## URIs
#     URIs = entities
#
#     for classLabel in classes.keys():
#
#         entitynamespace = namespace
#         entity_uri_prefix = uri_pref
#
#         ## remove spaces, commas and periods from label
#         cleanLabel = classLabel.replace(' ','').replace(',','').replace('.','')
#
#         ### SPECIAL CHARS ###
#         if '&' in cleanLabel:
#             cleanLabel = cleanLabel.replace('&','&amp;')
#
#         cleanLabel = cleanLabel.replace("'",'')
#         cleanLabel = cleanLabel.replace('"','')
#         cleanLabel = cleanLabel.replace('/','')
#         cleanLabel = cleanLabel.replace('\\','')
#
#         if '????' in cleanLabel:
#             cleanLabel = cleanLabel.replace('????','unnamedConcept')
#
#         ## assign namespace
#         if ':' in cleanLabel:
#             cleanLabel = cleanLabel[cleanLabel.find(':')+1:]
#             if 'spase' in classLabel:
#                 entitynamespace = 'https://spase-group.org/data/model/'
#                 entity_uri_prefix = "SPASE_"
#             elif 'genelab' in classLabel:
#                 entitynamespace = 'https://genelab.nasa.gov/schema/'
#                 entity_uri_prefix = "GENELAB_"
#             elif 'lsda' in classLabel:
#                 entitynamespace = 'https://lsda.jsc.nasa.gov/schema/'
#                 entity_uri_prefix = "LSDA_"
#         else:
#             print("Class " + cleanLabel + " is missing its namespace")
#
#         uri = entitynamespace+entity_uri_prefix+"{:07}".format(uri_prefixes[entity_uri_prefix])
#         uri_prefixes[entity_uri_prefix] += 1
#
#         entities[classLabel] = uri
#         print(classLabel)
#
#     for classLabel in classes.keys():
#
#                 ## remove spaces, commas and periods from label
#         cleanLabel = classLabel.replace(' ','').replace(',','').replace('.','')
#
#         ### SPECIAL CHARS ###
#         if '&' in cleanLabel:
#             cleanLabel = cleanLabel.replace('&','&amp;')
#
#         cleanLabel = cleanLabel.replace("'",'')
#         cleanLabel = cleanLabel.replace('"','')
#         cleanLabel = cleanLabel.replace('/','')
#         cleanLabel = cleanLabel.replace('\\','')
#
#         if '????' in cleanLabel:
#             cleanLabel = cleanLabel.replace('????','unnamedConcept')
#
#         cleanLabel = cleanLabel[cleanLabel.find(':')+1:]
#         xml += '<owl:Class rdf:about="'+URIs[classLabel]+'">'
# #         xml += '<owl:Class rdf:about="'+namespace+classLabel+'">'
#         xml += '<rdfs:label xml:lang="en">'+cleanLabel+'</rdfs:label>'
#
#
#         if len(classes[classLabel])>0:
#
#             for propRel in classes[classLabel]:
#
#                 propLabel = propRel[0]
#
#                 objectLabel = propRel[1]
#                 if propLabel == 'isA':
#                     xml += '<rdfs:subClassOf rdf:resource="'+URIs[objectLabel]+'"/>'
#                 else:
#                     xml += '<rdfs:subClassOf><owl:Restriction><owl:onProperty rdf:resource="' + URIs[propLabel] + '"/><owl:someValuesFrom rdf:resource="'+ URIs[objectLabel] + '"/></owl:Restriction></rdfs:subClassOf>'
# #                 xml += '<sddo:'+propLabel+' rdf:resource="'+namespace+objectLabel+'"/>'
#
#
#         ## owl-specific
#         xml += '</owl:Class>'
# #         xml += '</rdf:Description>'
#
#     for prop in properties:
#
#     #     xml += '<rdf:Description rdf:about="'+namespace+prop+'"><rdfs:label xml:lang="en-US">'+prop+'</rdfs:label>'
#
#         ## owl-specific
#         xml += '<owl:ObjectProperty rdf:about="'+URIs[prop]+'">'
# #         xml += '<owl:AnnotationProperty rdf:about="'+namespace+prop+'">'
#         xml += '<rdfs:label xml:lang="en">'+prop+'</rdfs:label>'
#
#         ## owl-specific
#         xml += '</owl:ObjectProperty>'
#     #     xml += '</rdf:Description>'
#
#
#     xml += "</rdf:RDF>"
#
#     newTree = ET.ElementTree(ET.fromstring(xml))
#     ET.indent(newTree, "     ", 0)
#
#     newTree.write('./'+filename.split('.')[0]+'_XMLRDF' + datetime.now().strftime("%d_%m_%Y_%H_%M_%S") + '.xml', "UTF-8", True, 'http://purl.obolibrary.org/obo/sddo.owl#')
#===============================================================================

if __name__ == "__main__":
    main(argv[1:])

    ## output extracted classes,triples to XMLRDF
#    with open('./'+filename.split('.')[0]+'_XMLRDF.xml','w') as xmlfile:
#       xmlfile.write(xml)