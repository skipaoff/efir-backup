import pathlib, re, subprocess, sys
f = pathlib.Path(sys.argv[1]); t = f.read_text()
js = t[t.index("<script>")+8:t.index("</script>")]
tmp = pathlib.Path("/tmp/_check.js"); tmp.write_text(js)
r = subprocess.run(["node","--check",str(tmp)],capture_output=True,text=True)
print(f.name, "JS ok" if r.returncode==0 else "JS ERROR\n"+r.stderr[:600])
# грубая проверка парности тегов
for tag in ("div","section","header"):
    o,c = len(re.findall("<%s[ >]"%tag,t)), t.count("</%s>"%tag)
    if o!=c: print("  теги %s: %d открыто, %d закрыто"%(tag,o,c))
