import 'package:flutter/material.dart';

class CustomAppBar extends StatelessWidget implements PreferredSizeWidget {
  const CustomAppBar({Key? key}) : super(key: key);

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight); // AppBar의 기본 높이

  @override
  Widget build(BuildContext context) {
    return AppBar(
      leading: Builder(
        builder: (context) => IconButton(
          icon: const Icon(Icons.menu), // 햄버거 아이콘
          onPressed: () {
            // TODO: Implement drawer opening (서랍 메뉴 열기 기능 구현)
          },
        ),
      ),
      title: const Column( // 앱 바 제목 부분
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'AB Foundation', // 메인 제목
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          Text(
            'the origination of your financial administration', // 부제목
            style: TextStyle(fontSize: 10),
          ),
        ],
      ),
      backgroundColor: Colors.white, // 배경색 흰색
      foregroundColor: Colors.black, // 아이콘 및 글자색 검정색
      elevation: 1, // 그림자
    );
  }
}