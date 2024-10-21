
#generate import statements from ai_search_ut.py

from ai_search import search

# method to test the search function
def test_search():
    # test search function
    docs = search("What's Micosoft's Fabric?", search_type='hybrid', top_k=5)
    return docs
    
    
    
    
# call test_search method
if __name__ == "__main__":
    
    # add try catch block to handle any kind of exception that might occur
    try:
        docs = test_search()
        print(docs)
    except Exception as e:
        #print(e)
        None
        
    






