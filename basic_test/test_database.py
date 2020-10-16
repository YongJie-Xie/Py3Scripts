#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : ''
@FileName    : test_database.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.1
"""
import MySQLdb
from MySQLdb.cursors import SSCursor

from basic import Logger, DEBUG, MySQLDatabase

logger = Logger('test_database', level=DEBUG, simplify=False)
database = MySQLDatabase(
    host='127.0.0.1', port=3306, username='test', password='test', database='test',
    creator=MySQLdb, cursor_class=SSCursor, logger=logger
)


@logger.info('=' * 120)
def create_table(table, columns_info):
    """
    Execute operation: CREATE TABLE IF NOT EXISTS `tmp_test_script`
                           (`a1` varchar(255) NULL, `b2` varchar(255) NULL, `c3` varchar(255) NULL);
    Execute params: None
    """
    logger.info('创建表：`%s`', table)
    rowcount = database.create_table(table, columns_info)
    logger.info('创建表结果：%s', rowcount)


@logger.info('=' * 120)
def insert_one(table, columns, params):
    """
    Execute operation: INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUE (%s, %s, %s);
    Execute params: ('1', '2', '3')
    """
    logger.info('插入单条数据：`%s` --> %s', table, params)
    rowcount = database.insert_one(table, columns, params)
    logger.info('插入单条数据结果：%s', rowcount)


@logger.info('=' * 120)
def insert_all(table, columns, seq_params):
    """
    Executemany operation: INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUES (%s, %s, %s);
    Executemany seq_params: [('4', '5', '6'), ('7', '8', '9')]
    """
    logger.info('插入多条数据：`%s` --> %s', table, seq_params)
    rowcount = database.insert_all(table, columns, seq_params)
    logger.info('插入多条数据结果：%s', rowcount)


@logger.info('=' * 120)
def select_one(table, columns):
    """
    Execute operation: SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;
    Execute params: None
    """
    logger.info('查询逐条数据：`%s`', table)
    for row in database.select_one(table, columns):
        logger.info('逐条查询数据结果：%s', row)


@logger.info('=' * 120)
def update(table, values, columns, params):
    """
    Execute operation: UPDATE `tmp_test_script` SET `a1` = %s, `b2` = %s, `c3` = %s
                           WHERE `a1` = %s AND `b2` = %s AND `c3` = %s;
    Execute params: ('-1', '-2', '-3', '1', '2', '3')
    """
    logger.info('更新数据：`%s` --> %s >>> %s', table, dict(zip(columns, params)), dict(values.items()))
    rowcount = database.update(table, values, columns, params)
    logger.info('更新数据结果：%s', rowcount)


@logger.info('=' * 120)
def select_many(table, columns, size=2):
    """
    Execute operation: SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;
    Execute params: None
    """
    logger.info('查询多条数据：`%s`', table)
    for row in database.select_many(table, columns, size=size):
        logger.info('查询多条数据结果：%s', row)


@logger.info('=' * 120)
def delete(table, columns, params):
    """
    Execute operation: DELETE FROM `tmp_test_script` WHERE `a1` = %s AND `b2` = %s AND `c3` = %s;
    Execute params: ('4', '5', '6')
    """
    logger.info('删除数据：`%s` --> %s', table, params)
    rowcount = database.delete(table, columns, params)
    logger.info('删除数据结果：%s', rowcount)


@logger.info('=' * 120)
def select_all(table, columns):
    """
    Execute operation: SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;
    Execute params: None
    """
    logger.info('查询全部数据：`%s`', table)
    rows = database.select_all(table, columns)
    logger.info('查询全部数据结果：%s', rows)


@logger.info('=' * 120)
def count(table, column):
    """
    Execute operation: SELECT COUNT(`a1`) FROM `tmp_test_script`;
    Execute params: None
    """
    logger.info('统计表：`%s`', table)
    rowcount = database.count(table, column)
    logger.info('统计表结果：%s', rowcount)


@logger.info('=' * 120)
def drop_table(table):
    """
    Execute operation: DROP TABLE IF EXISTS `tmp_test_script`;
    Execute params: None
    """
    logger.info('删除表：`%s`', table)
    rowcount = database.drop_table(table)
    logger.info('删除表结果：%s', rowcount)


def main():
    table = 'tmp_test_script'
    columns = ('a1', 'b2', 'c3')
    columns_info = {'a1': 'varchar(255) NULL', 'b2': 'varchar(255) NULL', 'c3': 'varchar(255) NULL'}
    params_123 = ('1', '2', '3')
    params_456 = ('4', '5', '6')
    params_789 = ('7', '8', '9')
    params_n123 = ('-1', '-2', '-3')

    create_table(table=table, columns_info=columns_info)
    insert_one(table=table, columns=columns, params=params_123)
    insert_all(table=table, columns=columns, seq_params=[params_456, params_789])
    select_one(table=table, columns=columns)
    update(table=table, values=dict(zip(columns, params_n123)), columns=columns, params=params_123)
    select_many(table=table, columns=columns)
    delete(table=table, columns=columns, params=params_456)
    select_all(table=table, columns=columns)
    count(table=table, column=columns[0])
    drop_table(table=table)


if __name__ == '__main__':
    main()
