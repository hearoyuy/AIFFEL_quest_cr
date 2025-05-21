import 'package:flutter/material.dart';

class SavedDocumentsContent extends StatelessWidget {
  const SavedDocumentsContent({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Approval No., Purpose, Business trip 등 정보 (image_536ef3.png 기반 리스트)
        Container(
          padding: const EdgeInsets.all(12.0),
          decoration: BoxDecoration(
              border: Border.all(color: Colors.grey),
              borderRadius: BorderRadius.circular(5.0),
              color: Colors.white // 이미지와 동일하게 흰색 배경
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(flex: 1, child: Text('Approval No.')),
                  Expanded(flex: 2, child: Text('LK-2021-38456')),
                ],
              ),
              SizedBox(height: 8),
              Divider(height: 1),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(flex: 1, child: Text('Purpose')),
                  Expanded(flex: 2, child: Text('Purchase of copy papers')),
                ],
              ),
              SizedBox(height: 8),
              Divider(height: 1),
              SizedBox(height: 8),
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(flex: 1, child: Row(children: [Icon(Icons.business_center, size: 18), SizedBox(width: 4), Text('Business trip')])),
                  Expanded(flex: 2, child: SizedBox.shrink()), // 오른쪽은 비워둠
                ],
              ),
              SizedBox(height: 8),
              Divider(height: 1),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(flex: 1, child: Text('Approval No.')),
                  Expanded(flex: 2, child: Text('LK-2021-38456')),
                ],
              ),
              SizedBox(height: 8),
              Divider(height: 1),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(flex: 1, child: Text('Period')),
                  Expanded(flex: 2, child: Text('15/01/2021 - 30/11/2021')),
                ],
              ),
              SizedBox(height: 8),
              Divider(height: 1),
              SizedBox(height: 8),
              Row(
                children: [
                  Expanded(flex: 1, child: Text('Country')),
                  Expanded(flex: 2, child: Text('United Kingdom')),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Upload 섹션
        Center(
          child: ElevatedButton.icon(
            onPressed: () {
              // TODO: Upload 액션
            },
            icon: const Icon(Icons.file_upload),
            label: const Text('Upload'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[300],
              foregroundColor: Colors.black87,
              padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
              textStyle: const TextStyle(fontSize: 16),
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Document Memo 섹션
        Container(
            padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 15.0),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(5.0),
            ),
            child: const Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Document Memo:', style: TextStyle(fontWeight: FontWeight.bold)),
                SizedBox(width: 8),
                Expanded(child: Text('Lunch with Clark@ HQ. Copy papers to give to Mary back at the office.')),
              ],
            )
        ),
        const SizedBox(height: 20),

        // Uploading result 섹션
        Container(
          padding: const EdgeInsets.symmetric(vertical: 15),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(5.0),
          ),
          child: const Text(
            'Uploading result',
            style: TextStyle(fontSize: 16),
          ),
        ),
        const SizedBox(height: 16),

        // Document Extraction Result 섹션
        Container(
          padding: const EdgeInsets.symmetric(vertical: 40),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(5.0),
          ),
          child: const Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                'Document',
                style: TextStyle(fontSize: 16),
              ),
              Text(
                'Extraction Result',
                style: TextStyle(fontSize: 16),
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // 하단 버튼 (Next Document, Exit) - New Document는 EmployeeContent에서 Saved/New 옆으로 옮겨짐
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4.0),
                child: ElevatedButton(
                  onPressed: (){
                    // TODO: Next Document 액션
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.grey[300],
                    foregroundColor: Colors.black87,
                  ),
                  child: const Text('Next Document'),
                ),
              ),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 4.0),
                child: ElevatedButton(
                  onPressed: (){
                    // TODO: Exit 액션
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.grey[300],
                    foregroundColor: Colors.black87,
                  ),
                  child: const Text('Exit'),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}