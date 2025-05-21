import 'package:flutter/material.dart';

// NewDocumentContent를 StatefulWidget으로 변경하여 상태 관리를 할 수 있도록 합니다.
class NewDocumentContent extends StatefulWidget {
  const NewDocumentContent({Key? key}) : super(key: key);

  @override
  _NewDocumentContentState createState() => _NewDocumentContentState();
}

// State 클래스
class _NewDocumentContentState extends State<NewDocumentContent> {
  // 라디오 버튼 선택 상태를 관리할 변수
  // null이면 아무것도 선택되지 않은 초기 상태를 의미합니다.
  String? _selectedExpenseType; // 'Other Expenses' 또는 'Business trip'

  // 입력 필드 컨트롤러
  final TextEditingController _otherExpensesApprovalNoController = TextEditingController();
  final TextEditingController _otherExpensesPurposeController = TextEditingController();
  final TextEditingController _businessTripApprovalNoController = TextEditingController();
  final TextEditingController _businessTripPeriodController = TextEditingController();
  final TextEditingController _businessTripCountryController = TextEditingController();
  final TextEditingController _documentMemoController = TextEditingController(); // Document Memo 컨트롤러

  @override
  void dispose() {
    // 위젯이 제거될 때 컨트롤러 해제하여 메모리 누수 방지
    _otherExpensesApprovalNoController.dispose();
    _otherExpensesPurposeController.dispose();
    _businessTripApprovalNoController.dispose();
    _businessTripPeriodController.dispose();
    _businessTripCountryController.dispose();
    _documentMemoController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 10),

        // **Other Expenses 섹션 헤더 및 라디오 버튼**
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
          color: Colors.grey,
          child: Row( // 라디오 버튼과 텍스트를 가로로 배열
            children: [
              Expanded( // 텍스트가 남은 공간을 차지하도록 Expanded 사용
                child: const Text(
                  'Other Expenses',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ),
              Radio<String>( // Other Expenses 라디오 버튼
                value: 'Other Expenses',
                groupValue: _selectedExpenseType, // 현재 선택된 값
                onChanged: (String? value) { // 라디오 버튼 선택 시 상태 업데이트
                  setState(() {
                    _selectedExpenseType = value;
                    // 다른 섹션 입력 필드 초기화 (선택 사항)
                    _businessTripApprovalNoController.clear();
                    _businessTripPeriodController.clear();
                    _businessTripCountryController.clear();
                  });
                },
                activeColor: Colors.white, // 선택 시 색상
                fillColor: MaterialStateProperty.resolveWith<Color>((Set<MaterialState> states) {
                  if (states.contains(MaterialState.selected)) {
                    return Colors.white; // 선택 시 흰색
                  }
                  return Colors.black; // 기본 색상 (회색 배경에 검은색이면 잘 안 보일 수 있음)
                }),
              ),
            ],
          ),
        ),
        // Other Expenses 데이터 row들
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0),
          child: Table( // 테이블 사용하여 라벨과 입력 필드 정렬
            columnWidths: const {
              0: IntrinsicColumnWidth(), // 라벨 컬럼
              1: FlexColumnWidth(), // 입력 필드 컬럼
            },
            defaultVerticalAlignment: TableCellVerticalAlignment.middle, // 세로 가운데 정렬
            children: [
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Archive Doc. No'),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: Text('EE258607_2023_0001'), // 고정된 값
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Approval No.'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _otherExpensesApprovalNoController,
                    // Other Expenses 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'Other Expenses',
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true, // 배경색 채우기
                      fillColor: _selectedExpenseType == 'Other Expenses' ? Colors.white : Colors.grey[300], // 활성화/비활성화 시 배경색 변경
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Purpose'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _otherExpensesPurposeController,
                    // Other Expenses 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'Other Expenses',
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true, // 배경색 채우기
                      fillColor: _selectedExpenseType == 'Other Expenses' ? Colors.white : Colors.grey[300], // 활성화/비활성화 시 배경색 변경
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Submitted'),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: Text('15.12.2023 / 13:55:13'), // 고정된 값
                ),
              ]),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // **Business trip 섹션 헤더 및 라디오 버튼**
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
          color: Colors.grey,
          child: Row( // 라디오 버튼과 텍스트를 가로로 배열
            children: [
              Expanded( // 텍스트가 남은 공간을 차지하도록 Expanded 사용
                child: const Text(
                  'Business trip',
                  style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                ),
              ),
              Radio<String>( // Business trip 라디오 버튼
                value: 'Business trip',
                groupValue: _selectedExpenseType, // 현재 선택된 값
                onChanged: (String? value) { // 라디오 버튼 선택 시 상태 업데이트
                  setState(() {
                    _selectedExpenseType = value;
                    // 다른 섹션 입력 필드 초기화 (선택 사항)
                    _otherExpensesApprovalNoController.clear();
                    _otherExpensesPurposeController.clear();
                  });
                },
                activeColor: Colors.white, // 선택 시 색상
                fillColor: MaterialStateProperty.resolveWith<Color>((Set<MaterialState> states) {
                  if (states.contains(MaterialState.selected)) {
                    return Colors.white; // 선택 시 흰색
                  }
                  return Colors.black; // 기본 색상
                }),
              ),
            ],
          ),
        ),
        // Business trip 데이터 row들 (간단한 예시 구조)
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0),
          child: Table( // 테이블 사용하여 라벨과 입력 필드 정렬
            columnWidths: const {
              0: IntrinsicColumnWidth(), // 라벨 컬럼
              1: FlexColumnWidth(), // 입력 필드 컬럼
            },
            defaultVerticalAlignment: TableCellVerticalAlignment.middle, // 세로 가운데 정렬
            children: [
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Archive Doc. No'),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8.0),
                  child: Text('EE258607_2025_0002'), // 고정 값
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Approval No.'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripApprovalNoController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'Business trip',
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'Business trip' ? Colors.white : Colors.grey[300],
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Period'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripPeriodController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'Business trip',
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'Business trip' ? Colors.white : Colors.grey[300],
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                // 수정: EdgeInsets.symmetric(vertical: 8.0, right: 8.0) -> EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0)
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Country'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripCountryController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'Business trip',
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'Business trip' ? Colors.white : Colors.grey[300],
                    ),
                  ),
                ),
              ]),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // **Document Memo 섹션 (항상 입력 가능)**
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
          color: Colors.grey,
          child: const Text(
            'Document Memo', // Document Memo 헤더 텍스트 변경
            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
          ),
        ),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12.0),
          child: TextField(
            controller: _documentMemoController, // Document Memo 컨트롤러 연결
            maxLines: 3, // 여러 줄 입력 가능하도록 설정
            // Document Memo는 항상 enabled
            enabled: true,
            decoration: InputDecoration(
              isDense: true,
              border: const OutlineInputBorder(),
              filled: true, // 배경색 채우기
              fillColor: Colors.white, // 항상 흰색 배경
              hintText: 'Enter memo here...', // 힌트 텍스트 추가
            ),
          ),
        ),
        const SizedBox(height: 20),


        // "Not yet submitted Documents" 섹션 (이전 내용 유지)
        // 여기서 const 키워드를 제거합니다.
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
          color: Colors.grey,
          child: const Text('Not yet submitted Documents', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        ),
        // 데이터 row들 (간단한 예시 구조)
        const SizedBox(height: 8),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 12.0),
          child: Row(
            children: [
              Expanded(flex: 2, child: Text('Saved')),
              Expanded(flex: 2, child: Text('your doc. no2.')),
              Expanded(flex: 1, child: Text('Lunch receipt')),
              Expanded(flex: 1, child: Text('-')),
            ],
          ),
        ),
        const Divider(height: 16),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 12.0),
          child: Row(
            children: [
              Expanded(flex: 2, child: Text('Saved')),
              Expanded(flex: 2, child: Text('your doc. no4.')),
              Expanded(flex: 1, child: Text('Taxi')),
              Expanded(flex: 1, child: Text('-')),
            ],
          ),
        ),
        const Divider(height: 16),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 12.0),
          child: Row(
            children: [
              Expanded(flex: 2, child: Text('Saved')),
              Expanded(flex: 2, child: Text('your doc. no5.')),
              Expanded(flex: 1, child: Text('Dinner receipt')),
              Expanded(flex: 1, child: Text('-')),
            ],
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}
