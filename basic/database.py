#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : 数据库操作类，支持线程池、增删改查、统计等。
@FileName    : database.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.1
"""
import contextlib
from typing import Union, List

from basic.logger import Logger


class MySQLDatabase:
    def __init__(
            self,
            creator: object,
            *,
            host: str,
            port: int,
            username: str,
            password: str,
            database: str,
            charset: str = 'utf8mb4',
            collation: str = 'utf8mb4_general_ci',
            auto_commit: bool = True,
            cursor_class: type = None,
            init_command_list: List[str] = None,
            min_cached: int = 5,
            max_cached: int = 20,
            max_shared: int = 10,
            max_connections: int = 40,
            blocking: bool = True,
            max_usage: int = 0,
            reset: bool = True,
            multi_thread: bool = True,
            logger: Logger = None,
            **kwargs
    ) -> None:
        """
        数据库操作类 MySQLDatabase 的初始化参数一览表
        :param type creator:
            数据库连接池支持的任何符合DB-API 2.0规范的函数或者兼容的数据库模块，例如 MySQLdb (mysqlclient) 等
        :param str host:
            数据库连接的主机，默认值为 127.0.0.1
        :param int port:
            数据库连接的端口，默认值为 3306
        :param str username:
            数据库连接的用户名
        :param str password:
            数据库连接的密码
        :param str database:
            数据库连接的数据库名
        :param str charset:
            数据库连接的字符集，默认值为 utf8mb4
        :param str collation:
            数据库连接的排序规则，默认值为 utf8mb4_general_ci
            注：此选项仅在 mysql.connector 模块中生效
        :param bool auto_commit:
            数据库连接的自动提交开关，默认值为 True
        :param type|None cursor_class:
            数据库连接的默认游标类，例如 MySQLdb 的 Cursor SSCursor DictCursor SSDictCursor 类等
        :param List[str]|None init_command_list:
            数据库连接初始化时执行的命令列表，例如 ["set datestyle to ..."，"set time zone ..."] 等
        :param int min_cached:
            数据库连接池中空闲连接的初始数量，为 0 表示不创建，默认值为 3
            注：此选项仅在 multi_thread 为 True 时生效
        :param int max_cached:
            数据库连接池中空闲连接的最大数量，为 0 表示不限制，默认值为 12
            注：此选项仅在 multi_thread 为 True 时生效
        :param int max_shared:
            数据库连接池中共享连接的最大数量，为 0 表示不共享，默认值为 6
            注：此选项仅在 multi_thread 为 True 时生效
        :param int max_connections:
            数据库连接池中连接的最大数量，为 0 表示不限制，默认值为 24
            注：此选项仅在 multi_thread 为 True 时生效
        :param bool blocking:
            数据库连接池超过最大连接数量时的阻塞开关，阻塞则等待可用连接，不阻塞则直接抛出异常，默认值为 True
            注：此选项仅在 multi_thread 为 True 时生效
        :param int max_usage:
            数据库连接池中单个连接的最大复用次数，为 0 表示不限制，默认值为 0
        :param bool reset:
            数据库连接池中连接放回池中的重置开关，为 True 时表示所有连接都执行回滚操作，默认值 True
            注：此选项仅在 multi_thread 为 True 时生效
        :param bool multi_thread:
            是否多线程调用，多线程则用 PooledDB 模块，否则使用 PersistentDB 模块，默认值 True
        :param Logger logger:
            日志对象
        """
        # 初始化日志对象
        self._logger = logger or Logger('MySQLDatabase')

        # 生成数据库配置
        if creator.__name__ == 'MySQLdb':
            self._config = {
                'host': host, 'port': port,
                'user': username, 'passwd': password,
                'database': database, 'charset': charset,
                'autocommit': auto_commit,
            }
        elif creator.__name__ == 'mysql.connector':
            self._config = {
                'host': host, 'port': port,
                'user': username, 'password': password,
                'database': database, 'charset': charset, 'collation': collation,
                'autocommit': auto_commit,
            }
        else:
            raise ValueError('暂不支持的数据库接口')

        if cursor_class is not None:
            self._config['cursorclass'] = cursor_class

        # DBUtils 是一套 Python 数据库连接池包，并允许对非线程安全的数据库接口进行线程安全包装。
        # DBUtils 提供两种外部接口：
        #   - PersistentDB：提供线程专用的数据库连接，并自动管理连接。
        #   - PooledDB：提供线程间可共享的数据库连接，并自动管理连接。

        if multi_thread:
            # 用于数据库连接池 PooledDB
            # from DBUtils.PooledDB import PooledDB  # DBUtils 1.x
            from dbutils.pooled_db import PooledDB  # DBUtils 2.x
            self._pool = PooledDB(
                creator, min_cached, max_cached, max_shared, max_connections, blocking, max_usage, init_command_list,
                reset,
                **self._config, **kwargs
            )
        else:
            # 用于数据库连接池 PersistentDB
            # from DBUtils.PersistentDB import PersistentDB  # DBUtils 1.x
            from dbutils.persistent_db import PersistentDB  # DBUtils 2.x
            self._pool = PersistentDB(
                creator, max_usage, init_command_list,
                **self._config, **kwargs
            )

        # 辅助函数（s -> 字符串）（x -> 元组）（sy -> 占位符）（sp -> 间隔符）
        self._wrapper = lambda s, sy='`%s`': sy % s  # 'test' -> '`test`'
        self._placeholder = lambda x, sy='%s', sp=', ': sp.join([sy] * len(x))  # '(1, 2)' -> '%s, %s'
        self._placeholder_plus = lambda x, sy='`%s`', sp=', ': (sp.join([sy] * len(x)) % x)  # '(1, 2)' -> '`%s`, `%s`'

    @contextlib.contextmanager
    def execute(
            self, operation: str,
            *,
            params: Union[dict, tuple, list] = None, cursor_class: type = None,
            stacklevel: int = 4
    ) -> type:
        self._logger.debug('Execute operation: {}'.format(operation), stacklevel=stacklevel)
        self._logger.debug('Execute params: {}'.format(params), stacklevel=stacklevel)
        connect = self._pool.connection()
        cursor = connect.cursor(cursorclass=cursor_class)
        try:
            cursor.execute(operation, params)
            yield cursor
        except Exception as e:
            self._logger.exception('Execute error: {}'.format(e), stacklevel=stacklevel)
            raise e
        finally:
            cursor.close()
            connect.close()

    @contextlib.contextmanager
    def executemany(
            self, operation: str,
            *,
            seq_params: Union[dict, tuple, list], cursor_class: type = None,
            stacklevel: int = 4
    ) -> type:
        self._logger.debug('Executemany operation: {}'.format(operation), stacklevel=stacklevel)
        self._logger.debug('Executemany seq_params: {}'.format(seq_params), stacklevel=stacklevel)
        connect = self._pool.connection()
        cursor = connect.cursor(cursorclass=cursor_class)
        try:
            cursor.executemany(operation, seq_params)
            yield cursor
        except Exception as e:
            self._logger.exception('Executemany error: {}'.format(e), stacklevel=stacklevel)
            raise e
        finally:
            cursor.close()
            connect.close()

    def create_table(self, table: str, columns_info: dict, ignore: bool = True, database: str = None):
        """
        sql = 'CREATE TABLE IF NOT EXISTS `tmp_test_script` \
              '(`a1` varchar(255) NULL, `b2` varchar(255) NULL, `c3` varchar(255) NULL);'
        rowcount = database.create_table(
            'tmp_test_script', {'a1': 'varchar(255) NULL', 'b2': 'varchar(255) NULL', 'c3': 'varchar(255) NULL'})
        """
        keys, values = zip(*columns_info.items())
        operation = 'CREATE TABLE {ignore}{database}{table} ({columns});'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            ignore='IF NOT EXISTS ' if ignore else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(keys, sy='`%s` %%s') % values
        )
        with self.execute(operation, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def drop_table(self, table: str, ignore: bool = True, database: str = None):
        """
        sql = 'DROP TABLE `tmp_test_script`;'
        rowcount = database.drop_table('tmp_test_script')
        """
        operation = 'DROP TABLE {ignore}{database}{table};'.format(
            ignore='IF EXISTS ' if ignore else '',
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table)
        )
        with self.execute(operation, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def insert_one(self, table: str, columns: tuple, params: tuple, database: str = None) -> int:
        """
        sql = 'INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUE (%s, %s, %s);'
        rowcount = database.insert_one('tmp_test_script', ('a1', 'b2', 'c3'), ('1', '2', '3'))
        """
        operation = 'INSERT INTO {database}{table} ({columns}) VALUE ({params});'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns),
            params=self._placeholder(columns)
        )
        with self.execute(operation, params=params, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def insert_all(self, table: str, columns: tuple, seq_params: List[tuple], database: str = None) -> int:
        """
        sql = 'INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUES (%s, %s, %s);'
        rowcount = database.insert_all('tmp_test_script', ('a1', 'b2', 'c3'), [("4", "5", "6"), ("7", "8", "9")])
        """
        operation = 'INSERT INTO {database}{table} ({columns}) VALUES ({params});'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns),
            params=self._placeholder(columns)
        )
        with self.executemany(operation, seq_params=seq_params, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def delete(self, table: str, columns: tuple, params: tuple, database: str = None) -> int:
        """
        sql = 'DELETE FROM `tmp_test_script` WHERE `a1`=%s AND `b2`=%s AND `c3`=%s;'
        rowcount = database.delete('tmp_test_script', ('a1', 'b2', 'c3'), ("4", "5", "6"))
        """
        operator = 'DELETE FROM {database}{table} WHERE {columns};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns, sy='`%s` = %%s', sp=' AND ')
        )
        with self.execute(operator, params=params, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def select_one(self, table: str, columns: tuple = (), database: str = None) -> iter:
        """
        sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
        database.select_one('tmp_test_script', ('a1', 'b2', 'c3')) <-- loop it
        """
        operation = 'SELECT {columns} FROM {database}{table};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns) if columns else '*'
        )
        with self.execute(operation, stacklevel=5) as cur:
            while True:
                row = cur.fetchone()
                if not row:
                    break
                yield row

    def select_many(self, table: str, columns: tuple = (), size: int = None, database: str = None) -> iter:
        """
        sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
        database.select_many('tmp_test_script', ('a1', 'b2', 'c3'), size=2) <-- loop it
        """
        operation = 'SELECT {columns} FROM {database}{table};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns) if columns else '*'
        )
        with self.execute(operation, stacklevel=5) as cur:
            while True:
                rows = cur.fetchmany(size)
                if not rows:
                    break
                yield rows

    def select_all(self, table: str, columns: tuple = (), database: str = None) -> list:
        """
        sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
        rows = database.select_all('tmp_test_script', ('a1', 'b2', 'c3'))
        """
        operation = 'SELECT {columns} FROM {database}{table};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            columns=self._placeholder_plus(columns) if columns else '*'
        )
        with self.execute(operation, stacklevel=5) as cur:
            rows = cur.fetchall()
        return rows

    def update(self, table: str, values: dict, columns: tuple, params: tuple, database: str = None) -> int:
        """
        sql = 'UPDATE `tmp_test_script` SET `a1`=%s, `b2`=%s, `c3`=%s WHERE `a1`=%s AND `b2`=%s AND `c3`=%s;'
        rowcount = database.update('tmp_test_script', {'a1': '-1', 'b2': '-2', 'c3': '-3'},
                                   ('a1', 'b2', 'c3'), ("1", "2", "3"))
        """
        keys, values = zip(*values.items())
        operator = 'UPDATE {database}{table} SET {values} WHERE {columns};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            values=self._placeholder_plus(keys, sy='`%s` = %%s'),
            columns=self._placeholder_plus(columns, sy='`%s` = %%s', sp=' AND ')
        )
        with self.execute(operator, params=values + params, stacklevel=5) as cur:
            rowcount = cur.rowcount
        return rowcount

    def count(self, table: str, column: str = None, database: str = None) -> int:
        """
        sql = 'SELECT COUNT(`a1`) FROM `tmp_test_script`;'
        rowcount = database.count('tmp_test_script', 'a1')
        """
        operation = 'SELECT COUNT({column}) FROM {database}{table};'.format(
            database='{}.'.format(self._wrapper(database)) if database else '',
            table=self._wrapper(table),
            column=self._wrapper(column) if column else '*'
        )
        with self.execute(operation, stacklevel=5) as cur:
            row, = cur.fetchone()
        return row


__all__ = ['MySQLDatabase']
