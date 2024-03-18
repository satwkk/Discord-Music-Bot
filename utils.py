from urllib import parse

# TODO: hacky way, use an optimized algo later
def get_id(url):
    return parse.urlsplit(url).path.split('/')[-1]
    # return url.split('/')[-1]

def is_url(keyword):
    if keyword.startswith("http"):
        return True
    return False
