import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart'; // file_picker 임포트

// BusinessCounterpartyContent를 StatefulWidget으로 변경하여 상태 관리를 합니다.
class BusinessCounterpartyContent extends StatefulWidget {
  // GlobalKey를 사용하여 외부에서 상태에 접근할 수 있도록 합니다.
  const BusinessCounterpartyContent({Key? key}) : super(key: key);

  @override
  // State 클래스의 이름을 public으로 변경합니다.
  BusinessCounterpartyContentState createState() => BusinessCounterpartyContentState();
}

// State 클래스의 이름을 public으로 변경합니다. (앞의 '_' 제거)
class BusinessCounterpartyContentState extends State<BusinessCounterpartyContent> {
  // 입력 필드 컨트롤러
  final TextEditingController _companyNameController = TextEditingController();
  final TextEditingController _businessNumberController = TextEditingController();
  final TextEditingController _representativeNameController = TextEditingController();
  final TextEditingController _addressController = TextEditingController();
  final TextEditingController _contactPersonController = TextEditingController();
  final TextEditingController _contactNumberController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _bankNameController = TextEditingController();
  final TextEditingController _accountNumberController = TextEditingController();
  final TextEditingController _swiftCodeController = TextEditingController();
  final TextEditingController _paymentTermsController = TextEditingController();
  final TextEditingController _currencyController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  // 파일 업로드를 위한 변수
  List<PlatformFile>? _selectedFiles; // 선택된 파일 목록을 저장

  @override
  void dispose() {
    // 위젯이 제거될 때 컨트롤러 해제
    _companyNameController.dispose();
    _businessNumberController.dispose();
    _representativeNameController.dispose();
    _addressController.dispose();
    _contactPersonController.dispose();
    _contactNumberController.dispose();
    _emailController.dispose();
    _bankNameController.dispose();
    _accountNumberController.dispose();
    _swiftCodeController.dispose();
    _paymentTermsController.dispose();
    _currencyController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  // 파일 선택 함수
  Future<void> _pickFiles() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      allowMultiple: true, // 여러 파일 선택 허용
      type: FileType.any, // 모든 파일 타입 허용 (image, video, audio, custom 등 지정 가능)
    );

    if (result != null) {
      setState(() {
        _selectedFiles = result.files;
      });
    } else {
      // 사용자가 파일 선택을 취소한 경우
      setState(() {
        _selectedFiles = null; // 선택 취소 시 파일 목록 초기화
      });
    }
  }

  // 외부에서 호출 가능한 메서드 (예: DocumentPortalScreen에서 GlobalKey를 통해 호출)
  void addInsertTime() {
    // TODO: 여기에 Insert Time을 추가하는 로직 구현
    print("addInsertTime called in BusinessCounterpartyContentState");
    // 예시: notes 필드에 현재 시간을 추가
    // _notesController.text += "\nInsert Time: ${DateTime.now()}";
  }

  // 외부에서 호출 가능한 메서드 (예: DocumentPortalScreen에서 GlobalKey를 통해 호출)
  void resetForm() {
    // 입력 필드 초기화
    _companyNameController.clear();
    _businessNumberController.clear();
    _representativeNameController.clear();
    _addressController.clear();
    _contactPersonController.clear();
    _contactNumberController.clear();
    _emailController.clear();
    _bankNameController.clear();
    _accountNumberController.clear();
    _swiftCodeController.clear();
    _paymentTermsController.clear();
    _currencyController.clear();
    _notesController.clear();
    // 파일 선택 상태 초기화
    setState(() {
      _selectedFiles = null;
    });
    print("resetForm called in BusinessCounterpartyContentState");
  }

  // 외부에서 호출 가능한 메서드 (예: DocumentPortalScreen에서 GlobalKey를 통해 호출)
  void collectInitialDataAndDisplay() {
    // TODO: 여기에 초기 데이터를 수집하고 표시하는 로직 구현
    print("collectInitialDataAndDisplay called in BusinessCounterpartyContentState");
    // 예시: 현재 입력된 값을 출력
    print('Company Name: ${_companyNameController.text}');
    print('Business Number: ${_businessNumberController.text}');
    // ... 나머지 필드 값 출력 ...
    if (_selectedFiles != null) {
      print('Selected Files: ${_selectedFiles!.map((f) => f.name).join(', ')}');
    }
  }


  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: ListView( // 스크롤 가능하도록 ListView 사용
        children: [
          const Text(
            'Business Counterparty Information',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          // Company Name
          const Text('Company Name', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _companyNameController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Business Number
          const Text('Business Number', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _businessNumberController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Representative Name
          const Text('Representative Name', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _representativeNameController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Address
          const Text('Address', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _addressController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            maxLines: 2,
          ),
          const SizedBox(height: 16),

          // Contact Person
          const Text('Contact Person', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _contactPersonController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Contact Number
          const Text('Contact Number', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _contactNumberController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            keyboardType: TextInputType.phone,
          ),
          const SizedBox(height: 16),

          // Email
          const Text('Email', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _emailController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            keyboardType: TextInputType.emailAddress,
          ),
          const SizedBox(height: 16),

          // Bank Information Header
          const Text(
            'Bank Information',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          // Bank Name
          const Text('Bank Name', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _bankNameController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Account Number
          const Text('Account Number', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _accountNumberController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            keyboardType: TextInputType.number,
          ),
          const SizedBox(height: 16),

          // SWIFT Code
          const Text('SWIFT Code', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _swiftCodeController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Payment Terms
          const Text('Payment Terms', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _paymentTermsController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Currency
          const Text('Currency', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _currencyController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
          ),
          const SizedBox(height: 16),

          // Notes
          const Text('Notes', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextField(
            controller: _notesController,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              isDense: true,
              contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            maxLines: 3,
          ),
          const SizedBox(height: 24),

          // ** 파일 업로드 섹션 **
          const Text('Upload Files', style: TextStyle(fontWeight: FontWeight.bold)), // 파일 업로드 섹션 헤더
          const SizedBox(height: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ElevatedButton(
                onPressed: _pickFiles, // 파일 선택 함수 호출
                child: const Text('Upload'), // 버튼 이름 변경
              ),
              const SizedBox(height: 8),
              // 선택된 파일 이름 목록 표시
              if (_selectedFiles != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: _selectedFiles!.map((file) => Text(file.name)).toList(),
                ),
            ],
          ),
          const SizedBox(height: 24),


          // Save Button (예시)
          Center(
            child: ElevatedButton(
              onPressed: () {
                // TODO: 입력된 정보와 선택된 파일들을 처리하는 로직 구현
                print('Company Name: ${_companyNameController.text}');
                print('Business Number: ${_businessNumberController.text}');
                // ... 나머지 필드 값 출력 ...
                if (_selectedFiles != null) {
                  print('Selected Files: ${_selectedFiles!.map((f) => f.name).join(', ')}');
                }
                // 여기에 데이터 저장 또는 전송 로직을 추가합니다.
              },
              child: const Text('Save Counterparty'),
            ),
          ),
          const SizedBox(height: 24), // 하단 여백
        ],
      ),
    );
  }
}
