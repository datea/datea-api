from datea_api.utils import remove_accents

def normalize_tag(tag):
    return remove_accents(tag).lower()
