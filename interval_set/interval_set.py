"""
Functions to manage and convert intervals set.

An interval is a tuple (begin, end). An interval of 1 element where eID is the
element ID is formated (eID, eID).

An interval set is a list of non overlapping intervals.
"""
#
# Conversion operations
#

#
# String conversion
#


def interval_set_to_string(intervals, separator=" "):
    '''
    Convert interval set to strings:

    >>> interval_set_to_string([(1, 2), (5, 5), (10, 50)])
    '1-2 5 10-50'
    '''
    res = ''
    for (begin, end) in intervals:
        if begin == end:
            res += separator + str(begin)

        else:
            res += separator + '{}-{}'.format(begin, end)
    return res.strip(separator)


def string_to_interval_set(s, separator=" "):
    """Transforms a string interval set representation to interval set

    >>> string_to_interval_set("1 2 3 7-9 13")
    [(1, 1), (2, 2), (3, 3), (7, 9), (13, 13)]
    >>> string_to_interval_set("")
    []
    >>> string_to_interval_set("(2,3)")
    Traceback (most recent call last):
        ...
    ValueError: Bad interval format. Parsed string is: (2,3)
    """
    intervals = []
    if not s:
        return []
    try:
        res_str = s.split(separator)
        if '-' in (separator).join(res_str):
            # it is already intervals so get it directly
            for inter in res_str:
                splitted = inter.split('-')
                if len(splitted) == 2:
                    (begin, end) = splitted
                    intervals.append((int(begin), int(end)))
                else:
                    intervals.append((int(inter), int(inter)))
        else:
            res = sorted([int(x) for x in res_str])
            intervals = id_list_to_iterval_set(res)
    except (ValueError, IndexError):
        raise ValueError("Bad interval format. Parsed string is: {}".format(s))

    return intervals


#
# ID list conversion
#

def id_list_to_iterval_set(ids):
    """Convert list of ID (int) to an intervals set"""
    itvs = []
    if ids:
        b = ids[0]
        e = ids[0]
        for i in ids:
            if i > (e + 1):  # end itv and prepare new itv
                itvs.append((b, e))
                b = i
            e = i
        itvs.append((b, e))

    return itvs


def interval_set_to_id_list(itvs):
    """ Convert an interval set to a list of ID (int)"""
    ids = []
    for itv in itvs:
        b, e = itv
        ids.extend(range(b, e + 1))
    return ids


#
# Set conversion
#

def interval_set_to_set(intervals):
    """ Convert interval set to python set

    >>> interval_set_to_set([])
    set()
    >>> interval_set_to_set([(1, 1), (3, 4)])
    {1, 3, 4}
    """
    s = set()

    for (begin, end) in intervals:
        for x in range(begin, end+1):
            s.add(x)

    return s


def set_to_interval_set(s):
    """ Convert python set to interval set

    >>> set_to_interval_set(set())
    []
    >>> set_to_interval_set({1, 2, 5, 7, 9, 10, 11})
    [(1, 2), (5, 5), (7, 7), (9, 11)]
    """
    intervals = []
    l = list(s)
    l.sort()

    if len(l) > 0:
        i = 0
        current_interval = [l[i], l[i]]
        i += 1

        while i < len(l):
            if l[i] == current_interval[1] + 1:
                current_interval[1] = l[i]
            else:
                intervals.append(tuple(current_interval))
                current_interval = [l[i], l[i]]
            i += 1

        if current_interval not in intervals:
            intervals.append(tuple(current_interval))

    return intervals


#
# Info operations
#


def total(itvs):
    '''
    Compute the total number of element by a cumulative sum on the size
    of all intervals

    >>> total([])
    0
    >>> total([(0, 0)])
    1
    >>> total([(1, 1), (3, 4)])
    3
    '''
    # Add +1 because it is a closed interval
    return sum([(end - begin) + 1 for begin, end in itvs])


#
# Ensemble operations
#


def equals(itvs1, itvs2):
    """ Check for equality between two interval sets

    TODO: this version is working bu it is not optimized...

    >>> equals([],[])
    True
    >>> equals([(1, 1)],[(1, 2)])
    False
    >>> equals([(1, 10)],[])
    False
    >>> equals([(1, 2), (3, 4)], [(1, 4)])
    True
    >>> equals([(5, 100), (3, 4)], [(3, 4), (5, 100)])
    True
    """
    return interval_set_to_set(itvs1) == interval_set_to_set(itvs2)


def difference(itvs_base, itvs2):
    """ returns the difference between an interval set and an other

    >>> difference([], [(1, 1)])
    []
    >>> difference([(1, 1), (3, 4)], [(1, 2), (4, 7)])
    [(3, 3)]
    >>> difference([(1, 12)], [(1, 2), (4, 7)])
    [(3, 3), (8, 12)]
    """
    itvs1 = [(k, v) for (k, v) in itvs_base]
    lx = len(itvs1)
    ly = len(itvs2)
    i = 0
    k = 0
    itvs = []

    while (i < lx) and (lx > 0):
        x = itvs1[i]
        if (k == ly):
            itvs.append(x)
            i += 1
        else:
            y = itvs2[k]
            # y before x w/ no overlap
            if (y[1] < x[0]):
                k += 1
            else:
                # x before y w/ no overlap
                if (y[0] > x[1]):
                    itvs.append(x)
                    i += 1
                else:
                    if (y[0] > x[0]):
                        if (y[1] < x[1]):
                            # x overlap totally y
                            itvs.append((x[0], y[0] - 1))
                            itvs1[i] = (y[1] + 1, x[1])
                            k += 1
                        else:
                            # x overlap partially
                            itvs.append((x[0], y[0] - 1))
                            i += 1
                    else:
                        if (y[1] < x[1]):
                            # x overlap partially
                            itvs1[i] = (y[1] + 1, x[1])
                            k += 1
                        else:
                            # y overlap totally x
                            i += 1

    return itvs


def intersection(itvs1, itvs2):
    """Returns an interval set that is an intersection of itvs1 and itvs2.

    >>> intersection([(1, 2), (4, 5)], [(1, 3), (5, 7)])
    [(1, 2), (5, 5)]
    >>> intersection([(2, 3), (5, 7)], [(1, 1), (4, 4)])
    []
    >>> intersection([(3, 7)], [(2, 8)])
    [(3, 7)]
    >>> intersection([(3, 7)], [(2, 6)])
    [(3, 6)]
    """

    lx = len(itvs1)
    ly = len(itvs2)
    i = 0
    k = 0
    itvs = []

    while (i < lx) and (lx > 0) and (ly > 0):
        x = itvs1[i]
        if (k == ly):
            break
        else:
            y = itvs2[k]

        # y before x w/ no overlap
        if (y[1] < x[0]):
            k += 1
        else:

            # x before y w/ no overlap
            if (y[0] > x[1]):
                i += 1
            else:

                if (y[0] >= x[0]):
                    if (y[1] <= x[1]):
                        itvs.append(y)
                        k += 1
                    else:
                        itvs.append((y[0], x[1]))
                        i += 1
                else:
                    if (y[1] <= x[1]):
                        itvs.append((x[0], y[1]))
                        k += 1
                    else:
                        itvs.append(x)
                        i += 1
    return itvs


def union(itvs1, itvs2):
    """ Do the union of two interval sets

    TODO: this version is working bu it is not optimized...

    >>> union([(1, 1), (3, 4)], [(1, 2), (4, 7)])
    [(1, 7)]
    """

    intersect = intersection(itvs1, itvs2)
    diff12 = difference(itvs1, itvs2)
    diff21 = difference(itvs2, itvs1)
    union = aggregate(intersect + diff12 + diff21)
    return union


def aggregate(itvs):
    """Aggregate *NOT overlapping* intervals (intersect must be empty) to
    remove gaps.

    >>> aggregate([])
    []
    >>> aggregate([(1, 2), (3, 4)])
    [(1, 4)]
    >>> aggregate([(3, 4), (1, 2)])
    [(1, 4)]
    """
    lg = len(itvs)
    if lg <= 1:
        return itvs

    # sort intervals
    itvs = sorted(itvs)
    res = []
    i = 1
    a, b = itvs[0]
    while True:
        if i == lg:
            res.append((a, b))
            return res
        else:
            x, y = itvs[i]
            if x == (b + 1):
                b = y
            else:
                res.append((a, b))
                a, b = x, y
            i += 1
