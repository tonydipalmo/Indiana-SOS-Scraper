from indiana import Indiana


#search_keywords = ["basement", "handy", "landsc", "plumb", "electric", "remodel", "paint", "clean", "hvac", "window", "constr"]
#search_keywords = ["clean", "hvac", "window", "constr"]
#search_keywords = ["inc", "ind", "llc"]
search_keywords = ["ave", "dr.", "way", "street", "lane", "court", "road", "rd."]
#search_keywords = ["renovat", "remodel", "build", "improve", "repair", "bathroom", "kitchen", "basement", "contract", "general"]
#search_keywords = ["bathroom", "kitchen", "basement", "contract", "general"]

def test():
    for search in search_keywords:
        new = Indiana()
        new.run(search_phrase=search)
    
test()