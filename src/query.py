from SPARQLWrapper import SPARQLWrapper, JSON


def get_main_subjects(film_ids):
    endpoint_url = "https://query.wikidata.org/sparql"
    
    main_subjects = []
    
    for film_id in film_ids:
        # SPARQL query to get main subjects of a film
        query = f"""
        SELECT DISTINCT ?mainSubjectLabel
        WHERE {{
          wd:{film_id} wdt:P921 ?mainSubject.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        """
        
        # Set up SPARQL query and execute it
        sparql = SPARQLWrapper(endpoint_url)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        # Extract main subjects and add them to the main_subjects list
        subjects = {
            "film_id":film_id, 
            "main_subjects": [result['mainSubjectLabel']['value'] for result in results['results']['bindings']]
        }
        main_subjects.append(subjects)
    
    return main_subjects

def get_related_films(wikidata_id):
  endpoint_url = "https://query.wikidata.org/sparql"
    
  # SPARQL query to get films based on the specified rules
  query = f"""
  SELECT DISTINCT ?z
  WHERE {{
      {{
        ?x wdt:P136 ?genre.
        ?z wdt:P136 ?genre.
        ?z wdt:P31 wd:Q11424.
        
        ?x wdt:P577 ?publicationDateX.
        ?z wdt:P577 ?publicationDateZ.
        FILTER(?publicationDateZ >= ?publicationDateX - 10 && ?publicationDateZ <= ?publicationDateX + 10)
        FILTER(?x != ?z)
      }}
      UNION
      {{
        ?x wdt:P57 ?director.
        ?z wdt:P57 ?director.
        ?z wdt:P31 wd:Q11424.

        FILTER(?x != ?z)
      }}
      UNION
      {{
        ?x wdt:P921 ?mainSubject.
        ?z wdt:P921 ?mainSubject.
        ?z wdt:P31 wd:Q11424.
        
        FILTER(?publicationDateZ >= ?publicationDateX - 10 && ?publicationDateZ <= ?publicationDateX + 10)
        FILTER(?x != ?z)
      }}

    VALUES ?x {{ wd:{wikidata_id} }}
  }}
  """

    
  # Set up SPARQL query and execute it
  sparql = SPARQLWrapper(endpoint_url)
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  
  # Extract and return the list of related film IDs
  related_films = [result['z']['value'].split('/')[-1] for result in results['results']['bindings']]
  return related_films

def get_displaying_data(wikidata_id):
    
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery(f"""
        SELECT ?item ?title ?year ?director ?image ?idwikidata 
        WHERE {{
            ?item wdt:P31 wd:Q11424.
            ?item wdt:P1476 ?title. 
            OPTIONAL {{ ?item wdt:P577 ?date. BIND(YEAR(?date) AS ?year) }}
            OPTIONAL {{ ?item wdt:P57 ?director_item. ?director_item rdfs:label ?director. FILTER(LANG(?director) = "en") }}
            OPTIONAL {{ ?item wdt:P18 ?image }}
            BIND(REPLACE(STR(?item), ".*Q", "Q") AS ?idwikidata)
            FILTER(LANG(?title) = "en")
        }}
        VALUES ?item {{ wd:{wikidata_id} }}
    """)

    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()["results"]["bindings"][0]
  
    film = {
        "title": result["title"]["value"],
        "year": result.get("year", {}).get("value"),
        "director": result.get("director", {}).get("value", ""),
        "image": result.get("image", {}).get("value", "") if "image" in result else None,
        "idwikidata": result["idwikidata"]["value"]
    }
    return film

if __name__ == "__main__":

    print(get_displaying_data("Q25188"))
