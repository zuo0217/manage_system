# from mysql.connector import connect
#
# doThing = 1

from MySQLdb import connect

doThing = 2


class ConnectDB():
    """
    Used setDefault setup parameter for DB connect
    """

    def __init__(self):
        self.config = {}
        self.default = False
        self.connect = None

    def setDefault(self, **kwargs):
        self.config["host"] = kwargs.get("host", "127.0.0.1")
        self.config["port"] = kwargs.get("port", "3306")
        self.config["database"] = kwargs.get("database", False)
        self.config["charset"] = kwargs.get("charset", "utf8")
        self.config["user"] = kwargs.get("username", False)
        self.config["password"] = kwargs.get("password", False)
        status = [x for x in self.config.values() if x is False]
        if not status:
            self.default = True

    def mysql_db(self):
        if self.default:
            self.config["port"] = int(self.config["port"])
            self.config["db"] = self.config.pop("database")
            self.config["passwd"] = self.config.pop("password")

    def _connect_(self, times=3):
        """
        :param times:   连接次数
        :return:        返回连接状态
        """
        if self.default:
            for i in range(times):
                try:
                    if doThing == 1:
                        """使用模块 mysql.connector"""
                        # self.config["allowNativePasswords"] = True
                        self.connect = connect(**self.config)  # mysql.connector

                    elif doThing == 2:
                        """使用模块 MySQLdb"""
                        self.mysql_db()
                        self.connect = connect(**self.config)  # MySQLdb
                    else:
                        return False

                    return True
                except Exception as e:
                    print(e)
                    if i + 1 == times:
                        return False
        else:
            return False

    def create(self, name, sql=None):
        """
        :param name:   表名称
        :param sql:    使用SQL语言建表
        :return:       返回状态
        """
        state = False
        if self._connect_():
            cursor = self.connect.cursor()
            sql_table = "CREATE TABLE IF NOT EXISTS {} (`id` int(50) NOT NULL AUTO_INCREMENT," \
                        "`name` varchar(100) DEFAULT NULL," \
                        "`id_number` varchar(18) DEFAULT NULL," \
                        "PRIMARY KEY (`id`))ENGINE=MyISAM DEFAULT CHARSET=utf8".format(name)
            if sql is not None:
                sql_table = sql
            try:
                cursor.execute(sql_table)
                self.connect.commit()
                state = True
            except:
                state = False
            finally:
                self.connect.close()
                return state
        else:
            print("Connect Error.")
            return False

    def insert(self, name, info, listInsert=False):
        if self._connect_():
            if listInsert is False:
                cursor = self.connect.cursor()
                sql_insert = "INSERT INTO {} ({}) values{}".format(name,
                                                                   ",".join(["`{}`".format(x) for x in info.keys()]),
                                                                   tuple(info.values()))
                try:
                    cursor.execute(sql_insert, ())
                    self.connect.commit()
                    self.connect.close()
                    return True
                except:
                    print("ERROR: {}".format(sql_insert))
                    self.connect.close()
                    return False
            else:
                cursor = self.connect.cursor()
                for i in info:
                    sql_insert = "INSERT INTO {} ({}) values{}".format(name,
                                                                       ",".join(["`{}`".format(x) for x in i.keys()]),
                                                                       tuple(i.values()))
                    try:
                        cursor.execute(sql_insert, ())
                    except:
                        print("ERROR: {}".format(sql_insert))
                        continue
                self.connect.commit()
                self.connect.close()
        else:
            print("Connect Error.")
            return False

    def search(self, name, info={}):
        if self._connect_():
            cursor = self.connect.cursor()
            all = "SELECT * FROM {}".format(name)
            tmp = []
            for i in info.keys():
                tmp.append("`{}` = \"{}\"".format(i, info[i]))
            if tmp:
                sql_search = "".join([all, " WHERE {}".format(" and ".join(tmp))])
            else:
                sql_search = all
            try:
                cursor.execute(sql_search)
                for i in cursor:
                    yield i
            except:
                return False
            finally:
                self.connect.close()
        else:
            print("Connect Error.")
            return False

    def delete(self, name, info={}):
        if self._connect_():
            cursor = self.connect.cursor()
            if not info:
                sql_delete = "DROP TABLE {}".format(name)
            else:
                tmp = []
                for i in info.keys():
                    tmp.append("{} = \"{}\"".format(i, info[i]))
                sql_delete = "DELETE FROM {} WHERE {}".format(name, " and ".join(tmp))
            try:
                cursor.execute(sql_delete)
                self.connect.commit()
                self.connect.close()
                return True
            except:
                self.connect.close()
                return False
        else:
            print("Connect Error.")
            return False

    def update(self, name, source, target):
        if self._connect_():
            cursor = self.connect.cursor()
            tmp = []
            ted = []
            for i in source.keys():
                tmp.append("{} = \"{}\"".format(i, source[i]))
            for l in target.keys():
                ted.append("{} = \"{}\"".format(l, target[l]))

            sql_update = "UPDATE {} SET {} WHERE {}".format(name, ", ".join(ted), " and ".join(tmp))
            try:
                cursor.execute(sql_update)
                self.connect.commit()
                self.connect.close()
                return True
            except:
                self.connect.rollback()
                self.connect.close()
                return False
        else:
            print("Connect Error.")
            return False

    def query(self, sql, get=False, commit=False):
        """
        :param sql:     SQL语句
        :param get:     get 是否返回查询信息   默认 False [one / all]
        :param commit:  commit在创建表时用
        :return:
        """
        if self._connect_():
            cursor = self.connect.cursor()
            try:
                cursor.execute(sql)

                if commit is True:
                    self.connect.commit()

                if get is not False:
                    if get == "all":
                        """返回所有行"""
                        return cursor.fetchall()
                    elif get == "one":
                        """返回一行"""
                        return cursor.fetchone()
                    else:
                        """返回行数"""
                        return len(cursor.fetchall())
                self.connect.close()
                return True
            except:
                self.connect.close()
                return False
        else:
            print("Connect Error.")
            return False

    def filter(self, name, value, keys=None, REGEXP=False, QTY="one"):
        """
        :param name:      表名称
        :param value:     匹配信息
        :param keys:      列信息
        :param REGEXP:    是否使用正则匹配 / 默认不使用
        :param QTY:       返回信息   [all / one / *]
        :return:          返回
        """
        if REGEXP is True:
            format_ = "REGEXP"
        else:
            format_ = "LIKE"

        if keys is None:
            return False

        elif type(keys) is str:
            sql_filter = "SELECT * FROM {} WHERE {} {} \"{}\"".format(name, keys, format_, value)

        elif type(keys) is list:
            tmp = []
            for i in keys:
                tmp.append("{} {} \"{}\"".format(i, format_, value))
            sql_filter = "SELECT * FROM {} WHERE {}".format(name, " or ".join(tmp))

        else:
            sql_filter = "SELECT * FROM {}".format(name)

        if self._connect_():
            cursor = self.connect.cursor()

            try:
                cursor.execute(sql_filter)
                if QTY == "one":
                    return cursor.fetchone()
                elif QTY == "all":
                    return cursor.fetchall()
                else:
                    return len(cursor.fetchall())
            except:
                self.connect.close()
                return False

    def tryConnect(self):
        if self._connect_():
            print("数据库连接成功.")
        else:
            print("数据库连接失败.")


if __name__ == "__main__":
    con = ConnectDB()
    con.setDefault(host="101.200.55.217", database="FANG", username="root", password="root123")
    print(con.query(sql="show databases", get="all"))
