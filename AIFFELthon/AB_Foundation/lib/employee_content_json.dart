import 'package:flutter/material.dart';

class EmployeeContent extends StatefulWidget {
  const EmployeeContent({Key? key}) : super(key: key);

  @override
  State<EmployeeContent> createState() => _EmployeeContentState();
}

class _EmployeeContentState extends State<EmployeeContent> {
  String _selectedTab = 'saved';
  String _selectedExpenseType = 'business';

  final List<Map<String, dynamic>> savedDocuments = [
    {
      'section': 'Other Expense',
      'docNo': 'EE258607_2025_0001',
      'approvalNo': 'IA-205138450',
      'purpose': 'Purchase of copy papers',
      'statusRows': [
        ['Submitted', 'your doc. no.1', '15.12.2023 / 13:55:13']
      ]
    },
    {
      'section': 'Business trip',
      'docNo': 'EE258607_2025_0002',
      'approvalNo': 'IA-205138450',
      'period': '19.03.2025 - 30.03.2025',
      'country': 'UK',
      'statusRows': [
        ['Saved', 'your doc. no.2', 'Lunch receipt', '-'],
        ['Submitted', 'your doc. no.3', 'Dinner receipt', '22.2.2023 / 15:13']
      ]
    },
    {
      'docNo': 'EE258607_2025_0003',
      'approvalNo': 'IA-205138460',
      'period': '01.04.2025 - 05.04.2025',
      'country': 'Germany',
      'statusRows': [
        ['Saved', 'your doc. no.4', 'Taxi', '-'],
        ['Saved', 'your doc. no.5', 'Dinner receipt', '-']
      ]
    },
  ];

  final List<List<String>> notSubmitted = [
    ['Saved', 'your doc. no.2', 'Lunch receipt', '-'],
    ['Saved', 'your doc. no.4', 'Taxi', '-'],
    ['Saved', 'your doc. no.5', 'Dinner receipt', '-'],
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Please enter your employee no.',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        TextField(
          decoration: const InputDecoration(
            hintText: 'Employee No.',
            border: OutlineInputBorder(),
            isDense: true,
            contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
          ),
        ),
        const SizedBox(height: 24),
        const Center(
          child: Text(
            'To Next Step >>',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        const SizedBox(height: 24),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildTabButton('saved', 'Saved Documents', Colors.blue[100]),
            const SizedBox(width: 16),
            _buildTabButton('new', 'New Document', Colors.red[300]),
          ],
        ),
        const SizedBox(height: 20),
        if (_selectedTab == 'saved') ...[
          for (final doc in savedDocuments) ...[
            if (doc.containsKey('section')) _buildSectionTitle(doc['section']),
            _buildDocumentTable(
              docNo: doc['docNo'],
              approvalNo: doc['approvalNo'],
              purpose: doc['purpose'],
              period: doc['period'],
              country: doc['country'],
              statusRows: List<List<String>>.from(doc['statusRows']),
            ),
            const SizedBox(height: 20),
          ],
          _buildSectionTitle('Not yet submitted Documents'),
          _buildSimpleStatusList(notSubmitted),
        ] else ...[
          const Divider(),
          Row(
            children: [
              Radio<String>(
                value: 'other',
                groupValue: _selectedExpenseType,
                onChanged: (value) {
                  setState(() {
                    _selectedExpenseType = value!;
                  });
                },
              ),
              const Text('Other expense', style: TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
          // New Document input 섹션 등 나중에 추가 가능
        ],
      ],
    );
  }

  Widget _buildTabButton(String tab, String label, Color? selectedColor) {
    final bool isSelected = _selectedTab == tab;
    return ElevatedButton(
      onPressed: () {
        setState(() {
          _selectedTab = tab;
        });
      },
      style: ElevatedButton.styleFrom(
        backgroundColor: isSelected ? selectedColor : Colors.grey[300],
        foregroundColor: Colors.black87,
      ),
      child: Text(label),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      color: Colors.grey.shade400,
      child: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildDocumentTable({
    required String docNo,
    required String approvalNo,
    String? purpose,
    String? period,
    String? country,
    required List<List<String>> statusRows,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Table(
          columnWidths: const {
            0: IntrinsicColumnWidth(),
            1: FlexColumnWidth(),
          },
          children: [
            TableRow(children: [
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 6),
                child: Text('Archive Doc. No', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Text(docNo),
              ),
            ]),
            TableRow(children: [
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 6),
                child: Text('Approval No.', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Text(approvalNo),
              ),
            ]),
            if (purpose != null)
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 6),
                  child: Text('Purpose', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Text(purpose),
                ),
              ]),
            if (period != null)
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 6),
                  child: Text('Period', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Text(period),
                ),
              ]),
            if (country != null)
              TableRow(children: [
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 6),
                  child: Center(child: Text('Country', style: TextStyle(fontWeight: FontWeight.bold))),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 6),
                  child: Text(country),
                ),
              ]),
          ],
        ),
        const SizedBox(height: 10),
        for (final row in statusRows)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: row.map((item) => Expanded(child: Text(item))).toList(),
            ),
          ),
      ],
    );
  }

  Widget _buildSimpleStatusList(List<List<String>> rows) {
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
}
