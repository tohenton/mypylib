from collections import namedtuple
from copy import deepcopy

def dict_as_namedtuple(d):
    """Convert dictionary to namedtuple.
    It is useful to access Jenkins build info. It consists of dict and array.
    So accessing each value require specify key name as str liek below.

        bi = jenkins.get_build_info(JOB_NAME, JOB_NUM)
        bi["artifacts"][0]["fileName"]

    Messy!

    namedtuple provide to accessing each value as attribute

        bi = dict_as_namedtuple(jenkins.get_build_info(JOB_NAME, JOB_NUM))
        bi.artifacts[0].fileName

    So smart!
    """

    d = deepcopy(d)
    for key, value in d.iteritems():
        if isinstance(value, dict):    # If dict has dict, convert it recursively
            d[key] = dict_as_namedtuple(value)
        elif isinstance(value, list):  # If dict has list, convert it iteratively
            d[key] = []
            for i in value:
                j = None
                if isinstance(i, dict):  # If list has dict, convert it recusrively
                    j = dict_as_namedtuple(i)
                d[key].append(j)
    return namedtuple('GenericDict', d.keys())(**d)

    for key, value in d.iteritems():
        if isinstance(value, dict):
            d[key] = dict_as_namedtuple(value)
        elif isinstance(value, list):
            d[key] = []
            for i in value:
                d[key].append(dict_as_namedtuple(i))
    return namedtuple('GenericDict', d.keys())(**d)
