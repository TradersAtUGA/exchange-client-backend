import quickfix as fix
import broker.initiator as init

from dotenv import load_dotenv
import os
load_dotenv()

def create_fix_server(): 
    """
    Creates a new quickfix broker side server, should only be called
    once. Call start on the returned object to start the server and 
    call stop to stop the server. 
    
    :return: quickfix server initiator, application 
    :rtype: Application
    """
    settings = fix.SessionSettings(os.getenv("EXCHANGE_CONFIG_FILE_PATH"))
    app = init.Application()
    store = fix.FileStoreFactory(settings)
    log = fix.FileLogFactory(settings)
    initiator = fix.SocketInitiator(app, store, settings, log)
    return app, initiator


