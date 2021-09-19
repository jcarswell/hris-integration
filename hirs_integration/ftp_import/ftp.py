from hirs_integration.smtp_client.exceptions.errors import ConfigError
import logging
import paramiko
import re
import time

from django import conf
from tempfile import TemporaryFile
from hirs_integration.smtp_client.smtp import Smtp

from .helpers import config
from .helpers.stats import Stats
from .helpers.text_utils import int_or_str
from .exceptions import ConfigurationError,SFTPIOError
from .models import FileTrack
from .csv import CsvImport
from hirs_integration.smtp_client import SmtpToInvalid,SmtpClientConfig,SmtpServerError

logger = logging.getLogger('ftp.FTPClient')

class FTPClient:
    """
    FTP client interface. Initalizing the class will setup the connection and start the
    to the connection to the configured server. This class is not directly configurable,
    everything must be setup in the web interface via the hirs_admin frontend module.
    Currently this module only implements FTP Support
    """
    def __init__(self) -> None:
        """
        Initalizing the class will setup and start the connection to the configured server.
        
        Raises:
            ConfigurationError: configured protocol is not supported.
        """

        self.server = config.get_config(config.CAT_SERVER,config.SERVER_SERVER)
        self.port = config.get_config(config.CAT_SERVER,config.SERVER_PORT)
        self.user = config.get_config(config.CAT_SERVER,config.SERVER_USER)
        basepath = config.get_config(config.CAT_SERVER,config.SERVER_PATH)
        file_expr = config.get_config(config.CAT_SERVER,config.SERVER_FILE_EXP)
        protocol = config.get_config(config.CAT_SERVER,config.SERVER_PROTOCAL)
        self.__password = config.get_config(config.CAT_SERVER,config.SERVER_PASSWORD)
        Stats.time_start = time.time()
        
        self.file_expr = re.compile(file_expr)
        self.basepath = ''

        for char in basepath:
            if char == '\\':
                self.basepath += '/'
            else:
                self.basepath += char

        if not self.basepath[-1] == '/':
            self.basepath += '/'

        try:
            self.port = int_or_str(self.port)
        except ValueError:
            self.port = 22
            
        if protocol.lower() != 'sftp':
            logger.fatal(f"unsupported protocol specified {protocol}")
            raise ConfigurationError("currently only SFTP is supported")

        else:
            self.connect()


    def connect(self):
        """
        Creates the connection to the server and ensures that we can access files
        that are stored in the configured base path.

        Raises:
            ConfigurationError: Invalid username or password configured
            SFTPIOError: Base path is not readable or does not exist
        """

        logger.info(f"Connecting to {self.server}")
        paramiko.util.log_to_file(str(conf.settings.LOG_DIR) + '\\ftp_client.log')
        
        self.sock = paramiko.Transport((self.server, self.port))
        try:
            self.sock.connect(username=self.user,password=self.__password)
            self.sftp = paramiko.SFTPClient.from_transport(self.sock)
            logger.info(f"Connected to {self.server}")
        except paramiko.SSHException as e:
            logger.fatal("Failed to connecto to the server, invalid private key or username/password")
            self.sock.close()
            raise ConfigurationError(e.message) from e
        
        try:
            _ = self.sftp.listdir(self.basepath)
        except IOError as e:
            logger.fatal(f"Base Path {self.basepath} does not exists or is not readable")
            logger.info(f"shutting down server connection")
            self.sftp.close()
            self.sock.close()

            raise SFTPIOError("Configured base path is not accessable")

    def close(self):
        """Close the server connection and client socket"""

        logger.info("Closing the connection to the server")
        self.sftp.close()
        self.sock.close()
    
    def __del__(self):
        """Call the close method prior to deleting"""
        del self.__password
        del self.user
        self.close()
    
    def run_import(self):
        """Get all new files based on the configuration and imports them"""

        logger.warning("Starting ftp import cycle")
        path = self.sftp.listdir(self.basepath)
        
        for f in path:
            logger.debug(f"Got file {f} for checking")
            m = re.search(self.file_expr,f)
            if m and not FileTrack.objects.filter(name=f).exists():
                logger.debug(f"Importing {f}")
                Stats.files.append(f)
                
                with TemporaryFile() as fh:
                    self.sftp.getfo(self.basepath+f,fh)
                    fh.seek(0)
                    logger.debug(f"header row of file should be {fh.readline(80)}")
                    CsvImport(fh)
                ft = FileTrack()
                ft.name=f
                ft.save()
                del ft

        logger.info(f"Finished running import.")
        Stats.time_end = time.time()
        logger.info(str(Stats()))
        if Stats.errors:
            logger.error("Errors:\n\t" + "\n\t".join(Stats.errors))

        try:
            to = config.get_config(config.CAT_CSV,config.CSV_FAIL_NOTIF).split(',')
            if to:
                s = Smtp()
                s.send(to,Stats().as_html,"FTP Import Job")
        except SmtpToInvalid as e:
            logger.warning(str(e))
        except SmtpServerError:
            logger.error("Please review the SMTP server configuration")
        except ConfigError:
            logger.error("Please double check the configured SMTP Credentials")
        