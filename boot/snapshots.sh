R=$RUN; N=${1:-j17}; T=900
S=$SCRIPTS
P=$ANYPS5/tools/pad_input.py
G=gdb
rm -rf $R/runs/$N; mkdir -p $R/runs/$N/snap; : > $R/pad.cmd; cd $R
(env APS5_NO_WGI=1 APS5_LOG_TIMESTAMPS=1 ANYPS5_SCREENSHOTS="$R/runs/$N/shots" APS5_SCREENSHOT_TRIGGER="$R/shot.trigger" APS5_PAD_INPUT_FILE="$R/pad.cmd" timeout $T ./jedi.exe > $R/runs/$N/run.log 2>&1; echo "exit=$?" > $R/runs/$N/exit.txt) &
PID=""; t0=$(date +%s)
while true; do
  sleep 5; [ -f $R/runs/$N/exit.txt ] && break
  t=$(( $(date +%s) - t0 ))
  PID=$(tasklist //FI "IMAGENAME eq jedi.exe" //FO CSV //NH | grep -i jedi | head -1 | cut -d, -f2 | tr -d '"')
  if [ $t -gt 60 ]; then case $(( t / 15 % 3 )) in 0) python $P --hold-ms 300 $R/pad.cmd cross >/dev/null 2>&1;; 1) python $P --hold-ms 2000 --left-stick 128 0 $R/pad.cmd >/dev/null 2>&1;; 2) touch $R/shot.trigger;; esac; fi
  if [ -n "$PID" ] && [ $t -gt 40 ]; then
    $G -p $PID -batch -x $SCRIPTS/gdb/q2.py > $R/runs/$N/snap/s_$t.txt 2>&1
    grep -q "^LowLevelFatal" $R/runs/$N/run.log && { echo "fatal at t=$t"; break; }
    sleep 10
  fi
done
echo "loop end t=$t"
