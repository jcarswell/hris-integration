import logging
import paramiko
import re

from django import conf
from tempfile import TemporaryFile

from .helpers import settings
from .helpers.text_utils import int_or_str
from .exceptions import ConfigurationError
from .models import FileTrack
from .csv import CsvImport

logger = logging.getLogger('ftp.FTPClient')

class FTPClient:
    
    def __init__(self) -> None:
        self.server = settings.get_config(settings.SERVER_CONFIG,'server')
        self.port = settings.get_config(settings.SERVER_CONFIG,'port')
        self.user = settings.get_config(settings.SERVER_CONFIG,'user')
        self.basepath = settings.get_config(settings.SERVER_CONFIG,'base_path')
        file_expr = settings.get_config(settings.SERVER_CONFIG,'file_name_expression')
        protocol = settings.get_config(settings.SERVER_CONFIG,'protocal')
        self.__password = settings.get_config(settings.SERVER_CONFIG,'password')
        
        self.file_expr = re.compile(file_expr)
        
        try:
            self.port = int_or_str(self.port)
        except ValueError:
            self.port = 22
            
        if protocol.lower != 'sftp':
            logger.fatal(f"unsupported protocol specified {protocol}")
            raise ConfigurationError("currently only SFTP is supported")

        else:
            self.connect()


    def connect(self):
        logger.info(f"Connecting to {self.server}")
        paramiko.util.log_to_file(conf.settings['LOG_DIR'] + '\\ftp_client.log')
        
        self.sock = paramiko.Transport((self.server, self.port))
        try:
            self.sock.connect(None,self.__user,self.__password)
            self.sftp = paramiko.SFTPClient.from_transport(self.sock)
            logger.info(f"Connected to {self.server} - {self.sftp}")
        except paramiko.SSHException as e:
            logger.fatal("Failed to connecto to the server, invalid private key or username/password")
            self.sock.close()
            raise ConfigurationError(e.message) from e
        
        try:
            _ = self.sftp.listdir(self.basepath)
        except IOError:
            logger.fatal(f"Base Path {self.basepath} does not exists or is not readable")
            logger.info(f"shutting down server connection")
            self.sftp.close()
            self.sock.close()
    
    def close(self):
        logger.info("Closing the connection to the server")
        self.sftp.close()
        self.sock.close()
    
    def __del__(self):
        self.close()
    
    def run_import(self):
        logger.info("Starting ftp import cycle")
        path = self.sftp.listdir(self.basepath)
        imported = 0
        
        for f in path:
            logger.debug(f"Got file {f} for checking")
            m = re.search(self.file_expr,f)
            if m and not FileTrack.objects.exists(name=f):
                logger.info(f"Importing {f}")
                fh = self.sftp.getfo(self.basepath+f)
                CsvImport(fh)
                del fh

        logger.info(f"Finished running import. Imported {imported} files.")
                