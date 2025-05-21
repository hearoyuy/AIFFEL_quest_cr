import 'package:flutter/material.dart';
import 'app_bar_widget.dart';
import 'business_entity_section.dart';
import 'relation_section.dart';
import 'employee_content.dart'; // Employee 콘텐츠 위젯 (Placeholder가 들어있음)
import 'business_counterparty_content.dart'; // Business Counterparty 콘텐츠 위젯 (상세 입력 폼 + Upload/Table 기능이 들어있음)
import 'bottom_bar_widget.dart'; // CustomBottomBar 임포트

// 화면 하단에 표시될 콘텐츠의 주요 상태
enum ViewState {
  initial, // 초기 상태 (하단 내용 숨김)
  employee, // Employee 선택 시 (Placeholder 표시)
  businessCounterparty, // Business Counterparty 선택 시 (상세 입력 폼 표시)
}

// Business Counterparty 선택 시 하단 콘텐츠 중 일부의 서브 상태 (Archives UI 내부)
// 현재 BusinessCounterpartyContent는 Archives UI가 아닌 상세 폼이라 사용되지 않음
enum ArchivesSubViewState {
  savedDocuments, // Saved Documents 탭/클릭 시
  newDocument, // New Document 탭/클릭 시 (새 이미지 내용)
}

class DocumentPortalScreen extends StatefulWidget {
  const DocumentPortalScreen({Key? key}) : super(key: key);

  @override
  _DocumentPortalScreenState createState() => _DocumentPortalScreenState();
}

class _DocumentPortalScreenState extends State<DocumentPortalScreen> {
  bool _isEmployeeChecked = false;
  bool _isBusinessCounterpartyChecked = false;

  ViewState _currentViewState = ViewState.initial;
  // Business Counterparty 선택 시 사용될 Archives UI 내부의 서브 상태 관리 변수
  // 현재 BusinessCounterpartyContent는 Archives UI가 아닌 상세 폼이라 이 변수는 사용되지 않음
  ArchivesSubViewState _archivesSubViewState = ArchivesSubViewState.savedDocuments;

  // BusinessCounterpartyContent의 상태에 접근하기 위해 GlobalKey 사용
  // GlobalKey 타입 인자를 public으로 변경된 BusinessCounterpartyContentState로 수정
  final GlobalKey<BusinessCounterpartyContentState> _businessCounterpartyContentKey = GlobalKey<BusinessCounterpartyContentState>();


  // Relation 섹션 체크박스 상태 변경 콜백
  void _onRelationCheckboxChanged({bool? isEmployee, bool? isBusinessCounterparty}) {
    setState(() {
      if (isEmployee != null) {
        _isEmployeeChecked = isEmployee;
        if (_isEmployeeChecked) {
          _isBusinessCounterpartyChecked = false; // Employee 선택 시 Business Counterparty 해제
        }
      }
      if (isBusinessCounterparty != null) {
        _isBusinessCounterpartyChecked = isBusinessCounterparty;
        if (_isBusinessCounterpartyChecked) {
          _isEmployeeChecked = false; // Business Counterparty 선택 시 Employee 해제
        }
      }
      // 체크 상태 변경 시 하단 내용 초기화
      _currentViewState = ViewState.initial;
      // 서브 상태도 초기화
      _archivesSubViewState = ArchivesSubViewState.savedDocuments;
    });
  }

  // Relation 섹션 "To Next Step" 버튼 콜백 (Relation 섹션 아래 버튼)
  void _onRelationNextStepPressed() {
    setState(() {
      if (_isEmployeeChecked) {
        // **Employee 체크 시 ViewState.employee로 설정 (EmployeeContent 표시)**
        _currentViewState = ViewState.employee; // ViewState.employee로 설정 (Placeholder 표시)
        // ArchivesSubViewState는 ViewState.businessCounterparty일 때 사용되므로, 여기서 초기화하지 않음
      } else if (_isBusinessCounterpartyChecked) {
        // **Business Counterparty 체크 시 ViewState.businessCounterparty로 설정 (BusinessCounterpartyContent 표시)**
        _currentViewState = ViewState.businessCounterparty; // ViewState.businessCounterparty로 설정 (상세 입력 폼 표시)
        // Business Counterparty 선택 시 하단 콘텐츠의 서브 상태 초기화 ( Archives UI 였다면 필요)
        _archivesSubViewState = ArchivesSubViewState.savedDocuments;
      } else {
        // 어떤 체크박스도 선택되지 않았을 경우 메시지 표시
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please select your relation.')),
        );
        _currentViewState = ViewState.initial; // 상태 초기화
        _archivesSubViewState = ArchivesSubViewState.savedDocuments; // 서브 상태 초기화
      }
    });
  }

  // Business Counterparty 선택 시 "Add Documents" 버튼 기능 (CustomBottomBar에서 호출됨)
  void _onAddDocumentsPressedForBusinessCounterparty() {
    // BusinessCounterpartyContent 위젯의 상태에 접근하여 addInsertTime 메서드를 호출합니다.
    final businessCounterpartyState = _businessCounterpartyContentKey.currentState;

    if (businessCounterpartyState != null) {
      // public으로 변경된 addInsertTime 메서드 호출
      businessCounterpartyState.addInsertTime();
    } else {
      print("BusinessCounterpartyContent state is not available.");
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please ensure the form is visible first.')),
      );
    }
  }


  // Business Counterparty 선택 시 "Exit" 버튼 기능 (CustomBottomBar에서 호출됨)
  void _onExitPressedForBusinessCounterparty() {
    // BusinessCounterpartyContent 위젯의 상태를 초기화합니다.
    _businessCounterpartyContentKey.currentState?.resetForm(); // public으로 변경된 resetForm 메서드 호출

    setState(() {
      // Exit 버튼 클릭 시 초기 상태(ViewState.initial)로 돌아가도록 설정
      _currentViewState = ViewState.initial;
      // 초기 상태로 돌아갈 때 필요하다면 체크박스 상태 및 서브 상태 초기화
      _isEmployeeChecked = false; // 체크박스 상태 초기화
      _isBusinessCounterpartyChecked = false; // 체크박스 상태 초기화
      _archivesSubViewState = ArchivesSubViewState.savedDocuments; // 서브 상태 초기화
    });
    print("Exit button pressed. Returning to initial state.");
  }

  // Business Counterparty 선택 시 "To Next Step >>" 버튼 기능 (CustomBottomBar에서 호출됨)
  void _onToNextStepPressedForBusinessCounterparty() {
    // BusinessCounterpartyContent 위젯의 상태에 접근하여 collectInitialDataAndDisplay 메서드를 호출합니다.
    final businessCounterpartyState = _businessCounterpartyContentKey.currentState;

    if (businessCounterpartyState != null) {
      // public으로 변경된 collectInitialDataAndDisplay 메서드 호출
      businessCounterpartyState.collectInitialDataAndDisplay();
    } else {
      print("BusinessCounterpartyContent state is not available.");
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please ensure the form is visible first.')),
      );
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(), // 상단 앱 바
      body: SingleChildScrollView( // 스크롤 가능한 본문
        padding: const EdgeInsets.all(16.0),
        child: Column( // 본문 내용을 세로로 배열
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Center( // 제목 "Document Portal"
              child: Text(
                'Document Portal',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),

            const BusinessEntitySection(), // Business Entity 섹션
            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            RelationSection( // Relation 섹션
              isEmployeeChecked: _isEmployeeChecked,
              isBusinessCounterpartyChecked: _isBusinessCounterpartyChecked,
              onCheckboxChanged: _onRelationCheckboxChanged,
              onNextStepPressed: _onRelationNextStepPressed,
            ),
            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            // **_currentViewState에 따라 다른 하단 콘텐츠를 조건부로 표시**
            if (_currentViewState == ViewState.employee)
            // ViewState.employee 일 때 (Employee 체크 시) EmployeeContent 표시 (Placeholder)
              const EmployeeContent(), // EmployeeContent는 상태나 콜백이 필요 없음
            if (_currentViewState == ViewState.businessCounterparty)
            // ViewState.businessCounterparty 일 때 (Business Counterparty 체크 시) BusinessCounterpartyContent 표시 (상세 입력 폼)
              BusinessCounterpartyContent(
                key: _businessCounterpartyContentKey, // GlobalKey 연결
                // 하단 버튼이 CustomBottomBar로 이동했으므로 여기서 콜백 전달 안 함
              ),

            // 초기 상태일 때는 아무 내용도 표시되지 않음
          ],
        ),
      ),
      // 하단 버튼 바는 ViewState.businessCounterparty 일 때만 보이도록 조건부 렌더링
      bottomNavigationBar: CustomBottomBar(
        currentViewState: _currentViewState,
        // Business Counterparty 선택 시 필요한 콜백들을 CustomBottomBar로 전달
        onAddDocumentsPressed: _currentViewState == ViewState.businessCounterparty ? _onAddDocumentsPressedForBusinessCounterparty : null,
        onExitPressed: _currentViewState == ViewState.businessCounterparty ? _onExitPressedForBusinessCounterparty : null,
        onToNextStepPressed: _currentViewState == ViewState.businessCounterparty ? _onToNextStepPressedForBusinessCounterparty : null,
      ),
    );
  }
}

// BusinessCounterpartyContentState에 대한 확장 (public 메서드 정의)
// 이 확장은 BusinessCounterpartyContentState가 public으로 변경된 후에 사용 가능합니다.
// extension BusinessCounterpartyContentStateExtension on BusinessCounterpartyContentState {
//   // resetForm 메서드는 이제 BusinessCounterpartyContentState 클래스 자체에 public으로 정의되었습니다.
// }