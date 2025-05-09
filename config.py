from configparser import ConfigParser
import os

def config(filename='database.ini', section='postgresql'):
    # Create a parser
    parser = ConfigParser()

    filepath = os.path.join(os.path.dirname(__file__), filename)

    parser.read(filepath)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')

    return db
