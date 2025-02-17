from threading import Thread
from time import sleep
from customisedLogs import CustomisedLogs
from pooledMySQL import PooledMySQL


from Hidden.Secrets import DBSecrets


class DBHolder:
    def __init__(self, logger:CustomisedLogs):
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
                mysqlPool = PooledMySQL(user=DBSecrets.DBUser, password=DBSecrets.DBPassword, dbName=DBSecrets.DBName, host=host)
                mysqlPool.execute("SHOW DATABASES", dbRequired=False, catchErrors=False)
                logger.log(logger.Colors.green_800, "DB", f"connected to: {host}")
                self.db=mysqlPool
                return
            except:
                logger.log(logger.Colors.red_500, "DB", f"failed: {host}")
        else:
            logger.log(logger.Colors.red_800, "DB", "Unable to connect to DataBase")
            input("EXIT...")
            exit(0)


    def __initialise(self):
        """
        Initialise DB when called for
        :return:
        """
        if self.initialised: return
        self.__connect(self.logger)
        self.initialised = True


    def useDB(self):
        """
        Waits till DB preparation and then executes DB commands
        :return:
        """
        while not self.initialised: sleep(1)
        return self.db

