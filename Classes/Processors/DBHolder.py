from threading import Thread
from time import sleep
from customisedLogs import CustomisedLogs
from pooledMySQL import PooledMySQL


from Hidden.Secrets import DBSecrets


class DBHolder:
    def __init__(self, logger:CustomisedLogs):
        """
        Fetches secrets for DB and connects using pooledMySQL
        :param logger: instance of customisedLogger
        """
        self.db:None|PooledMySQL = None
        self.logger:None|CustomisedLogs = logger
        self.initialised = False
        Thread(target=self.__initialise).start()


    def __connect(self, logger: CustomisedLogs) -> None:
        """
        Blocking function to connect to DB
        :return: None
        """
        for host in DBSecrets.DBHosts:
            try:
                pool = PooledMySQL(user=DBSecrets.DBUser, password=DBSecrets.DBPassword, dbName=DBSecrets.DBName, host=host)
                pool.execute("SHOW DATABASES", dbRequired=False, catchErrors=False)
                logger.log(logger.Colors.green_800, "DB", f"connected to: {host}")
                self.db=pool
                return
            except:
                logger.log(logger.Colors.red_500, "DB", f"failed: {host}")
        else:
            logger.log(logger.Colors.red_800, "DB", "Unable to connect to DataBase")
            input("EXIT...")
            exit(0)


    def __initialise(self) -> None:
        """
        Initialise DB when called for
        :return:
        """
        if self.initialised: return
        self.__connect(self.logger)
        self.initialised = True


    def useDB(self) -> PooledMySQL:
        """
        Waits till DB preparation and then returns the pool
        :return:
        """
        while not self.initialised: sleep(1)
        return self.db

