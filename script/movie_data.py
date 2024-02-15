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
        LIMIT 10000
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    films = []
    print("Processing results...")
    for result in results["results"]["bindings"]:
        film = {
            "title": result["title"]["value"],
            "year": result.get("year", {}).get("value"),
            "director": result.get("director", {}).get("value") if "director" in result else None,
            "image": result.get("image", {}).get("value") if "image" in result else None,
            "idwikidata": result["idwikidata"]["value"]
        }
        if film["idwikidata"] not in [f["idwikidata"] for f in films]:
            films.append(film)
        else:
            index = next((i for i, f in enumerate(films) if f["idwikidata"] == film["idwikidata"]), None)
            if film["director"] and film["director"] not in films[index]["director"]:
                films[index]["director"] += ", " + film["director"]
            if film["year"] and film["year"] not in films[index]["year"]:
                films[index]["year"] = min(films[index]["year"], film["year"])

    return films

def store_films_to_binary_file(films, filename):
    print("Storing films to binary file...")
    with open(filename, 'wb') as f:
        pickle.dump(films, f)

# Query films from Wikidata
films = query_films_from_wikidata()

# Store the results in a binary file
store_films_to_binary_file(films, "data/films_data.bin")
