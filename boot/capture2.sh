R=$RUN; P=$ANYPS5/tools/pad_input.py
for N in "$@"; do
  rm -rf $R/runs/$N; mkdir -p $R/runs/$N/cp; : > $R/pad.cmd; cd $R
  (env APS5_DUMP_COMPUTE_PIPELINES="$R/runs/$N/cp" APS5_DUMP_COMPUTE_MIN_WORDS=2000000 APS5_PROFILE_DRAW=1 APS5_NO_WGI=1 APS5_LOG_TIMESTAMPS=1 APS5_PAD_INPUT_FILE="$R/pad.cmd" timeout 1500 ./jedi.exe > $R/runs/$N/run.log 2>&1; echo "exit=$?" > $R/runs/$N/exit.txt) &
  t0=$(date +%s)
  while true; do
    sleep 5; t=$(( $(date +%s) - t0 ))
    [ -f $R/runs/$N/exit.txt ] && break
    if [ $t -gt 60 ]; then case $(( t / 15 % 3 )) in 0) python $P --hold-ms 300 $R/pad.cmd cross >/dev/null 2>&1;; 1) python $P --hold-ms 2000 --left-stick 128 0 $R/pad.cmd >/dev/null 2>&1;; 2) : ;; esac; sleep 10; fi
    if grep -a -q "creating a pipeline for 22[0-9]\{5\} SPIR-V words (program 0x201a870000)" $R/runs/$N/run.log; then sleep 20; echo "$N captured at t=$t: $(grep -a -o 'creating a pipeline for 22[0-9]\{5\} SPIR-V words (program 0x201a870000)' $R/runs/$N/run.log | head -1)"; break; fi
    grep -q "^LowLevelFatal" $R/runs/$N/run.log && { echo "$N froze at t=$t before capture"; break; }
  done
  taskkill //IM jedi.exe //F > /dev/null 2>&1; sleep 5
  ls -la $R/runs/$N/cp | tail -3
done
