__author__ = 'tonycastronova'

from engineManager import Engine
from threading import Thread


def addModel(id=None, attrib=None):
    e = Engine()
    kwargs = dict(attrib=attrib, id=id, event='onModelAdded')
    task = [('add_model', kwargs)]
    e.setTasks(task)

    e.thread = Thread(target=e.check_for_process_results)
    e.thread.start()


def addLink(source_id=None, source_item=None, target_id=None, target_item=None, spatial_interpolation=None,
            temporal_interpolation=None):
    e = Engine()
    kwargs = dict(from_id=source_id, from_item_id=source_item, to_id=target_id, to_item_id=target_item,
                  spatial_interp=spatial_interpolation, temporal_interp=temporal_interpolation)
    task = [('add_link', kwargs)]
    e.setTasks(task)

    result = e.processTasks()
    return result

    # e.thread = Thread(target = e.check_for_process_results)
    # e.thread.start()

def getDbConnections():
    e = Engine()
    kwargs = dict()
    task = [('get_db_connections',kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def getDefaultDb():
    e = Engine()
    kwargs = dict()
    task = [('get_default_db',kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result


def removeModelById(modelid):
    e = Engine()
    kwargs = dict(id=modelid)
    task = [('remove_model_by_id',kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def clearAll():
    """
    Clears all the models and links in the configuration
    :return: True on success
    """
    e = Engine()
    kwargs = dict()
    task = [('clear_all',kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def getModelById(modelid):
    e = Engine()
    kwargs = dict(id=modelid)
    task = [('get_model_by_id_summary', kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def getOutputExchangeItems(modelid):
    e = Engine()
    kwargs = dict(id=modelid)
    task = [('get_output_exchange_items_summary', kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def getInputExchangeItems(modelid):
    e = Engine()
    kwargs = dict(id=modelid)
    task = [('get_input_exchange_items_summary', kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

def getLinksBtwnModels(from_model_id, to_model_id):
    e = Engine()
    kwargs = dict(from_model_id=from_model_id, to_model_id=to_model_id)
    task = [('get_links_btwn_models', kwargs)]
    e.setTasks(task)
    result = e.processTasks()
    return result

# def getLinkById():
#     e = Engine()
#     kwargs = dict()
#     task = [('get_link_by_id',kwargs)]
#     e.setTasks(task)
#     result = e.processTasks()
#     return result
#
# getLinkById (id)
# get_links_btwn_models


# def connectToDbFromFile(filepath):
#     e = Engine()
#     kwargs = dict(filepath=filepath)
#     task = [('connect_to_db_from_file',kwargs)]
#     e.setTasks(task)
#
#     e.thread = Thread(target = e.check_for_process_results)
#     e.thread.start()