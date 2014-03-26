import itertools

def catlist(list_of_list):
    return list(itertools.chain.from_iterable(list_of_list))
