import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AB Foundation Document Portal',
      theme: ThemeData(
        primarySwatch: Colors.grey,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const DocumentPortalScreen(),
    );
  }
}

// 메인 문서 포털 화면 (StatefulWidget 유지)
class DocumentPortalScreen extends StatefulWidget {
  const DocumentPortalScreen({Key? key}) : super(key: key);

  @override
  _DocumentPortalScreenState createState() => _DocumentPortalScreenState();
}

class _DocumentPortalScreenState extends State<DocumentPortalScreen> {
  bool _isEmployeeChecked = false;
  bool _isBusinessCounterpartyChecked = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () {
              // TODO: Implement drawer opening
            },
          ),
        ),
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'AB Foundation',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            Text(
              'the origination of your financial administration',
              style: TextStyle(fontSize: 10),
            ),
          ],
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 1,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Center(
              child: Text(
                'Document Portal',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 20),

            // Select Business Entity Section
            const Text(
              'Please select the business entity to whom your document to be submitted.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            TextField(
              decoration: InputDecoration(
                hintText: 'Business Entity Name',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(5.0),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Colors.grey[200],
                contentPadding:
                const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0),
                suffixIcon: const Icon(Icons.search),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
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
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  // TODO: Implement first next step action if needed
                },
                child: const Text(
                  'To Next Step >>',
                  style: TextStyle(color: Colors.black),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            // Relation Section (화면 전환 로직 추가)
            const Text(
              'Please let us know your relation with the entity.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Checkbox(
                      value: _isEmployeeChecked,
                      onChanged: (bool? newValue) {
                        setState(() {
                          _isEmployeeChecked = newValue ?? false;
                          if (_isEmployeeChecked) {
                            _isBusinessCounterpartyChecked = false;
                          }
                        });
                      },
                    ),
                    const Text('Employee'),
                  ],
                ),
                const SizedBox(width: 20),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Checkbox(
                      value: _isBusinessCounterpartyChecked,
                      onChanged: (bool? newValue) {
                        setState(() {
                          _isBusinessCounterpartyChecked = newValue ?? false;
                          if (_isBusinessCounterpartyChecked) {
                            _isEmployeeChecked = false;
                          }
                        });
                      },
                    ),
                    const Text('Business Counterparty'),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  // **여기서 체크 상태에 따라 다른 화면으로 이동**
                  if (_isEmployeeChecked) {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const EmployeeScreen()),
                    );
                  } else if (_isBusinessCounterpartyChecked) {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const BusinessCounterpartyScreen()),
                    );
                  } else {
                    // 어떤 체크박스도 선택되지 않았을 경우 처리 (예: 메시지 표시)
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please select your relation.')),
                    );
                  }
                },
                child: const Text(
                  'To Next Step >>',
                  style: TextStyle(color: Colors.black),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            // Submit Document Section (이하 이전 코드와 동일)
            const Text(
              'Please submit your document.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(flex: 1, child: Text('Counterparty No.')),
                      Expanded(flex: 2, child: Text('123-4564')),
                    ],
                  ),
                  SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(flex: 1, child: Text('Purchase Order No.')),
                      Expanded(flex: 2,  child: Text('N/A')),
                    ],
                  ),
                  SizedBox(height: 8),
                  Row(
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
            Center(
              child: ElevatedButton.icon(
                onPressed: () {
                  // TODO: Implement upload action
                },
                icon: const Icon(Icons.file_upload),
                label: const Text('Upload'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[300],
                  foregroundColor: Colors.black87,
                  padding:
                  const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  textStyle: const TextStyle(fontSize: 16),
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Uploaded Document Section
            Container(
              padding: const EdgeInsets.symmetric(vertical: 15),
              alignment: Alignment.center,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(5.0),
              ),
              child: const Text(
                'Uploaded Document',
                style: TextStyle(fontSize: 16),
              ),
            ),
            const SizedBox(height: 16),

            // Submission Result Section
            Container(
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
      bottomNavigationBar: BottomAppBar(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              ElevatedButton(
                onPressed: () {
                  // TODO: Implement Add Documents action
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey[300],
                  foregroundColor: Colors.black87,
                ),
                child: const Text('Add Documents'),
              ),
              ElevatedButton(
                onPressed: () {
                  // TODO: Implement Exit action
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
    );
  }
}

// Employee 정보를 보여줄 간단한 화면
class EmployeeScreen extends StatelessWidget {
  const EmployeeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Employee Information'),
      ),
      body: const Center(
        child: Text(
          'This is the Employee screen.',
          style: TextStyle(fontSize: 20),
        ),
      ),
    );
  }
}

// Business Counterparty 정보를 보여줄 간단한 화면
class BusinessCounterpartyScreen extends StatelessWidget {
  const BusinessCounterpartyScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Business Counterparty Information'),
      ),
      body: const Center(
        child: Text(
          'This is the Business Counterparty screen.',
          style: TextStyle(fontSize: 20),
        ),
      ),
    );
  }
}