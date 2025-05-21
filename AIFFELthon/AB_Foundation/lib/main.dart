import 'package:flutter/material.dart';
import 'document_portal_screen.dart'; // 메인 화면 위젯 임포트

void main() {
  runApp(const MyApp()); // 앱 실행
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp( // 앱의 기본 설정
      title: 'AB Foundation Document Portal',
      theme: ThemeData(
        primarySwatch: Colors.grey,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const DocumentPortalScreen(), // 첫 화면 지정
    );
  }
}