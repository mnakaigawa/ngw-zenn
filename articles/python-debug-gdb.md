---
title: "gdbでpythonをデバッグ"
emoji: "🐷"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "gdb"]
published: true
---

## はじめに
pythonプロセスをgdbでアタッチして、python領域をデバッグする方法です。
gdbでC/C++のデバッグができますが、python領域は簡単にはみれないのでpython-debuginfoをつかって、デバッグする方法を記載します。
情報の元ネタは、参考文献[^1]を参照。

## どういう時につかえるか
- pdbではスレッド間のアタッチ／デタッチができないので、マルチスレッドのデバッグできるようにどうにかしたい
- 特定の環境でしかおきないバグや、長時間実行後にハングアップするなど、ログ出力でのデバッグなど調査がツラい
- IDEでインスペクタなどがつかえない環境、pydevなどでsuspendしてもスレッドがとまってくれない

## 開発環境
- python2.7 / python3.6.8 (どちらもyumでインストール)
- Cent OS 7
CentOS Linux release 7.7.1908 (Core)
- GNU gdb
GNU gdb (GDB) Red Hat Enterprise Linux 7.6.1-115.el7

## セットアップ
- デバッグ用のリポジトリを有効にして、python-debuginfoをインストール
(python2.7の場合)
```
# debuginfo-install python
```
(python3の場合)
```
# debuginfo-install python3 libgcc
```
:::message
私自身は、以下のようにデバッグ用のリポジトリを有効にしてインストールする方法をやっていましたが、debuginfo-installのほうがスマートそうなので直しています。
`yum --disablerepo='*' --enablerepo='*-debug*' install python-debuginfo`
:::

:::message
python3ではなぜかlibgccのdebuginfoもインストールしろ、と怒られたので追記しています。ほかにも必要なパッケージが必要かもしれません。足りない場合は、以下に記載するgdb起動時に、インストールが必要なものについてメッセージが出力されるはず？
:::

## 使い方
1. デバッグしたいプロセスのIDを取得
2. 以下のコマンドでgdbを起動してアタッチ
``` Bash
$ gdb python <PID>
```
3. python-debuginfo用のコマンドファイルを実行
(python2.7の場合)
``` Bash
(gdb) source /usr/lib/debug/usr/lib64/libpython2.7.so.1.0.debug-gdb.py
```
(python3の場合)
``` Bash
(gdb) source /usr/lib/debug/usr/lib64/libpython3.6dm.so.1.0-3.6.8-18.el7.x86_64.debug-gdb.py
```
:::message
今回は、3.6.8をつかっているので上記ですが、/usr/lib/debug/usr/lib64/下を覗いて、適宜バージョンに対応するファイルを適用してください。
:::

4. 以下のコマンドがつかえるようになったので、実行してデバッグ
* `py-list`
該当範囲のPythonコード出力
* `py-bt`
該当Pythonコードのバックトレース
* `py-up`
Pythonスタックの上へ
* `py-down`
Pythonスタックの下へ
* `py-print`
Pythonスタックの変数表示
* `py-locals`
Pythonスタックの変数リスト表示

:::message
上記の説明は、参考文献[^2]から引用させていただきました。
使い方などヘルプを探しましたが、見当たりませんでした。
どこかに情報あるかもしれませんが、コマンドファイル*.debug-gdb.pyのソースをみて、なんのコマンドがつかえるか／どう使うのかみてみるのが早いかもしれません。
:::
## デモ
1. デッドロックするpythonプログラムを実行
なんでもよいですが、この記事用に試しにつくったプログラムは以下です。
:::details pythondebugggb.py
``` python: pythondebugggb.py
import threading
import time

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
```
:::

2. プロセスIDをチェック
psコマンドとかpgrepとかで探してください。

3. gdbでアタッチして、コマンドファイル*.debug-gdb.pyを実行して、py-btを実行
``` Bash
$ gdb python3 7066
GNU gdb (GDB) Red Hat Enterprise Linux 7.6.1-115.el7
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-redhat-linux-gnu".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>...
Reading symbols from /usr/bin/python3.6...Reading symbols from /usr/lib/debug/usr/bin/python3.6.debug...done.
done.
Attaching to program: /usr/bin/python3, process 7066
Reading symbols from /lib64/libpython3.6m.so.1.0...Reading symbols from /usr/lib/debug/usr/lib64/libpython3.6m.so.1.0.debug...done.
done.
Loaded symbols for /lib64/libpython3.6m.so.1.0
Reading symbols from /lib64/libpthread.so.0...Reading symbols from /usr/lib/debug/usr/lib64/libpthread-2.17.so.debug...done.
done.
[New LWP 7067]
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
Loaded symbols for /lib64/libpthread.so.0
Reading symbols from /lib64/libdl.so.2...Reading symbols from /usr/lib/debug/usr/lib64/libdl-2.17.so.debug...done.
done.
Loaded symbols for /lib64/libdl.so.2
Reading symbols from /lib64/libutil.so.1...Reading symbols from /usr/lib/debug/usr/lib64/libutil-2.17.so.debug...done.
done.
Loaded symbols for /lib64/libutil.so.1
Reading symbols from /lib64/libm.so.6...Reading symbols from /usr/lib/debug/usr/lib64/libm-2.17.so.debug...done.
done.
Loaded symbols for /lib64/libm.so.6
Reading symbols from /lib64/libc.so.6...Reading symbols from /usr/lib/debug/usr/lib64/libc-2.17.so.debug...done.
done.
Loaded symbols for /lib64/libc.so.6
Reading symbols from /lib64/ld-linux-x86-64.so.2...Reading symbols from /usr/lib/debug/usr/lib64/ld-2.17.so.debug...done.
done.
Loaded symbols for /lib64/ld-linux-x86-64.so.2
Reading symbols from /usr/lib64/python3.6/lib-dynload/_heapq.cpython-36m-x86_64-linux-gnu.so...Reading symbols from /usr/lib/debug/usr/lib64/python3.6/lib-dynload/_heapq.cpython-36m-x86_64-linux-gnu.so.debug...done.
done.
Loaded symbols for /usr/lib64/python3.6/lib-dynload/_heapq.cpython-36m-x86_64-linux-gnu.so
Reading symbols from /lib64/libgcc_s.so.1...Reading symbols from /usr/lib/debug/usr/lib64/libgcc_s-4.8.5-20150702.so.1.debug...done.
done.
Loaded symbols for /lib64/libgcc_s.so.1
0x00007f5a083e8afb in futex_abstimed_wait (cancel=true, private=<optimized out>, 
    abstime=0x0, expected=0, futex=0x7f59fc000c10)
    at ../nptl/sysdeps/unix/sysv/linux/sem_waitcommon.c:43
43	      err = lll_futex_wait (futex, expected, private);
(gdb) source /usr/lib/debug/usr/lib64/libpython3.6dm.so.1.0-3.6.8-18.el7.x86_64.debug-gdb.py
(gdb) py-bt
(gdb) py-bt
Traceback (most recent call first):
  <built-in method acquire of _thread.lock object at remote 0x7f5a011328c8>
  File "/usr/lib64/python3.6/threading.py", line 1072, in _wait_for_tstate_lock
    elif lock.acquire(block, timeout):
  File "/usr/lib64/python3.6/threading.py", line 1056, in join
    self._wait_for_tstate_lock()
  File "pythondebuggdb.py", line 68, in main
    inc_thread.join()
  File "pythondebuggdb.py", line 26, in __init__
    self.main()
  File "pythondebuggdb.py", line 72, in <module>
    MultiThreadDeadLock()
```

4. スレッドを切り替え
``` Bash
(gdb) info threads
  Id   Target Id         Frame 
  2    Thread 0x7f5a01094700 (LWP 7067) "python3" 0x00007f5a083e8afb in futex_abstimed_wait (cancel=true, private=<optimized out>, abstime=0x0, expected=0, futex=0x2471020)
    at ../nptl/sysdeps/unix/sysv/linux/sem_waitcommon.c:43
* 1    Thread 0x7f5a08d20740 (LWP 7066) "python3" 0x00007f5a083e8afb in futex_abstimed_wait (cancel=true, private=<optimized out>, abstime=0x0, expected=0, futex=0x7f59fc000c10)
    at ../nptl/sysdeps/unix/sysv/linux/sem_waitcommon.c:43
(gdb) thread 2
[Switching to thread 2 (Thread 0x7f5a01094700 (LWP 7067))]
#0  0x00007f5a083e8afb in futex_abstimed_wait (cancel=true, private=<optimized out>, 
    abstime=0x0, expected=0, futex=0x2471020)
    at ../nptl/sysdeps/unix/sysv/linux/sem_waitcommon.c:43
43	      err = lll_futex_wait (futex, expected, private);
```

* py-listで実行行を確認しつつ、別スレッド側をpy-btでスタックトレースを確認
``` Bash
(gdb) py-list
  31            :param lock: (object) threading.Lock()で取得した排他用オブジェクト
  32            :return: None
  33            '''
  34            while True:
  35                time.sleep(0.1) # スレッド間の割り込み用に少し待たせる
 >36                lock.acquire()
  37                self._counter += 1
  38                lock.release()
  39    
  40        def print_counter(self, lock):
  41            '''
(gdb) py-bt
Traceback (most recent call first):
  <built-in method acquire of _thread.lock object at remote 0x7f5a08c2f4e0>
  File "pythondebuggdb.py", line 36, in increment
    lock.acquire()
  File "/usr/lib64/python3.6/threading.py", line 864, in run
    self._target(*self._args, **self._kwargs)
  File "/usr/lib64/python3.6/threading.py", line 916, in _bootstrap_inner
    self.run()
  File "/usr/lib64/python3.6/threading.py", line 884, in _bootstrap
    self._bootstrap_inner()
```
2スレッドともlock.acquire()で止まっているので、デッドロックだということがわかる。

# 参考文献
以下、脚注に記載
[^1]: [Debugging an inactive python process](https://medium.com/python-pandemonium/debugging-an-inactive-python-process-2b11f88730c7)
[^2]: [Qiita:Pythonでgdbを操作する。](https://qiita.com/sakaia/items/1ede177f56058e7d6997)
