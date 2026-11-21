R=$RUN; P=$ANYPS5/tools/pad_input.py; G=gdb
cat > $TEMP/qw.py <<'PY'
import gdb
gdb.execute("set pagination off")
for th in gdb.selected_inferior().threads():
    if th.name and th.name.startswith("qworker"):
        th.switch(); gdb.execute("bt 2")
PY
for N in "$@"; do
  rm -rf $R/runs/$N; mkdir -p $R/runs/$N; : > $R/pad.cmd; cd $R
  (env APS5_PROFILE_DRAW=1 APS5_NO_WGI=1 APS5_LOG_TIMESTAMPS=1 ANYPS5_SCREENSHOTS="$R/runs/$N/shots" APS5_SCREENSHOT_TRIGGER="$R/shot.trigger" APS5_PAD_INPUT_FILE="$R/pad.cmd" timeout 3600 ./jedi.exe > $R/runs/$N/run.log 2>&1; echo "exit=$?" > $R/runs/$N/exit.txt) &
  t0=$(date +%s); outcome=""
  while true; do
    sleep 5; t=$(( $(date +%s) - t0 ))
    [ -f $R/runs/$N/exit.txt ] && { outcome="exited at t=$t"; break; }
    if [ $t -gt 60 ]; then case $(( t / 15 % 3 )) in 0) python $P --hold-ms 300 $R/pad.cmd cross >/dev/null 2>&1;; 1) python $P --hold-ms 2000 --left-stick 128 0 $R/pad.cmd >/dev/null 2>&1;; 2) touch $R/shot.trigger;; esac; sleep 10; fi
    grep -q "^LowLevelFatal" $R/runs/$N/run.log && { outcome="froze at t=$t"; break; }
    [ $t -gt 900 ] && { outcome="NO FREEZE through t=$t"; break; }
  done
  echo "$N: $outcome"
  grep -a -o "\(creating\|created\) a pipeline for [0-9]\{6,\} SPIR-V words\( in [0-9]* ms\)\? (program 0x[0-9a-f]*)" $R/runs/$N/run.log | sort | uniq -c | sort -rn | head -8 | sed "s/^/  $N /"
  case "$outcome" in
    froze*)
      for i in $(seq 1 60); do
        PID=$(tasklist //FI "IMAGENAME eq jedi.exe" //FO CSV //NH | grep -i jedi | head -1 | cut -d, -f2 | tr -d '"'); [ -z "$PID" ] && break
        $G -p $PID -batch -x $TEMP/qw.py 2>&1 | grep -q nvgpucomp || { echo "  $N: compiles done after $((i*30))s"; break; }
        sleep 30
      done;;
    NO*) taskkill //IM jedi.exe //F > /dev/null 2>&1; echo "stopping: a boot got past the freeze"; exit 0;;
  esac
  taskkill //IM jedi.exe //F > /dev/null 2>&1; sleep 5
done
