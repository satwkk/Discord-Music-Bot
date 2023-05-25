# TODO: hacky way, use an optimized algo later
def get_id(url):
    return url.split('/')[-1]

def is_url(keyword):
    if keyword.startswith("http"):
        return True
    return False