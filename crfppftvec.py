__author__ = 'Aleksandar Savkov'

import re
import StringIO

def parse_ftvec_templ(self, s, r):
    """Parses a feature vector template string into a FeatureTemplate object.

    *Important*: if resources (e.g. embeddings) are used in the feature template
    they should be provided during the parsing in the `r` parameter in order to
    be prepacked as parameters to the feature extraction function.

    :param s: feature vector string
    :type s: str
    :param r: dictionary of resources
    :type r: dict
    :return: FeatureTemplate
    """
    fts_str = [x for x in re.sub('[\t ]', '', s).split(';')]
    for ft in fts_str:

        # empty featues (...; ;feature:params)
        if ft.strip() == '':
            continue

        # no parameter features
        no_par = ':' not in ft
        # misplaced column without parameters
        no_par_end_col = ft.count(':') == 1 and ft.endswith(':')
        if no_par or no_par_end_col:
            fn = ft if no_par else ft[:-1]
            self.add_feature(fn)
            continue

        # function name & parameter values
        fn, v = ft.split(':', 1)

        # value matches
        m = re.match('(?:\[([0-9:,-]+)\])?(.+)?', v)

        # window range
        fw = parse_range(m.group(1)) if m.group(1) else None

        # function parameters
        fp = []

        # adding resources to the parameters if required
        if fn in r.keys():
            fp.append(r[fn])

        # adding function parameters if specified
        if m.group(2) is not None:
            fp.extend([x for x in m.group(2).split(',') if x])

        # name, window, parameters
        self.add_win_features(fn, fw, tuple(fp))


def parse_range(r):
    """Parses a range in string representation adhering to the following
    format:
    1:3,6,8:9 -> 1,2,3,6,8,9

    :param r: range string
    :type r: str
    """
    rng = []

    # Range strings
    rss = [x.strip() for x in r.split(',')]

    for rs in rss:
        if ':' in rs:
            # Range start and end
            s, e = (int(x.strip()) for x in rs.split(':'))
            for i in range(s, e + 1):
                rng.append(int(i))
        else:
            rng.append(int(rs))

    return rng


def nrange(start, stop, step):
    """Returns the indices of n-grams in a context window. Works much like
    range(start, stop, step), but the stop index is inclusive, and indices are
    included only if the step can fit between the candidate index and the stop
    index.

    :param start: starting index
    :type start: int
    :param stop: stop index
    :type stop: int
    :param step: n-gram length
    :type step: int
    :return: n-gram indices from left to right
    :rtype: list of int
    """
    idx = start
    rng = []
    while idx + step <= stop + 1:
        rng.append(idx)
        idx += 1
    return rng


def parse_ng_range(fw, n):
    """Transforms context window index list to a context window n-gram index
    list.

    :param fw: context window
    :type fw: list of int
    :param n: n in n-grams
    :type n: int
    :return: n-gram indices
    :rtype: list of int
    """
    subranges = []
    cur = None
    rng = []
    for i in fw:
        if cur == None or cur + 1 == i:
            rng.append(i)
            cur = i
        else:
            subranges.append(rng)
            rng = [i]
            cur = i
    subranges.append(rng)
    nrng = []
    for sr in subranges:
        for i in nrange(sr[0], sr[-1], n):
            nrng.append(i)
    return nrng


def gen_ft(r, ftt=0, n=1, idx=0):
    rng = parse_range(r)
    fts = []
    assert n > 0, 'n needs to be a positive number.'
    for i, ci in enumerate(rng):
        f = 'U%02d:' % (idx + i)
        for i in range(n):
            f = '%s%s[%s,%s]' % (f, '%x', ci + i, ftt)
        fts.append(f)
    return fts


def to_crfpp_template(ftvec):

    fts = []
    b = False

    for fs in ftvec.split(';'):
        if fs == 'B':
            b = True
            continue
        fn, fw = fs[:fs.find('[')], fs[fs.find('[')+1:fs.find(']')]
        n = 3 if fn.startswith('tri') else 2 if fn.startswith('bi') else 1
        fts.extend(gen_ft(fw, int(fn.endswith('pos')), n, len(fts)))

    if b:
        fts.append('B')

    return '\n'.join(fts)
