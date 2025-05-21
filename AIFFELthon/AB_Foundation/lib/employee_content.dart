import 'package:flutter/material.dart';
// document_portal_screen.dart는 더 이상 EmployeeSubViewState를 사용하지 않으므로 임포트 제거
// import 'document_portal_screen.dart'; // EmployeeSubViewState 사용을 위해 임포트
// SavedDocumentsContent와 NewDocumentContent는 이제 이 파일 내부에 통합되므로 임포트 제거
// import 'saved_documents_content.dart';
// import 'new_document_content.dart';

// EmployeeContent를 StatefulWidget으로 변경하여 상태 관리를 합니다.
class EmployeeContent extends StatefulWidget {
  // 부모 위젯에서 전달받는 콜백 함수들 (이제 필요 없으므로 삭제)
  // final VoidCallback onSavedDocumentsPressed;
  // final VoidCallback onNewDocumentPressed;

  // 생성자에서 필수 매개변수 삭제하고 const 생성자로 변경
  const EmployeeContent({
    Key? key,
    // required this.onSavedDocumentsPressed, // 삭제
    // required this.onNewDocumentPressed, // 삭제
  }) : super(key: key);

  @override
  State<EmployeeContent> createState() => _EmployeeContentState();
}

class _EmployeeContentState extends State<EmployeeContent> {
  // 현재 선택된 탭 상태 ('saved' 또는 'new')
  String _selectedTab = 'saved';

  // New Document 탭에서 선택된 비용 유형 상태 ('other' 또는 'business')
  String? _selectedExpenseType; // null이면 아무것도 선택되지 않은 초기 상태

  // New Document 탭의 입력 필드 컨트롤러
  final TextEditingController _otherExpensesApprovalNoController = TextEditingController();
  final TextEditingController _otherExpensesPurposeController = TextEditingController();
  final TextEditingController _businessTripApprovalNoController = TextEditingController();
  final TextEditingController _businessTripPeriodController = TextEditingController();
  final TextEditingController _businessTripCountryController = TextEditingController();
  final TextEditingController _documentMemoController = TextEditingController(); // Document Memo 컨트롤러


  // Saved Documents 탭에 표시될 데이터 (JSON 구조 유지)
  final List<Map<String, dynamic>> savedDocuments = [
    {
      'section': 'Other Expense',
      'rows': [
        ['Archive Doc. No', 'Approval No.', 'Purpose'],
        ['EE258607_2025_0001', 'IA-205138450', 'Purchase of copy papers'],
        ['Submitted', 'your doc. no.1', '15.12.2023 / 13:55:13'],
      ],
    },
    {
      'section': 'Business trip',
      'rows': [
        ['Archive Doc. No', 'Approval No.', 'Period', 'Country'],
        ['EE258607_2025_0002', 'IA-205138450', '19.03.2025 - 30.03.2025', 'UK'],
        ['Saved', 'your doc. no.2', 'Lunch receipt', '-'],
        ['Submitted', 'your doc. no.3', 'Dinner receipt', '22.2.2023 / 15:13'],
        ['EE258607_2025_0003', 'IA-205138460', '01.04.2025 - 05.04.2025', 'Germany'],
        ['Saved', 'your doc. no.4', 'Taxi', '-'],
        ['Saved', 'your doc. no.5', 'Dinner receipt', '-'],
      ],
    },
    {
      'section': 'Not yet submitted Documents',
      'rows': [
        ['Status', 'Document', 'Type', 'Etc'],
        ['Saved', 'your doc. no.2', 'Lunch receipt', '-'],
        ['Saved', 'your doc. no.4', 'Taxi', '-'],
        ['Saved', 'your doc. no.5', 'Dinner receipt', '-'],
      ],
    },
  ];

  @override
  void dispose() {
    // 위젯이 제거될 때 컨트롤러 해제
    _otherExpensesApprovalNoController.dispose();
    _otherExpensesPurposeController.dispose();
    _businessTripApprovalNoController.dispose();
    _businessTripPeriodController.dispose();
    _businessTripCountryController.dispose();
    _documentMemoController.dispose();
    super.dispose();
  }

  // New Document 탭의 입력 필드 및 상태 초기화 메서드
  void _resetNewDocumentForm() {
    _selectedExpenseType = null;
    _otherExpensesApprovalNoController.clear();
    _otherExpensesPurposeController.clear();
    _businessTripApprovalNoController.clear();
    _businessTripPeriodController.clear();
    _businessTripCountryController.clear();
    _documentMemoController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Employee No. 입력 섹션 (Saved/New 탭 공통)
        const Text(
          'Please enter your employee no.',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const TextField( // TODO: 이 TextField에도 컨트롤러가 필요할 수 있습니다.
          decoration: InputDecoration(
            hintText: 'Employee No.',
            border: OutlineInputBorder(),
            isDense: true,
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          ),
        ),
        const SizedBox(height: 24),
        // "To Next Step >>" 텍스트 (Saved/New 탭 공통 - 역할 불분명)
        const Center( // TODO: 이 텍스트의 역할 재검토 필요
          child: Text(
            'To Next Step >>',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 24),
        // "Your document archives" 헤더 (Saved/New 탭 공통)
        const Center(
          child: Text(
            'Your document archives',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 8),
        // Name/ID 섹션 (Saved/New 탭 공통)
        Container(
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey),
            borderRadius: BorderRadius.circular(5.0),
            color: Colors.grey[100],
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(child: Text('Name:')),
                  Expanded(child: Text('Karina Romes')),
                ],
              ),
              SizedBox(height: 5),
              Row(
                children: [
                  Expanded(child: Text('ID:')),
                  Expanded(child: Text('EE258607')),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Saved Documents와 New Document 탭 버튼
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              // onPressed: onSavedDocumentsPressed, // 부모 위젯 콜백 대신 로컬 상태 변경
              onPressed: () {
                setState(() {
                  _selectedTab = 'saved';
                  _resetNewDocumentForm(); // New Document 탭에서 Saved 탭으로 이동 시 폼 초기화
                });
                // 부모 위젯에 Saved 탭 선택 알림 (필요하다면 유지)
                // widget.onSavedDocumentsPressed();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: _selectedTab == 'saved' ? Colors.blue[100] : Colors.grey[300],
                foregroundColor: Colors.black87,
              ),
              child: const Text('Saved Documents'),
            ),
            const SizedBox(width: 16),
            ElevatedButton(
              // onPressed: onNewDocumentPressed, // 부모 위젯 콜백 대신 로컬 상태 변경
              onPressed: () {
                setState(() {
                  _selectedTab = 'new';
                  _resetNewDocumentForm(); // New Document 탭 선택 시 폼 초기화
                });
                // 부모 위젯에 New 탭 선택 알림 (필요하다면 유지)
                // widget.onNewDocumentPressed();
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: _selectedTab == 'new' ? Colors.blue[100] : Colors.grey[300],
                foregroundColor: Colors.black87,
              ),
              child: const Text('New Document'),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // **선택된 탭에 따라 다른 콘텐츠 표시**
        if (_selectedTab == 'saved')
        // Saved Documents 탭 콘텐츠
          _buildSavedDocumentsContent(savedDocuments) // 기존 Saved Documents UI 로직 사용
        else
        // New Document 탭 콘텐츠 (기존 NewDocumentContent 내용을 통합)
          _buildNewDocumentContent(), // New Document UI 로직 호출
      ],
    );
  }

  // ========================================================================
  // Saved Documents 탭 UI 빌드 메서드 (기존 로직 유지)
  // ========================================================================

  Widget _buildSavedDocumentsContent(List<Map<String, dynamic>> sections) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // JSON 데이터 구조를 기반으로 섹션 및 테이블 빌드
        for (final sectionData in sections) ...[
          _buildSavedSectionTitle(sectionData['section']), // 도우미 메서드 사용
          const SizedBox(height: 8),
          // 'Not yet submitted Documents' 섹션은 테이블 구조가 다름
          if (sectionData['section'] == 'Not yet submitted Documents')
            _buildSavedSimpleStatusList(List<List<String>>.from(sectionData['rows'])) // 도우미 메서드 사용
          else
          // 다른 섹션은 JSON rows를 기반으로 테이블을 직접 빌드
            Table(
              columnWidths: const {
                0: IntrinsicColumnWidth(),
                1: FlexColumnWidth(),
              },
              border: TableBorder.all(color: Colors.grey.shade300), // 테이블 경계선 추가
              children: [
                for (final row in List<List<String>>.from(sectionData['rows']))
                  TableRow(
                    children: [
                      for (final cell in row)
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Text(cell, style: row == sectionData['rows'].first ? const TextStyle(fontWeight: FontWeight.bold) : null), // 첫 번째 행은 헤더로 간주
                        ),
                    ],
                  ),
              ],
            ),
          const SizedBox(height: 20), // 각 섹션 하단 간격
        ],
      ],
    );
  }


  // _buildSectionTitle은 Saved Documents 탭에서만 사용되는 도우미 메서드
  Widget _buildSavedSectionTitle(String title) {
    return Container(
      width: double.infinity, // 너비 전체 차지
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      color: Colors.grey.shade400,
      child: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
    );
  }

  // _buildSimpleStatusList는 Saved Documents 탭에서만 사용되는 도우미 메서드
  Widget _buildSavedSimpleStatusList(List<List<String>> rows) {
    return Column(
      children: rows
          .map((row) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 2),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: row.map((item) => Expanded(child: Text(item))).toList(),
        ),
      ))
          .toList(),
    );
  }

  // ========================================================================
  // New Document 탭 UI 빌드 메서드 (기존 NewDocumentContent 내용을 통합)
  // ========================================================================

  Widget _buildNewDocumentContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 10), // 상단 여백

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
                value: 'other', // 값 변경 ('Other Expenses' -> 'other')
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
                  return Colors.black; // 기본 색상
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
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Approval No.'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _otherExpensesApprovalNoController,
                    // Other Expenses 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'other', // 값 변경에 맞춰 조건 수정
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true, // 배경색 채우기
                      fillColor: _selectedExpenseType == 'other' ? Colors.white : Colors.grey[300], // 활성화/비활성화 시 배경색 변경
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Purpose'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _otherExpensesPurposeController,
                    // Other Expenses 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'other', // 값 변경에 맞춰 조건 수정
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true, // 배경색 채우기
                      fillColor: _selectedExpenseType == 'other' ? Colors.white : Colors.grey[300], // 활성화/비활성화 시 배경색 변경
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
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
                value: 'business', // 값 변경 ('Business trip' -> 'business')
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
        // Business trip 데이터 row들
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
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Approval No.'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripApprovalNoController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'business', // 값 변경에 맞춰 조건 수정
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'business' ? Colors.white : Colors.grey[300],
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Period'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripPeriodController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'business', // 값 변경에 맞춰 조건 수정
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'business' ? Colors.white : Colors.grey[300],
                    ),
                  ),
                ),
              ]),
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.only(top: 8.0, bottom: 8.0, right: 8.0),
                  child: Text('Country'),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: TextField(
                    controller: _businessTripCountryController,
                    // Business trip 선택 시에만 enabled
                    enabled: _selectedExpenseType == 'business', // 값 변경에 맞춰 조건 수정
                    decoration: InputDecoration(
                      isDense: true,
                      border: const OutlineInputBorder(),
                      filled: true,
                      fillColor: _selectedExpenseType == 'business' ? Colors.white : Colors.grey[300],
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


        // "Not yet submitted Documents" 섹션 (New Document 탭에서는 삭제)
        // 이 섹션은 New Document 탭에서 필요 없으므로 주석 처리하거나 삭제합니다.
        // const Container(
        //   width: double.infinity,
        //   padding: EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
        //   color: Colors.grey,
        //   child: Text('Not yet submitted Documents', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
        // ),
        // // 데이터 row들 (간단한 예시 구조)
        // const SizedBox(height: 8),
        // const Padding(
        //   padding: EdgeInsets.symmetric(horizontal: 12.0),
        //   child: Row(
        //     children: [
        //       Expanded(flex: 2, child: Text('Saved')),
        //       Expanded(flex: 2, child: Text('your doc. no2.')),
        //       Expanded(flex: 1, child: Text('Lunch receipt')),
        //       Expanded(flex: 1, child: Text('-')),
        //     ],
        //   ),
        // ),
        // const Divider(height: 16),
        // const Padding(
        //   padding: EdgeInsets.symmetric(horizontal: 12.0),
        //   child: Row(
        //     children: [
        //       Expanded(flex: 2, child: Text('Saved')),
        //       Expanded(flex: 2, child: Text('your doc. no4.')),
        //       Expanded(flex: 1, child: Text('Taxi')),
        //       Expanded(flex: 1, child: Text('-')),
        //     ],
        //   ),
        // ),
        // const Divider(height: 16),
        // const Padding(
        //   padding: EdgeInsets.symmetric(horizontal: 12.0),
        //   child: Row(
        //     children: [
        //       Expanded(flex: 2, child: Text('Saved')),
        //       Expanded(flex: 2, child: Text('your doc. no5.')),
        //       Expanded(flex: 1, child: Text('Dinner receipt')),
        //       Expanded(flex: 1, child: Text('-')),
        //     ],
        //   ),
        // ),
        // const SizedBox(height: 20),

        // TODO: New Document 탭에 필요한 추가 UI 요소 (예: 파일 업로드, 제출 버튼 등)는
        // BusinessCounterpartyContent에서 옮겨오거나 새로 구현해야 합니다.
        // 현재는 입력 필드와 라디오 버튼만 포함합니다.
      ],
    );
  }
}
