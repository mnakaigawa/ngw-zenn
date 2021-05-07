#!/usr/bin/env python
# -*- coding:utf-8-*-
'''
Created on 2021/03/27(Sat)

@author: nakaigawa
'''
import threading
import time

__author__ = "Masaki Nakaigawa <tnkngw29@gmail.com>"
__status__ = "prototype"
__version__ = "0.1.0"

class MultiThreadDeadLock(object):
    '''
    MultiThreadDeadLock
    デッドロックを意図的におこすテスト用の実装
    '''

    def __init__(self):
        '''
        constructor
        '''
        self._counter = 0
        self.main()

    def increment(self, lock):
        '''
        カウンタをインクリメントします。
        :param lock: (object) threading.Lock()で取得した排他用オブジェクト
        :return: None
        '''
        while True:
            time.sleep(0.1) # スレッド間の割り込み用に少し待たせる
            lock.acquire()
            self._counter += 1
            lock.release()

    def print_counter(self, lock):
        '''
        現在のカウンタを表示します。
        デッドロックを再現するため3より大きい場合に意図的にロックを解放せずにExceptionをraiseします。
        :param lock: (object) threading.Lock()で取得した排他用オブジェクト
        :return: None
        '''
        while True:
            time.sleep(0.1) # スレッド間の割り込み用に少し待たせる
            lock.acquire()
            print("counter = {}".format(self._counter))
            if self._counter > 3:
                # 意図的にExceptionをraiseして、デッドロックさせる。
                # 実際には、予期しないところでExceptionがraiseされることだろう...
                raise RuntimeError()
            lock.release()

    def main(self):
        '''
        メイン処理
        :return: None
        '''
        lock = threading.Lock()

        inc_thread = threading.Thread(target=self.increment, args=(lock,))
        print_thread = threading.Thread(target=self.print_counter, args=(lock,))
        inc_thread.start()
        print_thread.start()
        inc_thread.join()
        print_thread.join()

if __name__ == '__main__':
    MultiThreadDeadLock()
