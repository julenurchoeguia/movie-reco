from email.mime import image
import streamlit as st
import pickle
from fuzzywuzzy import process

def load_films_from_binary_file(filename):
    with open(filename, 'rb') as f:
        films = pickle.load(f)
    return films

def fuzzy_search_title(films, search_term):
    results = []
    titles = [film["title"] for film in films]
    matches = process.extract(search_term, titles, limit=5)
    
    for match in matches:
        title, score = match
        film_index = next((i for i, film in enumerate(films) if film["title"] == title), None)
        if film_index is not None:
            film_info = films.pop(film_index)
            result = {
                "title": film_info["title"],
                "year": film_info.get("year", None),
                "director": film_info.get("director", None),
                "image": film_info.get("image", None),
                "idwikidata": film_info["idwikidata"],
                "score": score
            }
            results.append(result)
    
    return results


# Load films from the binary file
loaded_films = load_films_from_binary_file("data/films_data.bin")

# Initialize session state (list of ids)
if "list_ids" not in st.session_state:
    st.session_state.list_ids = []

# Streamlit app
st.title('Movie Search App')

#Side bar "My List"
st.sidebar.title("My List")
st.sidebar.write("Here are the movies you've added to your list:")

id_list = st.session_state.list_ids
for id in id_list:
    film = next((f for f in loaded_films if f["idwikidata"] == id), None)
    if film:
        st.sidebar.write(film["title"])
        if st.sidebar.button('Remove from my list', key= "remove_"+id):
            id_list.remove(id)
            st.sidebar.write("Removed from your list!")
            #force the sidebar to update
            st.rerun()
        st.sidebar.write("------")

# Search bar
search_term = st.text_input('Enter movie title:')
if search_term:
    results = fuzzy_search_title(loaded_films, search_term)
    st.subheader("Top 5 fuzzy search results for '{}':".format(search_term))
    for result in results:
        image = result["image"]
        if image:
            st.image(image, width=200)
        st.write(f"Title: {result['title']}")
        st.write(f"Year: {result['year']}")
        st.write(f"Director: {result['director']}")
        st.write(f"ID Wikidata: {result['idwikidata']}")
        st.write(f"Score: {result['score']}")

        # Check if idwikidata is not in the session_state id_list
        if result['idwikidata'] not in id_list:
            # Add button to select movie
            if st.button('Add to my list', key="add_"+result['idwikidata']):
                # Append idwikidata to id_list in session_state
                id_list.append(result['idwikidata'])
                st.rerun()
                
                
        else:
            st.write("Added to your list!")

        st.write("------")