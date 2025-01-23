import pandas_gbq
from config.settings import PROJECT_ID

def execute_query(query):
    try:
        return pandas_gbq.read_gbq(query, project_id=PROJECT_ID)
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'exécution de la requête : {e}")