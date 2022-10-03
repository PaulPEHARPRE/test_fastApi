from sqlalchemy import inspect

def object_as_dict(objArray):
    dictArray = []
    for object in objArray: 
        dictArray.append(object.__dict__)
    return dictArray