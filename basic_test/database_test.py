#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author      : YongJie-Xie
@Contact     : fsswxyj@qq.com
@DateTime    : 0000-00-00 00:00
@Description : ''
@FileName    : database_test.py
@License     : MIT License
@ProjectName : Py3Scripts
@Software    : PyCharm
@Version     : 1.0
"""
import MySQLdb
from MySQLdb.cursors import SSCursor

from basic import DEBUG, logger, MySQLDatabase


def main():
    database = MySQLDatabase(
        host='127.0.0.1', port=3306, username='test', password='test', database='test',
        creator=MySQLdb, cursor_class=SSCursor, logger=logger)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('创建表：`tmp_test_script`')
    # sql = 'CREATE TABLE IF NOT EXISTS `tmp_test_script` (`a1` varchar(255) NULL, `b2` varchar(255) NULL, ' \
    #       '`c3` varchar(255) NULL);'
    # with database.execute(sql) as cur:
    #     logger.info('创建表结果：%s', cur.rowcount)
    rowcount = database.create_table(
        'tmp_test_script', {'a1': 'varchar(255) NULL', 'b2': 'varchar(255) NULL', 'c3': 'varchar(255) NULL'})
    logger.info('创建表结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('插入单条数据：`tmp_test_script` --> ("1", "2", "3")')
    # sql = 'INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUE (%s, %s, %s);'
    # with database.execute(sql, params=('1', '2', '3')) as cur:
    #     logger.info('插入单条数据结果：%s', cur.rowcount)
    rowcount = database.insert_one('tmp_test_script', ('a1', 'b2', 'c3'), ('1', '2', '3'))
    logger.info('插入单条数据结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('插入多条数据：`tmp_test_script` --> [("4", "5", "6"), ("7", "8", "9")]')
    # sql = 'INSERT INTO `tmp_test_script` (`a1`, `b2`, `c3`) VALUES (%s, %s, %s);'
    # with database.executemany(sql, seq_params=[("4", "5", "6"), ("7", "8", "9")]) as cur:
    #     logger.info('插入多条数据结果：%s', cur.rowcount)
    rowcount = database.insert_all('tmp_test_script', ('a1', 'b2', 'c3'), [("4", "5", "6"), ("7", "8", "9")])
    logger.info('插入多条数据结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('查询逐条数据：`tmp_test_script`')
    # sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
    # with database.execute(sql) as cur:
    #     row = cur.fetchone()
    #     while row:
    #         logger.info('查询逐条数据结果：%s', row)
    #         row = cur.fetchone()
    #     # Python 3.8 very nice!!!
    #     # while row := cur.fetchone():
    #     #     logger.info('逐条查询数据结果：%s', row)
    for row in database.select_one('tmp_test_script', ('a1', 'b2', 'c3')):
        logger.info('逐条查询数据结果：%s', row)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('更新数据：`tmp_test_script` --> ("1", "2", "3") --> ("-1", "-2", "-3")')
    # sql = 'UPDATE `tmp_test_script` SET `a1`=%s, `b2`=%s, `c3`=%s WHERE `a1`=%s AND `b2`=%s AND `c3`=%s;'
    # with database.execute(sql, params=("-1", "-2", "-3", "1", "2", "3")) as cur:
    #     logger.info('更新数据结果：%s', cur.rowcount)
    rowcount = database.update('tmp_test_script',
                               {'a1': '-1', 'b2': '-2', 'c3': '-3'}, ('a1', 'b2', 'c3'), ("1", "2", "3"))
    logger.info('更新数据结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('查询多条数据：`tmp_test_script`')
    # sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
    # with database.execute(sql) as cur:
    #     while True:
    #         rows = cur.fetchmany(2)
    #         if not rows:
    #             break
    #         logger.info('查询多条数据结果：%s', rows)
    for row in database.select_many('tmp_test_script', ('a1', 'b2', 'c3'), size=2):
        logger.info('查询多条数据结果：%s', row)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('删除数据：`tmp_test_script` --> ("4", "5", "6")')
    # sql = 'DELETE FROM `tmp_test_script` WHERE `a1`=%s AND `b2`=%s AND `c3`=%s;'
    # with database.execute(sql, params=("4", "5", "6")) as cur:
    #     logger.info('删除数据结果：%s', cur.rowcount)
    rowcount = database.delete('tmp_test_script', ('a1', 'b2', 'c3'), ("4", "5", "6"))
    logger.info('删除数据结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('查询全部数据：`tmp_test_script`')
    # sql = 'SELECT `a1`, `b2`, `c3` FROM `tmp_test_script`;'
    # with database.execute(sql) as cur:
    #     rows = cur.fetchall()
    #     logger.info('查询全部数据结果：%s', rows)
    rows = database.select_all('tmp_test_script', ('a1', 'b2', 'c3'))
    logger.info('查询全部数据结果：%s', rows)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('统计表：`tmp_test_script`')
    # sql = 'SELECT COUNT(`a1`) FROM `tmp_test_script`;'
    # with database.execute(sql) as cur:
    #     logger.info('统计表结果：%s', cur.fetchone()[0])
    rowcount = database.count('tmp_test_script', 'a1')
    logger.info('统计表结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################
    logger.info('删除表：`tmp_test_script`')
    # sql = 'DROP TABLE `tmp_test_script`;'
    # with database.execute(sql) as cur:
    #     logger.info('删除表结果：%s', cur.rowcount)
    rowcount = database.drop_table('tmp_test_script')
    logger.info('删除表结果：%s', rowcount)
    logger.info('=====================================================================================================')
    ####################################################################################################################


if __name__ == '__main__':
    logger.set_level(DEBUG)
    main()
