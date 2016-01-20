# windbg-plugins
Repository for any useful windbg plugins I've written.

#heap_trace
Hooks heap operations and tracks their arguments and return values.
Run:
<pre>
.load pykd.pyd
!py "PATH_TO_REPO\heap_trace.py"
</pre>
#Requirements
All plugins use the [pykd](https://pykd.codeplex.com/) python interface for windbg.