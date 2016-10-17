import json

def is_valid_json(data):
    try:
        json.dumps(data)
        return True
    except Exception as e:
        msg = """Whoops. The data you're trying to send could not be
converted into JSON. If the data you're attempting to send includes a numpy
array, try casting it to a list (x.tolist()), or consider structuring your data
as a pandas DataFrame. If you're still having trouble, please contact:
{URL}.""".format(URL="support@yhathq.com")
        print(msg)
        return False


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def create_tests(df, output_file, columns=None):
    """
    Creates ScienceOps compatible (JSON Line Format) smoke test files from your dataframes.
    Once created, these files can be uploaded directly to your model via ScienceOps --> '/models/{model}/unit-tests'

    Parameters
    ----------
    df: dataframe
        the dataframe you wish to pull test inputs from
    output_file: string
        the name you will give your exported test file
    columns: array of strings
        the columns in your df which will be made into inputs

    Example
    -------
    Let's say you've built a book recommender model that takes 2 inputs - title & page count:

    from yhat.utils import create_tests
    books =  pd.read_csv('./book_data.csv')
    create_tests(books, "book_model_inputs.ldjson", columns=["title","pages"])
    * That's it! *
    --> book_model_inputs.ldjson {"title":"harry potter","pages":"800"}\\n{"title":"war and peace","pages":"875"}\\n{"title":"lord of the rings","pages":"500"}

      """
    # if the user doesn't specify columns, then we'll assume they want them all!
    if columns is None:
        columns = df.columns
    with open(output_file, "wb") as f:
        for _, row in df[columns].iterrows():
            f.write(row.to_json() + '\n')
