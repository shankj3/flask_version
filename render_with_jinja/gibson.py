"""
.. module:: gibson
   :synopsis: A high-performance XML difference engine for comparing XML
              pairs, and extracting data from pairs whose text elements are
              formatted in a specific "mo money" manner.

.. moduleauthor:: Emily Langer <emily.langer@expeditors.com>
"""

import re
import logging
from dateutil import parser
import datetime

logger = logging.getLogger('PynetServer')


def diff_xml(expected_xml, live_xml, validate_strict_order, xpaths_to_ignore=None):
    """
    Diffs two ElementTree Elements.

    Takes two Element instances, transforms them into two lists, one for
    expected, one for live data. Each of those contains lists of tuples
    representing the elements contained in the respective XML trees.
    These lists are diffed, and variables in $${} format are extracted.

    xpaths_to_ignore takes a list of strings which is passed to
    get_comparison_objects. Elements that match are ignored and not validated.

    :param expected_xml: XML containing the expected data.
    :type expected_xml: xml.etree.ElementTree.Element
    :param live_xml: XML containing the live response data.
    :type live_xml: xml.etree.ElementTree.Element
    :param xpaths_to_ignore: List of XPath strings which should be used
        to filter elements that should not be diffed.
    :type xpaths_to_ignore: None, list
    :returns: List of tuples: (Parsed variables dict, non-matching elements from expected_xml,
        non-matching elements from live_xml)
    :rtype: tuple
    """
    expected_xml_objects = get_comparison_objects(expected_xml, xpaths_to_ignore)
    live_xml_objects = get_comparison_objects(live_xml, xpaths_to_ignore)

    expected_xml_objects, live_xml_objects = compare_lists_strict(expected_xml_objects, live_xml_objects,
                                                                  validate_strict_order)

    mo_money_dict, expected_xml_objects, live_xml_objects = get_mo_money(expected_xml_objects, live_xml_objects)

    return mo_money_dict, expected_xml_objects, live_xml_objects


def get_comparison_objects(xml_element, xpaths_to_ignore=None):
    """
    Builds list-of-tuples representations of each element and its ancestors.

    Python's xml.etree.ElementTree module does not offer Element objects
    whose contents can be directly compared. To address this issue in an
    efficient way, we expand Elements into representations comprised of
    Python built-ins, which can be compared very quickly and cheaply.

    Each childless Element is represented by a (tag, attrib, text) tuple,
    and each of its ancestors is represented only by (tag, attrib), as
    the text attribute of those Elements is typically whitespace, which
    we want to ignore for our purposes.

    xpaths_to_ignore takes a list of strings to use as args for
    Element.findall(). Elements that match are discarded (not returned)
    as they are not to be validated.

    :param xml_element: The XML object to be broken into a list of tuples.
    :type xml_element: xml.etree.ElementTree.Element
    :param xpaths_to_ignore: List of XPath strings which should be used
        to filter elements in xml_element.
    :type xpaths_to_ignore: None, list
    :returns: List of tuples that represent xml_element and its children.
    :rtype: list
    """
    # Build dict of {child: parent} relationships
    parent_map = {child: parent for parent in xml_element.iter() for child in parent}
    # This is where all of our childless nodes go for later comparison.
    compare_list = []

    # Generate a set of all elements which match the xpaths_to_ignore.
    ignore_set = set()
    if xpaths_to_ignore:
        for xpath in xpaths_to_ignore:
            ignore_set.update(xml_element.findall(xpath))

    # Handling the root by itself lets us bypass the check for None after .get()ting
    # from the ancestor_map in the loop below. Root has no parent_info.
    ancestor_map = {}
    if xml_element not in ignore_set:
        ancestor_map[xml_element] = [(xml_element.tag, xml_element.attrib)]
    # If there are no children, we want to compare everything.
    if not list(xml_element):
        compare_list.append([(xml_element.tag, xml_element.attrib, xml_element.text)])

    xml_element_iter = xml_element.iter()
    next(xml_element_iter)  # Skip the root, because we've already handled it.
    for elem in xml_element_iter:
        parent = parent_map.get(elem)
        parent_info = ancestor_map.get(parent)
        # No parent info means the parent was ignored, and elem should be too.
        # TODO: This implementation ignores cases where an element whose contents
        # we don't care about goes missing entirely, which might not be what we
        # what we want. We might want to make sure the element is at least present.
        # This complicates the ignore process, but is possible. Evaluate how
        # important that might be and implement if necessary.
        if elem in ignore_set or parent_info is None:
            continue
        if list(elem):  # See if the elem has children
            # If so, don't track the element's text. 99% of the time, it's just
            # the whitespace between elements, which we don't want to validate.
            elem_info = [(elem.tag, elem.attrib)]
            elem_info.extend(parent_info)
            ancestor_map[elem] = elem_info
        else:
            # If there are no children, track everything
            elem_info = [(elem.tag, elem.attrib, elem.text)]
            elem_info.extend(parent_info)
            compare_list.append(elem_info)

    # Reorders things to be more XPath-like, like a person would expect.
    # We should probably do this at the end, when there isn't much left to reverse.
    for item in compare_list:
        item.reverse()

    return compare_list


def compare_lists_strict(list_a, list_b, validate_strict_order=False):
    """
    Compares two lists, keeping both ordered and accounting for duplicates.

    Compare two lists without using a shortcut like set(list_a) - set(list_b)
    or a simple list comprehension because those don't account for the
    possibility that there may be perfect duplicates of list members, and we
    need to make sure the correct number of each are present.

    :param list_a: First list to compare
    :type list_a: list
    :param list_b: Second list to compare
    :type list_b: list
    :returns: Tuple containing the elements of the respective lists which were
        not found in the opposing list.
    :rtype: tuple
    """
    # It's really cheap to do this quick check first,
    # and is lightning fast if it works.

    if list_a == list_b:
        return [], []
    else:
        if validate_strict_order is True:
            for i in range(len(list_a)):
                if list_a[i] != list_b[i]:
                    list_a_leftovers = list_a[i:]
                    list_b = list_b[i:]
                    break
        else:
        # Can't modify the list we're iterating over, and
        # this is the fastest way to shallow copy a list
            list_a_leftovers = list_a[:]
            for a_obj in list_a:
                if a_obj in list_b:
                    # We can't modify the list we iterate over, so we modify the copy.
                    list_a_leftovers.remove(a_obj)
                    # But we can modify this one. Makes our final list at the
                    # same time it shrinks the comparison pool!
                    list_b.remove(a_obj)
    return list_a_leftovers, list_b


def get_mo_money(expected_xml_extras, live_xml_extras):
    """
    Parses out "mo money" variables and removes "matched" diff remainders.

    Checks two lists of objects returned from get_comparison_objects for
    "mo money" variables (in the $${variable} format). If an expected XML
    element's text contains a mo money variable, get_mo_money tries to find
    its corresponding element in the live XML.

    If successful, the value from the live element is saved to a dictionary
    with the variable name as its key. The two elements are now considered
    matched, and are thus removed from their respective lists of differences.

    :param expected_xml_extras: The list of remaining element representations
        in the expected XML that were left after comparing to the live XML.
    :type expected_xml_extras: list
    :param live_xml_extras: The list of remaining element representations
        in the live XML that were left after comparing to the expected XML.
    :type live_xml_extras: list
    :returns: (Parsed variables dict, non-matching elements from expected_xml,
        non-matching elements from live_xml)
    :raises: ValueError if a mo money variable is specified in the
        expected XML, but its match cannot be found in the live XML.
    :rtype: tuple
    """
    mo_money = {}
    # Can't modify the list we're iterating over, and
    # this is the fastest way to shallow copy a list
    leftover_expected_extras = expected_xml_extras[:]
    for expected_extra in expected_xml_extras:
        # Go to the last element (the childless node) and
        # expand the (tag, attribute, text) tuple.
        expected_tag, expected_attrib, expected_text = expected_extra[-1]
        if expected_text is None:
            expected_text = ''  # Element.text returns None, not '', if there's no text.

        if expected_text.find('$${') == -1:
            continue  # Didn't find the opening bracket. Move along.

        match = re.search('\$\$\{\s*([\w\_]+)\s*\}', expected_text)
        if not match:
            continue  # False positive during find. There's no closing bracket.

        key = match.group(1)
        # Compare the ancestry by slicing the childless element off the end.
        live_matches = [l for l in live_xml_extras if l[:-1] == expected_extra[:-1]]
        found_match = False  # Using a flag instead of a for/else for you old-timey Java folks... :)
        for live_match in live_matches:
            live_tag, live_attrib, live_text = live_match[-1]  # Expand just the childless element part.
            if live_tag == expected_tag and live_attrib == expected_attrib:
                mo_money[key] = live_text
                leftover_expected_extras.remove(expected_extra)  # These are now "matches".
                live_xml_extras.remove(live_match)
                found_match = True
                break
        if found_match is False:
            raise ValueError('Could not find expected $${} match in live response! Missing variable', key)

    return mo_money, leftover_expected_extras, live_xml_extras


def pretty_print_differences(expected_xml_leftovers, live_xml_leftovers, verbose=False, sort_result=True):
    """
    Pretty prints differences output by diff_xml().

    Takes diff lists output by diff_xml() and generates a list of strings
    for logging purposes. Strings are sorted such that related mismatches are
    usually printed next to each other, and lined up with each other in order
    to make the differences easier for a human to spot.

    :param expected_xml_leftovers: The list of remaining element representations
        in the expected XML that were left after comparing to the live XML.
    :type expected_xml_leftovers: list
    :param live_xml_leftovers: The list of remaining element representations
        in the live XML that were left after comparing to the expected XML.
    :type live_xml_leftovers: list
    :param verbose: If True, element attributes for ancestor elements are also
        printed. If False, only tags are returned for ancestors.
    :type verbose: bool
    :returns: List of strings, each representing one of the input mismatches.
    :rtype: list
    """
    # Define the transform function once at the top, so we don't have to check
    # verbose each time we go to build a string. Speed, speed, speed.
    if verbose is True:
        elem_tuple_to_str = lambda x: ''.join([x[0], str(x[1])])
    else:
        elem_tuple_to_str = lambda x: x[0]

    # Setting this up lets us de-dupe the loop below.
    work_dict = {'Expected: /': expected_xml_leftovers,
                 'Live    : /': live_xml_leftovers}

    # Turning the below into a list comprehension is faster... by about 2%.l
    # But it's 200% harder to understand.
    combined_leftovers = []
    for prefix, leftover_list in work_dict.items():
        for leftover in leftover_list:
            # We keep the string in a few different pieces to allow us to
            # sort/group similar elements together, i.e. put expected values
            # next to their likely live counterparts.
            if leftover[-1][2] is None:  # Another check for None. We don't just str() it, cause we don't want
                elem_text = ''           # the printed string to look like '[None]'.
            else:
                elem_text = leftover[-1][2]

            string_parts = [prefix,
                            '/'.join([elem_tuple_to_str(e) for e in leftover]),
                            ''.join(['[', elem_text, ']'])]
            combined_leftovers.append(string_parts)

    # Sort the parts, then join them into their final strings. Sort first
    # by ancestry, then put Expected above Live for each ancestry group.
    if sort_result is True:
        result_strings = [''.join(leftover) for leftover in
                          sorted(combined_leftovers, key=lambda x: (x[1], x[0]))]
    else:
        result_strings = [''.join(leftover) for leftover in sorted(combined_leftovers, key=lambda x: x[0])]
    return result_strings


def get_num_date_ignore_xpaths(xpaths_range_for_num_date, test_xml, live_xml, xpaths_ignore_num_date):
    """Finds test case level xpaths that are date/number ranges, grabs the range and uses the number to validate
    whether the expected response is in acceptable range of the live response. if so, adds that xpath to xpaths
    to ignore.
    :param xpaths_range_for_num_date: XPath to validate on, along with the  number range that considers the
    live value acceptable.
    :type xpaths_range_for_num_date: list
    :param test_xml: XML containing expected data.
    :type test_xml: xml.etree.ElementTree.Element
    :param live_xml: XML containing the live response data.
    :type live_xml: xml.etree.ElementTree.Element
    :param xpaths_ignore_num_date:
    :type xpaths_ignore_num_date: list

    :return: List of qualified XPaths to ignore because the live data fit within the number range provided by
    xpaths_range_for_num_date
    """
    for m in xpaths_range_for_num_date:
        xpath, acceptable_range = m.split(',', 1)
        number_or_date_tovalidate = test_xml.findtext(xpath)
        if not acceptable_range or not number_or_date_tovalidate:
            raise ValueError('Element or value missing from "testXPathAndRangeForNum" element group')
        if number_or_date_tovalidate.isdigit():
            upper_bound, lower_bound, num_live_int = num_compare(acceptable_range, number_or_date_tovalidate,
                                                                 live_xml, xpath)
            if lower_bound <= num_live_int <= upper_bound:
                xpaths_ignore_num_date += [xpath]
        else:
            upper_bound, lower_bound, real_date = date_compare(acceptable_range, number_or_date_tovalidate,
                                                               live_xml, xpath)
            try:
                if real_date and lower_bound <= real_date <= upper_bound:
                    xpaths_ignore_num_date += [xpath]
            except TypeError:
                logger.error("Error: type is not same for expected time and real time")
    return xpaths_ignore_num_date


def num_compare(range_no, num_date, live_response_xml, xpath):
    range_1 = re.findall('\d+', range_no)[0]
    big = int(num_date) + int(range_1)
    small = int(num_date) - int(range_1)
    num_live = live_response_xml.findtext(xpath)
    num_live_int = int(num_live)
    return big, small, num_live_int


def date_compare(range_no, num_date, live_response_xml, xpath):
    range_all = range_no.strip()[5:]
    range_day, range_1 = range_all.split('T')
    hour2, minute2, second2_1 = range_1.split(':')
    day = range_day
    second2 = float(second2_1)
    expected_datetime = parser.parse(num_date)
    # print(expected_datetime)
    bigger = expected_datetime + datetime.timedelta(int(day), int(second2), 0, 0, int(minute2), int(hour2), 0)
    smaller = expected_datetime - datetime.timedelta(int(day), int(second2), 0, 0, int(minute2), int(hour2), 0)
    time_live = live_response_xml.findtext(xpath)
    real_dat1 = ''
    datetime.timedelta()
    if time_live:
        real_dat1 = parser.parse(time_live)
    return bigger, smaller, real_dat1
