import re
import uvicorn
from fastapi import FastAPI
from fastapi import HTTPException
import psycopg2 as db2
import pandas as pd


description = """Test task for Okkam.
                By: S. Minakov"""

tags_metadata = [{
                    "name": "getPercentage",
                    "description": "Operation with data in Postgresql DB to calc percentages for 2 groups of audience",
                }]

app = FastAPI(title="Test task",
                description=description,
                summary="Calculating percentages",
                version="0.0.1",
                contact={
                    "name": "Sergei Minakov",
                    "email": "minakov.duck@gmail.com",
                },
                openapi_tags=tags_metadata)
conn_string = "dbname='postgres' user='postgres' host='app-db-local' password='mysecretpassword'"


def _get_avg_from_sql(condition: str) -> pd.DataFrame:
    """
    Method to utilize psycopg2 to select avg from SQL DB based on passed conditions parameter
    :param condition: Condition for filtering out the data in SQL
    :return: Pandas DataFrame with columns: "respondent", "weight"
    """
    try:
        exec_string = f"""SELECT respondent, avg(weight)
                            FROM respondents where respondent in 
                            (select distinct respondent from respondents where {condition}) 
                            group by respondent;"""
        conn = db2.connect(conn_string)
        cur = conn.cursor()
        query_tuple = ()
        cur.execute(exec_string, query_tuple)
        ret_fetch = cur.fetchall()
    except Exception as e:
        print(f"During processing of the parameter [{condition}] encountered following exception: [{e}]")
        return pd.DataFrame([], columns=["respondent", "weight"])
    if ret_fetch:
        return pd.DataFrame(ret_fetch, columns=["respondent", "weight"])
    return pd.DataFrame([], columns=["respondent", "weight"])


@app.get("/getPercent", tags=["getPercentage"])
def getPercent(audience1: str, audience2: str) -> dict:
    """
    Endpoint to calculate percentage of audience1 and audience2 crossover
    :param audience1: conditions for filtering of the first audience
    :param audience2: conditions for filtering the second audience
    :returns: dictionary {"percent": result}
    :raises: HTTPException
    """
    # Basic check if we actually receive 2 parameters:
    if not audience1 or not audience2:
        raise HTTPException(status_code=400, detail="Please provide 2 parameters: audience1 and audience2")

    # receiving parts of SQL syntax is unsafe and should be handled better.
    # But this is a basic safeguard against injections:
    pattern = re.compile(r"^(?!.*\-\-)(?!.*\/\*)(?!.*\*\/)(?!.*;)(?!.*CREATE)(?!.*DROP)(?!.*ALTER)(?!.*UPDATE)(?!.*DELETE).*$", re.I)
    if not re.search(pattern, audience1) or not re.search(pattern, audience2):
        raise HTTPException(status_code=400, detail="Unexpected string received")

    # get the first audience average:
    first_audience = _get_avg_from_sql(audience1)

    if len(first_audience) == 0:
        raise HTTPException(status_code=404, detail=f"Did not find anyone with parameters [{audience1}]")

    # getting the second audience average:
    second_audience = _get_avg_from_sql(audience2)
    if len(second_audience) == 0:
        raise HTTPException(status_code=404, detail=f"Did not find anyone with parameters [{audience2}]")
    
    # get intersection
    intersection = pd.merge(first_audience, second_audience, 
                             how='left', 
                             on=["respondent"], 
                             suffixes=("_aud1", "_aud2"))

    # counting the final
    result = intersection["weight_aud2"].sum()/intersection["weight_aud1"].sum()
    if result == 0:
        {"percent": 0}
    return {"percent": result}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, log_level="debug")
