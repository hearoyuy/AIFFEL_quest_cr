import 'package:flutter/material.dart';
import 'dart:async';


void main() {
  runApp(MyApp());
}


class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: TimerApp(),
    );
  }
}


class TimerApp extends StatefulWidget {
  @override
  State<TimerApp> createState() => _TimerAppState();
}


class _TimerAppState extends State<TimerApp> {
  int timeLeft = 25 * 60;  // 25분을 초로 변환
  Timer? timer;
  bool isRunning = false;
  bool isWork = true;
  int count = 0;


  void startNewSession() {
    if (count >= 8) {  // 4회 완료
      stop();
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('완료!'),
          content: Text('4회 반복이 모두 끝났습니다!'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                reset();
              },
              child: Text('확인'),
            ),
          ],
        ),
      );
      return;
    }


    setState(() {
      if (isWork) {
        count++;
        // 카운트가 7이면 마지막 휴식
        if (count == 7) {
          timeLeft = 15 * 60;  // 15분 휴식
        } else {
          timeLeft = 5 * 60;   // 5분 휴식
        }
        isWork = false;
      } else {
        timeLeft = 25 * 60;  // 25분 작업
        isWork = true;
      }
      start();  // 자동으로 다음 세션 시작
    });
  }


  void start() {
    timer = Timer.periodic(
      Duration(seconds: 1),
          (timer) {
        setState(() {
          if (timeLeft > 0) {
            timeLeft--;
          } else {
            timer.cancel();
            startNewSession();
          }
        });
      },
    );
    setState(() {
      isRunning = true;
    });
  }


  void stop() {
    timer?.cancel();
    setState(() {
      isRunning = false;
    });
  }


  void reset() {
    timer?.cancel();
    setState(() {
      timeLeft = 25 * 60;  // 25분으로 초기화
      isRunning = false;
      isWork = true;
      count = 0;
    });
  }


  String getTime() {
    int minutes = timeLeft ~/ 60;  // 분 계산
    int seconds = timeLeft % 60;   // 초 계산
    // 초가 1자리 수일 때 앞에 0을 붙임 (예: 05)
    return '$minutes:${seconds.toString().padLeft(2, '0')}';
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('포모도로 타이머'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              isWork ? '작업 중' : '휴식 중',
              style: TextStyle(fontSize: 24),
            ),
            SizedBox(height: 20),
            Text(
              getTime(),
              style: TextStyle(fontSize: 48, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 20),
            Text(
              '${(count + 1) ~/ 2}회차/4회',
              style: TextStyle(fontSize: 20),
            ),
            SizedBox(height: 30),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton(
                  onPressed: isRunning ? stop : start,
                  child: Text(isRunning ? '정지' : '시작'),
                ),
                SizedBox(width: 20),
                TextButton(
                  onPressed: reset,
                  child: Text('초기화'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }


  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }
}
