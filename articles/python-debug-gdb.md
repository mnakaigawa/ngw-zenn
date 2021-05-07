---
title: "gdbでpythonをデバッグ"
emoji: "🐷"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: ["python", "gdb"]
published: false
---

## はじめに
pythonプロセスをgdbでアタッチして、python領域をデバッグする方法です。
gdbでC/C++のデバッグができますが、python領域は簡単にはみれないのでpython-debuginfoをつかって、デバッグする方法を記載します。

## どういう時につかえるか
* pdbではスレッド間のアタッチ／デタッチができないので、マルチスレッドのデバッグできるようにどうにかしたい
* 特定の環境でしかおきないバグや、長時間実行後にハングアップするなど、ログ出力でのデバッグなど調査がツラい
* IDEでインスペクタなどがつかえない環境、pydevなどでsuspendしてもスレッドがとまってくれない

## 開発環境
* python2.7、python3系
* Cent OS 7

## セットアップ
* gdb、pythonはyumでインストール

* デバッグ用のリポジトリを有効にして、python-debuginfoをインストール
```
# yum -y --disablerepo='*' --enablerepo='*-debug*' install python-debuginfo
```

## 使い方
1. デバッグしたいプロセスのIDを取得
2. 以下のコマンドでgdbを起動してアタッチ
``` Bash
$ gdb python <PID>
```
3. python-debuginfo用のツールを実行
``` Bash
(gdb) source /usr/lib/debug/usr/lib64/libpython2.7.so.1.0.debug-gdb.py
```
4. 以下のコマンドがつかえるようになったので、実行してデバッグ
* py-list
該当範囲のPythonコード出力
* py-bt
該当Pythonコードのバックトレース
* py-up
Pythonスタックの上へ
* py-down
Pythonスタックの下へ
* py-print
Pythonスタックの変数表示
* py-locals
Pythonスタックの変数リスト表示

## デモ
* デッドロックするpythonプログラムを実行

* プロセスIDをチェック
* gdbでアタッチしてpy-btを実行
``` Bash
$ gdb python 20513
GNU gdb (GDB) Red Hat Enterprise Linux 7.6.1-119.el7
Copyright (C) 2013 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-redhat-linux-gnu".
For bug reporting instructions, please see:
<http://www.gnu.org/software/gdb/bugs/>...
Reading symbols from /usr/bin/python2.7...Reading symbols from /usr/lib/debug/usr/bin/python2.7.debug...done.
done.
Attaching to program: /usr/bin/python, process 20513
Reading symbols from /lib64/libpython2.7.so.1.0...Reading symbols from /usr/lib/debug/usr/lib64/libpython2.7.so.1.0.debug...done.
done.
Loaded symbols for /lib64/libpython2.7.so.1.0
Reading symbols from /lib64/libpthread.so.0...(no debugging symbols found)...done.
[New LWP 20515]
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib64/libthread_db.so.1".
Loaded symbols for /lib64/libpthread.so.0
(中略)
(gdb) source /usr/lib/debug/usr/lib64/libpython2.7.so.1.0.debug-gdb.py
(gdb) py-bt
#3 Waiting for a lock (e.g. GIL)
#4 Waiting for a lock (e.g. GIL)
#6 Frame 0x1badf20, for file /usr/lib64/python2.7/threading.py, line 339, in wait (self=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221f0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221f0>, _Condition__waiters=[<thread.lock at remote 0x7ffb8c522210>], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221f0>) at remote 0x7ffb8c406250>, timeout=None, balancing=True, waiter=<thread.lock at remote 0x7ffb8c522210>, saved_state=None)
    waiter.acquire()
#10 Frame 0x7ffb8c4e3da8, for file /usr/lib64/python2.7/threading.py, line 951, in join (self=<Thread(_Thread__ident=140718231648000, _Thread__block=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221f0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221f0>, _Condition__waiters=[<thread.lock at remote 0x7ffb8c522210>], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221f0>) at remote 0x7ffb8c406250>, _Thread__name='Thread-2', _Thread__daemonic=False, _Thread__started=<_Event(_Verbose__verbose=False, _Event__flag=True, _Event__cond=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221d0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221d0>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221d0>) at remote 0x7ffb8c406210>) at remote 0x7ffb8c4061d0>, _Thread__stderr=<file at remote 0x7ffb8c5711e0>, _Thread__targe...(truncate---Type <return> to continue, or q <return> to quit---
d)
    self.__block.wait()
#14 Frame 0x7ffb8c4e3bc0, for file python-debug-gdb.py, line 41, in main (self=<MultiThreadDeadLock(_counter=1) at remote 0x7ffb8c44c2d0>, lock=<thread.lock at remote 0x7ffb8c522130>, t1=<Thread(_Thread__ident=140718231648000, _Thread__block=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221b0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221b0>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221b0>) at remote 0x7ffb8c406150>, _Thread__name='Thread-1', _Thread__daemonic=False, _Thread__started=<_Event(_Verbose__verbose=False, _Event__flag=True, _Event__cond=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c522190>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c522190>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c522190>) at remote 0x7ffb8c406110>) at remote 0x7ffb8c4060d0>, _Thread_...(truncated)
    t2.join()
#17 Frame 0x7ffb8c5373c0, for file python-debug-gdb.py, line 18, in __init__ (self=<MultiThreadDeadLock(_counter=1) at remote 0x7ffb8c44c2d0>)
    self.main()
#28 Frame 0x7ffb8c537050, for file python-debug-gdb.py, line 44, in <module> ()
    MultiThreadDeadLock()
```

* スレッドを切り替え
``` Bash
(gdb) info threads
  Id   Target Id         Frame 
  2    Thread 0x7ffb8435f700 (LWP 20515) "python" 0x00007ffb8b3bea1d in write
    () from /lib64/libc.so.6
* 1    Thread 0x7ffb8c58f740 (LWP 20513) "python" 0x00007ffb8bdb3b3b in do_futex_wait.constprop.1 () from /lib64/libpthread.so.0
(gdb) thread 2
[Switching to thread 2 (Thread 0x7ffb8435f700 (LWP 20515))]
#0  0x00007ffb8b3bea1d in write () from /lib64/libc.so.6
```

* py-listで実行行を確認しつつ、別スレッド側をpy-btでスタックトレースを確認
``` Bash
(gdb) py-list
  23            lock.release()
  24    
  25        def print_counter(self, lock):
  26            while True:
  27                lock.acquire()
 >28                print("counter = {}".format(self._counter))
  29                if self._counter > 3:
  30                    raise RuntimeError()
  31                lock.release()
  32    
  33        def main(self): 
(gdb) py-bt
#6 Frame 0x7ffb8c420e50, for file python-debug-gdb.py, line 28, in print_counter (self=<MultiThreadDeadLock(_counter=1) at remote 0x7ffb8c44c2d0>, lock=<thread.lock at remote 0x7ffb8c522130>)
    print("counter = {}".format(self._counter))
#11 Frame 0x7ffb8c408050, for file /usr/lib64/python2.7/threading.py, line 765, in run (self=<Thread(_Thread__ident=140718231648000, _Thread__block=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221f0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221f0>, _Condition__waiters=[<thread.lock at remote 0x7ffb8c522210>], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221f0>) at remote 0x7ffb8c406250>, _Thread__name='Thread-2', _Thread__daemonic=False, _Thread__started=<_Event(_Verbose__verbose=False, _Event__flag=True, _Event__cond=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221d0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221d0>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221d0>) at remote 0x7ffb8c406210>) at remote 0x7ffb8c4061d0>, _Thread__stderr=<file at remote 0x7ffb8c5711e0>, _Thread__target...(truncated)
    self.__target(*self.__args, **self.__kwargs)
#14 Frame 0x7ffb7c000910, for file /usr/lib64/python2.7/threading.py, line 812, in __bootstrap_inner (self=<Thread(_Thread__ident=140718231648000, _Thread__block=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221f0>, acquire=<built-in method acquire of thread.lock object at remote---Type <return> to continue, or q <return> to quit---
 0x7ffb8c5221f0>, _Condition__waiters=[<thread.lock at remote 0x7ffb8c522210>], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221f0>) at remote 0x7ffb8c406250>, _Thread__name='Thread-2', _Thread__daemonic=False, _Thread__started=<_Event(_Verbose__verbose=False, _Event__flag=True, _Event__cond=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221d0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221d0>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221d0>) at remote 0x7ffb8c406210>) at remote 0x7ffb8c4061d0>, _Thread__stderr=<file at remote 0x7ffb8c5711e0>, _...(truncated)
    self.run()
#17 Frame 0x7ffb8c420ad0, for file /usr/lib64/python2.7/threading.py, line 785, in __bootstrap (self=<Thread(_Thread__ident=140718231648000, _Thread__block=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221f0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221f0>, _Condition__waiters=[<thread.lock at remote 0x7ffb8c522210>], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221f0>) at remote 0x7ffb8c406250>, _Thread__name='Thread-2', _Thread__daemonic=False, _Thread__started=<_Event(_Verbose__verbose=False, _Event__flag=True, _Event__cond=<_Condition(_Verbose__verbose=False, _Condition__lock=<thread.lock at remote 0x7ffb8c5221d0>, acquire=<built-in method acquire of thread.lock object at remote 0x7ffb8c5221d0>, _Condition__waiters=[], release=<built-in method release of thread.lock object at remote 0x7ffb8c5221d0>) at remote 0x7ffb8c406210>) at remote 0x7ff---Type <return> to continue, or q <return> to quit---
b8c4061d0>, _Thread__stderr=<file at remote 0x7ffb8c5711e0>, _Thread...(truncated)
    self.__bootstrap_inner()
```


# 参考文献
- [Debugging an inactive python process](https://medium.com/python-pandemonium/debugging-an-inactive-python-process-2b11f88730c7)
- [Qiita:Pythonでgdbを操作する。](https://qiita.com/sakaia/items/1ede177f56058e7d6997)
