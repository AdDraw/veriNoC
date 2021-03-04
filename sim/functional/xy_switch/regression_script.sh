#!/bin/bash
fail_cnt=0
att_cnt=0

make -j6 -B TESTFACTORY=0 PORT_N=5 SW_CONFIG=0 #CENTER
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=3 SW_CONFIG=1
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=3 SW_CONFIG=2
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=3 SW_CONFIG=3
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=3 SW_CONFIG=4
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=4 SW_CONFIG=5
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=4 SW_CONFIG=6
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=4 SW_CONFIG=7
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`
make -j6 -B TESTFACTORY=0 PORT_N=4 SW_CONFIG=8
fail_cnt=`expr $fail_cnt + $?`
att_cnt=`expr $att_cnt + 1`

echo "fails/attempts: "$fail_cnt"/"$att_cnt
