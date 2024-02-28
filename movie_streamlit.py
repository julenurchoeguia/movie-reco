from email.mime import image
import streamlit as st
import pickle
from fuzzywuzzy import process
from src.query import get_main_subjects, get_related_films, get_displaying_data
from src.similarity import average_vector_similarity, get_embedding
import logging

def load_films_from_binary_file(filename):
    with open(filename, 'rb') as f:
        films = pickle.load(f)
    return films

@st.cache_data(show_spinner=True)
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

@st.cache_data(show_spinner=True)
def get_recommended_films(id_list,nb_films=5):
    print("Getting main subjects...")
    main_subjects_reference = []
    for film_d in get_main_subjects(id_list):
        main_subjects_reference += film_d["main_subjects"]

    print("Getting related films...")
    similar_films = []
    for film_id in id_list:
        related_films = get_related_films(film_id)
        similar_films += related_films
    similar_films = list(set(similar_films))
    print(f"Found {len(similar_films)} related films.")

    # Check for any duplicates in similar_films
    for film_id in id_list:
        if film_id in similar_films:
            similar_films.remove(film_id)

    print("Getting main subjects of related films...")
    records = get_main_subjects(similar_films)
    all_main_subjects = main_subjects_reference 
    for record in records:
        all_main_subjects += record["main_subjects"]
    all_main_subjects = list(set(all_main_subjects))

    embeddings_dict = dict(zip(all_main_subjects, get_embedding(all_main_subjects)))
    reference_embeddings = [embeddings_dict[subject] for subject in main_subjects_reference]

    print("Embedding main subjects of related films and calculating similarity...")
    for record in records:
        main_subjects = record["main_subjects"]
        if main_subjects:
            try:    
                record["similarity"] = average_vector_similarity(reference_embeddings, [embeddings_dict[subject] for subject in main_subjects])
            except Exception as e:
                logging.error(e)
                logging.error(record)
                record["similarity"] = 0
        else:
            record["similarity"] = 0

    records = sorted(records, key=lambda x: x["similarity"], reverse=True)[:nb_films]
    films = [get_displaying_data(record["film_id"]) for record in records]
    for i in range(len(films)):
        films[i]["similarity"] = records[i]["similarity"]
    return films


# Load films from the binary file
loaded_films = load_films_from_binary_file("data/films_data.bin")

# Initialize session state (list of ids)
if "list_ids" not in st.session_state:
    st.session_state.list_ids = []

# Streamlit app
st.title('Movie Recomendation App')

# One tab for search engine and another for recomendations
tab1, tab2 = st.tabs(["Search Movie", "Recomendations"])

#Side bar "My List"

st.sidebar.title("My List")
st.sidebar.write("Here are the movies you've added to your list:")

id_list = st.session_state.list_ids
film_titles_dict = {film["idwikidata"]: film["title"] for film in loaded_films}
film_titles = [film_titles_dict[id] for id in id_list]
checkboxes_variables = {}
for title in film_titles:
    checkboxes_variables[title] = st.sidebar.checkbox(title, False, key=title)
if st.sidebar.button("Remove selected films"):
    id_list = [id for id in id_list if not checkboxes_variables[film_titles_dict[id]]]
    st.session_state.list_ids = id_list
    st.sidebar.write("Removed from your list!")
    #force the sidebar to update
    st.rerun()


with tab1:
    st.header("Search Movie")
    search_term = st.text_input('Enter movie title:')
    if search_term:
        results = fuzzy_search_title(loaded_films, search_term)
        if(len(results)>0):
            st.header("Top 5 Search Results")          
            for i in range(len(results)):
                col1, col2 = st.columns([1,4])
                with col1:
                    # Display movie poster              
                    if(results[i]['image'] is not None):
                        st.image(results[i]['image'], caption=results[i]['title'], use_column_width=True)
                    else:
                        # If there is no movie poster, use custom movie poster  
                        st.image(r"data/film-solid.png")               

                with col2:  
                    # Display movie details
                    markdown_msg = f"### {results[i]['title']}\n"
                    markdown_msg += f"*<font color=gray size=2>Score: {results[i]['score']}</font>*<br>"
                    markdown_msg += f"**Release Year:** {results[i]['year']}<br>"
                    markdown_msg += f"**Director:** {results[i]['director']}\n"
                    st.markdown(markdown_msg, unsafe_allow_html=True)
                    if results[i]['idwikidata'] not in id_list:
                        # Add button to select movie
                        if st.button('Add to my list', key="add_"+results[i]['idwikidata']):
                            # Append idwikidata to id_list in session_state
                            id_list.append(results[i]['idwikidata'])
                            st.rerun()
                    else:
                        st.write("Added to your list!")
                st.divider()   

with tab2:
    st.header("Recomendations")
    nb_films = st.selectbox("Number of films to recomend", [5, 10, 15, 20], index=0)
    if st.button("Get recomendations"):
        if len(id_list) > 0:
            recomendations = get_recommended_films(id_list, nb_films)
            st.header(f"Top {nb_films} Recomendations")
            for i in range(len(recomendations)):
                if recomendations[i]:
                    col1, col2 = st.columns([1,4])
                    with col1:
                        # Display movie poster
                        if(recomendations[i]['image'] is not None):
                            st.image(recomendations[i]['image'], caption=recomendations[i]['title'], use_column_width=True)
                        else:
                            # If there is no movie poster, use custom movie poster
                            st.image(r"data/film-solid.png")               

                    with col2:
                        # Display movie details
                        markdown_msg = f"### {recomendations[i]['title']}\n"
                        markdown_msg += f"*<font color=gray size=2>Similarity: {recomendations[i]['similarity']}</font>*<br>"
                        markdown_msg += f"**Release Year:** {recomendations[i]['year']}<br>"
                        markdown_msg += f"**Director:** {recomendations[i]['director']}\n"
                        st.markdown(markdown_msg, unsafe_allow_html=True)
                    st.divider()

