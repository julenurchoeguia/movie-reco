from SPARQLWrapper import SPARQLWrapper, JSON
import pickle

#current path print

def query_films_from_wikidata():
    print("Querying films from Wikidata...")
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
        SELECT DISTINCT ?item ?title ?year ?director ?image ?idwikidata WHERE {
            ?item wdt:P31 wd:Q11424.
            ?item wdt:P1476 ?title. 
            OPTIONAL { ?item wdt:P577 ?date. BIND(YEAR(?date) AS ?year) }
            OPTIONAL { ?item wdt:P57 ?director_item. ?director_item rdfs:label ?director. FILTER(LANG(?director) = "en") }
            OPTIONAL { ?item wdt:P18 ?image }
            BIND(REPLACE(STR(?item), ".*Q", "Q") AS ?idwikidata)
            FILTER(LANG(?title) = "en")
        }
        LIMIT 1000000
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    films = []
    print("Processing results...")
    for result in results["results"]["bindings"]:
        film = {
            "title": result["title"]["value"],
            "year": result.get("year", {}).get("value"),
            "director": result.get("director", {}).get("value", ""),
            "image": result.get("image", {}).get("value", "") if "image" in result else None,
            "idwikidata": result["idwikidata"]["value"]
        }
        current_ids = [f["idwikidata"] for f in films]
        if film["idwikidata"] not in current_ids:
            films.append(film)
        else:
            index = current_ids.index(film["idwikidata"])
            try:
                if film["director"] and film["director"] not in films[index]["director"]:
                    films[index]["director"] += ", " + film["director"]
                if film["year"] and film["year"] not in films[index]["year"]:
                    films[index]["year"] = min(films[index]["year"], film["year"])
            except Exception as e:
                print(e)
                print(film)
                print(index)

    return films

def store_films_to_binary_file(films, filename):
    print("Storing films to binary file...")
    with open(filename, 'wb') as f:
        pickle.dump(films, f)

# Query films from Wikidata
films = query_films_from_wikidata()

# Store the results in a binary file
store_films_to_binary_file(films, "data/films_data.bin")
