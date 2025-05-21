import 'package:flutter/material.dart'; // Flutter 위젯 사용을 위한 패키지 임포트

void main() {
  runApp(const MyApp()); // 앱의 시작점
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp( // Flutter 앱의 기본 뼈대
      title: 'AB Foundation Document Portal', // 앱 제목
      theme: ThemeData( // 앱의 기본 테마 설정
        primarySwatch: Colors.grey, // 기본 색상 설정
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const DocumentPortalScreen(), // 앱이 시작될 때 보여줄 화면
    );
  }
}

class DocumentPortalScreen extends StatelessWidget {
  const DocumentPortalScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold( // 앱 화면의 기본적인 구조를 제공 (AppBar, body 등)
      appBar: AppBar( // 화면 상단의 앱 바
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu), // 햄버거 메뉴 아이콘
            onPressed: () {
              // TODO: 서랍(Drawer) 열기 기능 구현 필요
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
        backgroundColor: Colors.white, // 앱 바 배경색 흰색
        foregroundColor: Colors.black, // 앱 바 아이콘 및 글자색 검정색
        elevation: 1, // 앱 바 그림자 정도
      ),
      body: SingleChildScrollView( // 화면 내용이 길어질 경우 스크롤 가능하게 함
        padding: const EdgeInsets.all(16.0), // 내용에 패딩 추가
        child: Column( // 위젯들을 세로로 배열
          crossAxisAlignment: CrossAxisAlignment.start, // 자식 위젯들을 왼쪽으로 정렬
          children: [
            const Center( // "Document Portal" 제목을 가운데 정렬
              child: Text(
                'Document Portal',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20), // 세로 간격 추가

            // 사업체 선택 섹션
            const Text(
              'Please select the business entity to whom your document to be submitted.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            TextField( // 사업체 이름 입력 필드
              decoration: InputDecoration( // 입력 필드 디자인 설정
                hintText: 'Business Entity Name', // 힌트 텍스트
                border: OutlineInputBorder( // 테두리 설정
                  borderRadius: BorderRadius.circular(5.0),
                  borderSide: BorderSide.none, // 테두리 선 없음
                ),
                filled: true, // 배경 채우기
                fillColor: Colors.grey[200], // 배경색 연한 회색
                contentPadding:
                const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0), // 내부 패딩
                suffixIcon: const Icon(Icons.search), // 오른쪽 아이콘 (검색)
              ),
            ),
            const SizedBox(height: 8),
            TextField( // 사업체 번호 입력 필드
              decoration: InputDecoration(
                hintText: 'Business Entity No.',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(5.0),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[200],
                contentPadding:
                const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0),
              ),
            ),
            const SizedBox(height: 16),
            Align( // "To Next Step >>" 버튼을 오른쪽으로 정렬
              alignment: Alignment.centerRight,
              child: TextButton( // 텍스트 버튼
                onPressed: () {
                  // TODO: 다음 단계 액션 구현 필요
                },
                child: const Text(
                  'To Next Step >>',
                  style: TextStyle(color: Colors.black),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Divider(), // 구분선
            const SizedBox(height: 20),

            // 관계 선택 섹션
            const Text(
              'Please let us know your relation with the entity.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Row( // 체크박스와 텍스트를 가로로 배열
              children: [
                Row( // Employee 체크박스 그룹
                  mainAxisSize: MainAxisSize.min, // 자식 위젯 크기만큼 공간 차지
                  children: [
                    Checkbox( // 체크박스
                      value: false, // 초기값 (상태 변수로 대체 필요)
                      onChanged: (bool? newValue) {
                        // TODO: 체크박스 상태 변경 처리 구현 필요
                      },
                    ),
                    const Text('Employee'), // 체크박스 라벨
                  ],
                ),
                const SizedBox(width: 20), // 가로 간격 추가
                Row( // Business Counterparty 체크박스 그룹
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Checkbox(
                      value: true, // 초기값 (상태 변수로 대체 필요)
                      onChanged: (bool? newValue) {
                        // TODO: 체크박스 상태 변경 처리 구현 필요
                      },
                    ),
                    const Text('Business Counterparty'), // 체크박스 라벨
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Align( // "To Next Step >>" 버튼을 오른쪽으로 정렬
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  // TODO: 다음 단계 액션 구현 필요
                },
                child: const Text(
                  'To Next Step >>',
                  style: TextStyle(color: Colors.black),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Divider(), // 구분선
            const SizedBox(height: 20),

            // 문서 제출 섹션
            const Text(
              'Please submit your document.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Container( // 문서 상세 정보를 담는 컨테이너 (테두리 있음)
              padding: const EdgeInsets.all(12.0), // 내부 패딩
              decoration: BoxDecoration( // 테두리 설정
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: const Column( // 상세 정보를 세로로 배열
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row( // Counterparty No. 행
                    children: [
                      Expanded(flex: 1, child: Text('Counterparty No.')), // 라벨
                      Expanded(flex: 2, child: Text('123-4564')), // 값
                    ],
                  ),
                  SizedBox(height: 8),
                  Row( // Purchase Order No. 행
                    children: [
                      Expanded(flex: 1, child: Text('Purchase Order No.')),
                      Expanded(flex: 2, child: Text('N/A')),
                    ],
                  ),
                  SizedBox(height: 8),
                  Row( // Your Memo 행
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(flex: 1, child: Text('Your Memo')),
                      Expanded(flex: 2, child: Text('The original invoice is sent via post.')),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Center( // Upload 버튼을 가운데 정렬
              child: ElevatedButton.icon( // 아이콘이 있는 ElevatedButton
                onPressed: () {
                  // TODO: 파일 업로드 액션 구현 필요
                },
                icon: const Icon(Icons.file_upload), // 업로드 아이콘
                label: const Text('Upload'), // 버튼 텍스트
                style: ElevatedButton.styleFrom( // 버튼 스타일 설정
                  backgroundColor: Colors.grey[300], // 배경색 연한 회색
                  foregroundColor: Colors.black87, // 글자색 및 아이콘 색상
                  padding:
                  const EdgeInsets.symmetric(horizontal: 40, vertical: 15), // 내부 패딩
                  textStyle: const TextStyle(fontSize: 16), // 텍스트 스타일
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Uploaded Document 섹션
            Container( // 업로드된 문서 정보를 표시할 컨테이너
              padding: const EdgeInsets.symmetric(vertical: 15), // 세로 패딩
              alignment: Alignment.center, // 내용을 가운데 정렬
              decoration: BoxDecoration( // 배경색 및 모서리 둥글게 설정
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: const Text(
                'Uploaded Document',
                style: TextStyle(fontSize: 16),
              ),
            ),
            const SizedBox(height: 16),

            // Submission Result 섹션
            Container( // 제출 결과 정보를 표시할 컨테이너
              padding: const EdgeInsets.symmetric(vertical: 15),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: const Text(
                'Submission Result',
                style: TextStyle(fontSize: 16),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
      bottomNavigationBar: BottomAppBar( // 화면 하단에 고정되는 앱 바
        child: Padding( // 내부 패딩
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row( // 버튼들을 가로로 배열
            mainAxisAlignment: MainAxisAlignment.spaceBetween, // 양쪽 끝에 버튼 배치
            children: [
              ElevatedButton( // Add Documents 버튼
                onPressed: () {
                  // TODO: Add Documents 액션 구현 필요
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[300],
                  foregroundColor: Colors.black87,
                ),
                child: const Text('Add Documents'),
              ),
              ElevatedButton( // Exit 버튼
                onPressed: () {
                  // TODO: Exit 액션 구현 필요
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[300],
                  foregroundColor: Colors.black87,
                ),
                child: const Text('Exit'),
              ),
            ],
          ),
        ),
      ),
      // 이미지의 주황색 "NB" 원형 요소들은 디자인 시스템의 일부이거나 커스텀 위젯일 가능성이 높습니다.
      // 이 기본적인 구조 코드에서는 생략되었습니다. 정확하게 구현하려면 별도의 커스텀 페인팅이나 위젯 스택킹이 필요합니다.
    );
  }
}