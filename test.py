from indiana import Indiana

search_keywords = ["inc", "ind", "llc"]

def test():
    for search in search_keywords:
        new = Indiana()
        new.run(search_phrase=search)
    
test()