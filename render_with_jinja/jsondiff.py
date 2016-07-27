import json
import xml.etree.ElementTree as ETree

s = '{"version":"$${abi_routing_version}","lastRoutingNumber":"$${last_routing_number}"}'
t = '{"version":"$${asdf}","lastRoutingNumber":"$${last_routing_number}"}'

wicked = """{"web-app": {
  "servlet": [   
    {
      "servlet-name": "cofaxCDS",
      "servlet-class": "org.cofax.cds.CDSServlet",
      "init-param": {
        "configGlossary:installationAt": "Philadelphia, PA",
        "configGlossary:adminEmail": "ksm@pobox.com",
        "configGlossary:poweredBy": "Cofax",
        "configGlossary:poweredByIcon": "/images/cofax.gif",
        "configGlossary:staticPath": "/content/static",
        "templateProcessorClass": "org.cofax.WysiwygTemplate",
        "templateLoaderClass": "org.cofax.FilesTemplateLoader",
        "templatePath": "templates",
        "templateOverridePath": "",
        "defaultListTemplate": "listTemplate.htm",
        "defaultFileTemplate": "articleTemplate.htm",
        "useJSP": false,
        "jspListTemplate": "listTemplate.jsp",
        "jspFileTemplate": "articleTemplate.jsp",
        "cachePackageTagsTrack": 200,
        "cachePackageTagsStore": 200,
        "cachePackageTagsRefresh": 60,
        "cacheTemplatesTrack": 100,
        "cacheTemplatesStore": 50,
        "cacheTemplatesRefresh": 15,
        "cachePagesTrack": 200,
        "cachePagesStore": 100,
        "cachePagesRefresh": 10,
        "cachePagesDirtyRead": 10,
        "searchEngineListTemplate": "forSearchEnginesList.htm",
        "searchEngineFileTemplate": "forSearchEngines.htm",
        "searchEngineRobotsDb": "WEB-INF/robots.db",
        "useDataStore": true,
        "dataStoreClass": "org.cofax.SqlDataStore",
        "redirectionClass": "org.cofax.SqlRedirection",
        "dataStoreName": "cofax",
        "dataStoreDriver": "com.microsoft.jdbc.sqlserver.SQLServerDriver",
        "dataStoreUrl": "jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon",
        "dataStoreUser": "sa",
        "dataStorePassword": "dataStoreTestQuery",
        "dataStoreTestQuery": "SET NOCOUNT ON;select test='test';",
        "dataStoreLogFile": "/usr/local/tomcat/logs/datastore.log",
        "dataStoreInitConns": 10,
        "dataStoreMaxConns": 100,
        "dataStoreConnUsageLimit": 100,
        "dataStoreLogLevel": "debug",
        "maxUrlLength": 500}},
    {
      "servlet-name": "cofaxEmail",
      "servlet-class": "org.cofax.cds.EmailServlet",
      "init-param": {
      "mailHost": "mail1",
      "mailHostOverride": "mail2"}},
    {
      "servlet-name": "cofaxAdmin",
      "servlet-class": "org.cofax.cds.AdminServlet"},
 
    {
      "servlet-name": "fileServlet",
      "servlet-class": "org.cofax.cds.FileServlet"},
    {
      "servlet-name": "cofaxTools",
      "servlet-class": "org.cofax.cms.CofaxToolsServlet",
      "init-param": {
        "templatePath": "toolstemplates/",
        "log": 1,
        "logLocation": "/usr/local/tomcat/logs/CofaxTools.log",
        "logMaxSize": "",
        "dataLog": 1,
        "dataLogLocation": "/usr/local/tomcat/logs/dataLog.log",
        "dataLogMaxSize": "",
        "removePageCache": "/content/admin/remove?cache=pages&id=",
        "removeTemplateCache": "/content/admin/remove?cache=templates&id=",
        "fileTransferFolder": "/usr/local/tomcat/webapps/content/fileTransferFolder",
        "lookInContext": 1,
        "adminGroupID": 4,
        "betaServer": true}}],
  "servlet-mapping": {
    "cofaxCDS": "/",
    "cofaxEmail": "/cofaxutil/aemail/*",
    "cofaxAdmin": "/admin/*",
    "fileServlet": "/static/*",
    "cofaxTools": "/tools/*"},
 
  "taglib": {
    "taglib-uri": "cofax.tld",
    "taglib-location": "/WEB-INF/tlds/cofax.tld"}}}"""


wicked_different = """{"web-app": {
  "servlet": [
    {
      "servlet-name": "cofaxCDS",
      "servlet-class": "org.cofax.cds.CDSServlet",
      "init-param": {
        "configGlossary:installationAt": "Philadelphia, PA",
        "configGlossary:adminEmail": "ksm@pobox.com",
        "configGlossary:poweredBy": "Cofax",
        "configGlossary:poweredByIcon": "/images/cofax.gif",
        "configGlossary:staticPath": "/content/static",
        "templateProcessorClass": "org.cofax.WysiwygTemplate",
        "templateLoaderClass": "org.cofax.FilesTemplateLoader",
        "templatePath": "templates",
        "templateOverridePath": "",
        "defaultListTemplate": "listTemplate.htm",
        "defaultFileTemplate": "articleTemplate.htm",
        "useJSP": false,
        "jspListTemplate": "listTemplate.jsp",
        "jspFileTemplate": "articleTemplate.jsp",
        "cachePackageTagsTrack": 200,
        "cachePackageTagsStore": 200,
        "cachePackageTagsRefresh": 99999999999,
        "cacheTemplatesTrack": 100,
        "cacheTemplatesStore": 50,
        "cacheTemplatesRefresh": 15,
        "cachePagesTrack": 200,
        "cachePagesStore": 100,
        "cachePagesRefresh": 10,
        "cachePagesDirtyRead": 10,
        "searchEngineListTemplate": "forSearchEnginesList.htm",
        "searchEngineFileTemplate": "forSearchEngines.htm",
        "searchEngineRobotsDb": "WEB-INF/robots.db",
        "useDataStore": true,
        "dataStoreClass": "org.cofax.SqlDataStore",
        "redirectionClass": "org.cofax.SqlRedirection",
        "dataStoreName": "cofax",
        "dataStoreDriver": "com.microsoft.jdbc.sqlserver.SQLServerDriver",
        "dataStoreUrl": "jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon",
        "dataStoreUser": "sa",
        "dataStorePassword": "dataStoreTestQuery",
        "dataStoreTestQuery": "SET NOCOUNT ON;select test='test';",
        "dataStoreLogFile": "/usr/local/tomcat/logs/datastore.log",
        "dataStoreInitConns": 10,
        "dataStoreMaxConns": 100,
        "dataStoreConnUsageLimit": 100,
        "dataStoreLogLevel": "debug",
        "maxUrlLength": 500}},
    {
      "servlet-name": "cofaxEmail",
      "servlet-class": "org.cofax.cds.EmailServlet",
      "init-param": {
      "mailHost": "mail1",
      "mailHostOverride": "mail2"}},
    {
      "servlet-name": "cofaxAdmin",
      "servlet-class": "org.cofax.cds.AdminServlet"},

    {
      "servlet-name": "fileServlet",
      "servlet-class": "org.cofax.cds.FileServlet"},
    {
      "servlet-name": "cofaxTools",
      "servlet-class": "org.cofax.cms.CofaxToolsServlet",
      "init-param": {
        "templatePath": "I AM CHANGED",
        "log": 1,
        "logLocation": "/usr/local/tomcat/logs/CofaxTools.log",
        "logMaxSize": "",
        "dataLog": 1,
        "dataLogLocation": "/usr/local/tomcat/logs/dataLog.log",
        "dataLogMaxSize": "",
        "removePageCache": "/content/admin/remove?cache=pages&id=",
        "removeTemplateCache": "/content/admin/remove?cache=templates&id=",
        "fileTransferFolder": "/usr/local/tomcat/webapps/content/fileTransferFolder",
        "lookInContext": 1,
        "adminGroupID": 4,
        "betaServer": true}}],
  "servlet-mapping": {
    "cofaxCDS": "/",
    "cofaxEmail": "/cofaxutil/aemail/*",
    "cofaxAdmin": "/admin/*",
    "fileServlet": "/static/*",
    "cofaxTools": "/tools/*"},

  "taglib": {
    "taglib-uri": "cofax.tld",
    "taglib-location": "/WEB-INF/tlds/cofax.tld"}}}"""

tag = 'abi-routing-number'

simple = """{
  "fen": "2502590-6",
  "fencomp": "25025906",
  "legacyFileNo": "2502590677",
  "legacyFileNoChange": "2502590688",
  "legacyFileNoShort": "250259067",
  "legacyFileNoShortChange": "250259068"
}"""

simpleb = """{
  "fen": "2502590-z",
  "fencomp": "25025906",
  "legacyFileNo": "2502590677",
  "legacyFileNoChange": "2502590688",
  "legacyFileNoShort": "25025906Q",
  "legacyFileNoShortChange": "250259068"
}"""


def json_elem_to_string(element_list):
    """Turns a list of (String, JSON Object) tuples and returns updated
    (String, remainder (JSON Object) tuples. The top level of each JSON Object
     is peeled off and appended to the given String in order to allow for
     recursive transformation of JSON into faux-JSONPath.
    """
    new_element_list = []
    for element in element_list:
        base_str, elem = element
        for item in elem:
            item_base_str = base_str
            new_element_list.append(make_jsonpath_str(item_base_str, elem, item))

    return new_element_list


def make_jsonpath_str(item_base_str, elem, item):
    """Takes a base string, an element, and a part of that element, and creates
    a faux-JSONPath string with the item appended to the base string.

    If the item has nested elements, one layer is peeled off, and, a
    "remainder" is created, which contains any dict or list parts that will
     need to be parsed further down the loop.

    Returns a tuple (New Base String, remainder)
    """
    elem_type = type(elem)
    # this fails on anything but a string, which makes sense
    if type(item) == str:
        value = elem[item]
    remainder = None
    if elem_type == dict:
        item_base_str += '{' + item + ':'
        if type(value) in [str, int, float]:
            item_base_str += str(value)
        elif type(value) == bool:
            item_base_str += str(value).lower()
        elif type(value) is None:
            remainder = None
        else:
            remainder = value
    elif elem_type == list:
        item_base_str += '['
        if type(item) in [str, int, float]:
            item_base_str += str(item)
        elif type(value) == bool:
            item_base_str += str(value).lower()
        elif type(value) is None:
            remainder = None
        else:
            remainder = item
    # I don't think this get used ever...
    # elif elem_type in [str, int, bool]:
    #     item_base_str += str(item)
    #     remainder = None
    else:
        raise Exception

    return item_base_str, remainder


def parse_json_path(json_object):
    """Takes a JSON Object and turns it into a list of faux-JSONPath strings."""
    string_list = []
    remainder = [('', json_object)]
    while remainder:
        result = json_elem_to_string(remainder)
        remainder = []
        for string, obj in result:
            if obj is None:
                string_list.append(string)
            else:
                remainder.append((string, obj))

    return string_list


def json_elem_to_xml(element_list):
    """Turns a list of (Element, JSON Object) tuples and returns updated
    (Element, remainder (JSON Object) tuples. The top level of each JSON Object
     is peeled off and appended to the given Element in order to allow for
     recursive transformation of JSON into XML.
    """
    new_element_list = []
    # This is the list of current parent elements and their child json objects.
    # for elem in element_list:
    #     parent_element, json_obj_list = elem
    for parent_element, json_obj, in element_list:
        # This is the list of things we're about to turn into child elements.

            obj_type = type(json_obj)
            if obj_type == dict:
                # Parse out each dict entry's value.
                for key in json_obj:
                    value = json_obj[key]
                    new_element_list.append(make_new_elem(parent_element, key, value))
            elif obj_type == list:
                # We fudge the element name because thankfully, we don't ever have to convert back, and it compares ok.
                for value in json_obj:
                    new_element_list.append(make_new_elem(parent_element, 'arrayValue', value))
            else:
                raise Exception

    return new_element_list


def make_new_elem(parent, elem_name, value):
    """Takes a parent XML Element, a name, and a value, and creates
    a SubElement of the parent with that name. If the SubElement's contents
    are of type str, int, bool, or None, the SubElement will have that value
    as its .text.

    Otherwise, a "remainder" is created, which contains any dict or list
    parts that will need to be parsed further down the loop.

    Returns a tuple (SubElement, remainder)
    """
    new_elem = ETree.SubElement(parent, elem_name)
    if type(value) in [str, int, float]:
        new_elem.text = str(value)
        remainder = None
    elif type(value) == bool:
        new_elem.text = str(value).lower()
        remainder = None
    elif type(value) is None:
        remainder = None
    else:
        remainder = value

    return new_elem, remainder


def json_to_xml(json_string):
    """Turns a JSON string into an XML Element with a "testResponse" root.
    This could be easily genericized to take any root element name.
    """
    json_object = json.loads(json_string)
    new_response_xml = ETree.Element('testResponseHttpBody')
    data_to_process = [(new_response_xml, json_object)]
    while data_to_process:
        result = json_elem_to_xml(data_to_process)
        data_to_process = []
        for new_elem, remainder in result:
            if remainder is not None:
                data_to_process.append((new_elem, remainder))

    return new_response_xml


def req_json_to_xml(json_string):
    json_object = json.loads(json_string)
    new_request_xml = ETree.Element('testRequestHttpBody')
    data_to_process = [(new_request_xml, json_object)]
    while data_to_process:
        result = json_elem_to_xml(data_to_process)
        data_to_process = []
        for new_elem, remainder in result:
            if remainder is not None:
                data_to_process.append((new_elem, remainder))
    return new_request_xml


def sql_json_to_xml(json_string):
    json_object = json.loads(json_string)
    new_sql_xml = ETree.Element('testRow')
    data_to_process = [(new_sql_xml, json_object)]
    while data_to_process:
        result = json_elem_to_xml(data_to_process)
        data_to_process = []
        for new_elem, remainder in result:
            if remainder is not None:
                data_to_process.append((new_elem, remainder))
    return new_sql_xml


def sql_queries_json_to_xml(root, json_string):
    json_object = json.loads(json_string)
    new_sql_xml = ETree.SubElement(root, 'testSqlQueries')
    data_to_process = [(new_sql_xml, json_object)]
    while data_to_process:
        result = json_elem_to_xml(data_to_process)
        data_to_process = []
        for new_elem, remainder in result:
            if remainder is not None:
                data_to_process.append((new_elem, remainder))
    return new_sql_xml


def diff_strings(a, b):
    """Takes two "custom JSONPath" strings and returns two lists of strings,
    enumerating the things in list a that are not in list b, and vice versa.
    """
    in_a_not_in_b = []
    in_b_not_in_a = []
    json_a = json.loads(a)
    json_b = json.loads(b)

    if json_a == json_b:
        pass
    else:
        a_list = parse_json_path(json_a)
        b_list = parse_json_path(json_b)

        pop_list = b_list[:]
        for item in a_list:
            if item not in pop_list:
                in_a_not_in_b.append(item)
            else:
                pop_list.remove(item)

        pop_list = a_list[:]
        for item in b_list:
            if item not in pop_list:
                in_b_not_in_a.append(item)
            else:
                pop_list.remove(item)

    return in_a_not_in_b, in_b_not_in_a
