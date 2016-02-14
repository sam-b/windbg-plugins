# windbg-plugins
Repository for any useful windbg plugins I've written.

#heap_trace
Hooks heap operations and tracks their arguments and return values.
Run:
<pre>
.load pykd.pyd
!py "PATH_TO_REPO\heap_trace.py"
</pre>
This will log to your home directory as log.log. You can then create a villoc visualisation of this by running:
<pre>
python villoc.py log.log out.html
</pre>
Example villoc output: 
![Example](https://raw.githubusercontent.com/sam-b/windbg-plugins/master/heap%20tracing/screenshots/pykd_heap_trace_villoc_example.PNG)
#Requirements
All plugins use the [pykd](https://pykd.codeplex.com/) python interface for windbg.